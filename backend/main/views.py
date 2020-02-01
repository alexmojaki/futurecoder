import inspect
import json
import logging
from io import StringIO
from random import shuffle
from tokenize import generate_tokens, Untokenizer
from typing import get_type_hints, Type

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from littleutils import select_attrs
from markdown import markdown

from main.chapters.c03_variables import WritingPrograms
from main.chapters.c05_if_statements import UnderstandingProgramsWithSnoop
from main.chapters.c06_lists import UnderstandingProgramsWithPythonTutor
from main.models import CodeEntry
from main.text import Page, page_slugs_list, pages, ExerciseStep, clean_program
from main.worker import worker_connection

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

    def run_code(self, code, source):
        entry_dict = dict(
            input=code,
            source=source,
            page_slug=self.user.page_slug,
            step_name=self.user.step_name,
        )

        entry = CodeEntry.objects.create(
            **entry_dict,
            user=self.user,
        )

        connection = worker_connection()
        connection.send(entry_dict)
        result = connection.recv()

        entry.output = result["output"]
        entry.save()

        if result["passed"]:
            self.move_step(1)

        return dict(
            result=result["lines"],
            message=markdown(result["message"]),
            state=self.current_state(),
        )

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
            showSnoop=(self.page.index, self.step_index) >= (UnderstandingProgramsWithSnoop.index, 1),
            showPythonTutor=self.page.index >= UnderstandingProgramsWithPythonTutor.index,
        )

    def move_step(self, delta: int):
        self.user.step_name = self.page.step_names[self.step_index + delta]
        self.user.save()

    def next_page(self):
        self.user.page_slug = page_slugs_list[self.page.index + 1]
        self.user.step_name = self.page.step_names[0]
        self.user.save()
        return self.current_state()

    def get_solution(self):
        step = getattr(self.page, self.user.step_name)
        if issubclass(step, ExerciseStep):
            program = clean_program(step.solution)
        else:
            program = step.program

        untokenizer = Untokenizer()
        tokens = generate_tokens(StringIO(program).readline)
        untokenizer.untokenize(tokens)
        tokens = untokenizer.tokens

        masked_indices = []
        mask = [False] * len(tokens)
        for i, token in enumerate(tokens):
            if not token.isspace():
                masked_indices.append(i)
                mask[i] = True
        shuffle(masked_indices)

        return dict(
            tokens=tokens,
            maskedIndices=masked_indices,
            mask=mask,
        )
