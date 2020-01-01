import inspect
import json
import linecache
import logging
import sys
import traceback
from code import InteractiveConsole
from io import StringIO
from typing import get_type_hints

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from markdown import markdown

from main.models import CodeEntry
from main.text import text_parts, steps, Steps

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
    def step(self):
        return self.user.step

    @property
    def progress(self):
        return steps.index(self.step)

    @property
    def hints(self):
        step = getattr(Steps, self.step)
        return step.hints

    def _run_code(self, code, runner, source):
        entry = CodeEntry.objects.create(
            input=code,
            source=source,
            user=self.user,
            step=self.step,
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

        try:
            f = getattr(Steps, self.step)
            method = getattr(Steps(entry, console, f.program), self.step)
            step_result = method()
        except SyntaxError:
            step_result = False

        if isinstance(step_result, dict):
            passed = step_result.get("passed", False)
            message = step_result.get("message", "")
        else:
            passed = step_result
            message = ""

        if passed:
            self.user.step = steps[self.progress + 1]
            self.user.save()

        def lines(text, color):
            return [
                dict(text=line or ' ', color=color)
                for line in text.splitlines()
            ]

        return dict(
            result=(lines(stdout, "white") +
                    lines(stderr, "red")),
            message=markdown(message),
            **self.current_state(),
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
            except SyntaxError:
                traceback.print_exc()
                return

            try:
                exec(code_obj, console.locals)
            except:
                traceback.print_exc()

        return self._run_code(code, runner, "editor")

    def load_data(self):
        return dict(
            parts=text_parts,
            **self.current_state(),
        )

    def current_state(self):
        return dict(
            progress=self.progress,
            hints=self.hints,
            showEditor=self.progress >= steps.index(Steps.editor_hello_world.__name__)
        )

    def move_step(self, delta: int):
        self.user.step = steps[self.progress + delta]
        self.user.save()
