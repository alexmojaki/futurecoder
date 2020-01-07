import inspect
import json
import linecache
import logging
import sys
from code import InteractiveConsole
from io import StringIO
from typing import get_type_hints, Type

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from littleutils import select_attrs
from markdown import markdown

from main.chapters.variables import WritingPrograms
from main.models import CodeEntry
from main.text import Page, page_slugs_list, pages
from main.utils import format_exception_string

log = logging.getLogger(__name__)


class IFrameView(LoginRequiredMixin, View):
    iframe_pattern = ""

    def get(self, request, *args, **kwargs):
        return render(
            request,
            "iframe_view.html",
            dict(iframe_url=self.iframe_pattern.format(*args, **kwargs)),
        )


def api_view(request, method_name):
    body = request.body
    try:
        method = getattr(API(request), method_name)
    except AttributeError:
        log.error('Unknown method %s, body = %s', method_name, body)
        return HttpResponseBadRequest()
    try:
        body = body.decode('utf8')
    except UnicodeDecodeError:
        log.exception('Failed to decode %s', body)
        return HttpResponseBadRequest()
    log.info('API request: method = %s, body = %s', method_name, body)
    try:
        args = json.loads(body)
    except ValueError as e:
        log.error('JSON decode error: %s', e)
        return HttpResponseBadRequest()
    signature = inspect.signature(method)
    try:
        signature.bind(**args)
    except TypeError as e:
        log.error(e)
        return HttpResponseBadRequest()
    for arg_name, hint in get_type_hints(method).items():
        if arg_name == 'return':
            continue
        arg = args[arg_name]
        if not isinstance(arg, hint):
            log.warning(
                'Incorrect type for argument %s = %r of method %s: found %s, expected %s',
                arg_name, arg, method_name, arg.__class__.__name__, hint.__name__)
    result = method(**args)
    if not isinstance(result, dict):
        result = {'result': result}
    return JsonResponse(result, json_dumps_params=dict(indent=4, sort_keys=True))


console = InteractiveConsole()


class API:
    def __init__(self, request):
        self.request = request

    @property
    def user(self):
        return self.request.user

    @property
    def page(self) -> Type[Page]:
        return self.user.page

    @property
    def step_index(self):
        return self.page.step_names.index(self.user.step_name)

    @property
    def hints(self):
        return getattr(self.user.step, "hints", ())

    def _run_code(self, code, runner, source):
        entry = CodeEntry.objects.create(
            input=code,
            source=source,
            user=self.user,
            page_slug=self.user.page_slug,
            step_name=self.user.step_name,
        )

        stdout = StringIO()
        stderr = StringIO()
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        try:
            sys.stdout = stdout
            sys.stderr = stderr
            runner()
        finally:
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
        stdout = stdout.getvalue().rstrip('\n')
        stderr = stderr.getvalue().rstrip('\n')
        entry.output = stdout + "\n" + stderr
        entry.save()

        message = ""

        if self.user.step_name != "final_text":
            step_result = self.page.check_step(self.user.step_name, entry, console)
            if isinstance(step_result, dict):
                passed = step_result.get("passed", False)
                message = step_result.get("message", "")
            else:
                passed = step_result

            if passed:
                self.move_step(1)

        def lines(text, color):
            return [
                dict(text=line or ' ', color=color)
                for line in text.splitlines()
            ]

        return dict(
            result=(lines(stdout, "white") +
                    lines(stderr, "red")),
            message=markdown(message),
            state=self.current_state(),
        )

    def shell_line(self, line):
        return self._run_code(line, lambda: console.push(line), "shell")

    def run_program(self, code):
        def runner():
            console.locals = {}
            filename = "my_program.py"
            linecache.cache[filename] = (
                len(code),
                None,
                [line + '\n' for line in code.splitlines()],
                filename,
            )
            try:
                code_obj = compile(code, filename, "exec")
            except SyntaxError as e:
                print(format_exception_string(e), file=sys.stderr)
                return

            try:
                exec(code_obj, console.locals)
            except Exception as e:
                print(format_exception_string(e), file=sys.stderr)

        return self._run_code(code, runner, "editor")

    def load_data(self):
        return dict(
            pages=[
                select_attrs(page, "title step_texts")
                for page in pages.values()
            ],
            state=self.current_state(),
        )

    def current_state(self):
        return dict(
            **select_attrs(self, "hints step_index"),
            page_index=self.page.index,
            showEditor=self.page.index >= WritingPrograms.index,
        )

    def move_step(self, delta: int):
        self.user.step_name = self.page.step_names[self.step_index + delta]
        self.user.save()

    def next_page(self):
        self.user.page_slug = page_slugs_list[self.page.index + 1]
        self.user.step_name = self.page.step_names[0]
        self.user.save()
        return self.current_state()
