import inspect
import json
import logging
from io import StringIO
from pathlib import Path
from random import shuffle
from tokenize import generate_tokens, Untokenizer
from typing import get_type_hints, Type
from uuid import uuid4

import requests
from birdseye import eye
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views import View
from django_user_agents.utils import get_user_agent
from littleutils import select_attrs
from markdown import markdown

from main.chapters.c03_variables import WritingPrograms
from main.chapters.c05_if_statements import UnderstandingProgramsWithSnoop
from main.chapters.c06_lists import UnderstandingProgramsWithPythonTutor
from main.models import CodeEntry
from main.text import Page, page_slugs_list, pages, ExerciseStep, clean_program
from main.worker import worker_connection

log = logging.getLogger(__name__)


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

        connection = worker_connection(self.user.id)
        connection.send(entry_dict)
        result = connection.recv()

        entry.output = result["output"]
        entry.save()

        if result["passed"]:
            self.move_step(1)

        output_parts = result["output_parts"]
        if not result["awaiting_input"]:
            output_parts.append(dict(text=">>> ", color="white"))

        birdseye_url = None
        birdseye_objects = result["birdseye_objects"]
        if birdseye_objects:
            functions = birdseye_objects["functions"]
            function_ids = [d.pop('id') for d in functions]
            functions = [eye.db.Function(**{**d, 'hash': uuid4().hex}) for d in functions]
            with eye.db.session_scope() as session:
                for func in functions:
                    session.add(func)
                session.commit()
                function_ids = {old: func.id for old, func in zip(function_ids, functions)}

                for call in birdseye_objects["calls"]:
                    call["function_id"] = function_ids[call["function_id"]]
                    call = eye.db.Call(**call)
                    session.add(call)
                    # TODO get correct call from top level
                    call_id = call.id

            birdseye_url = f"/birdseye/ipython_call/{call_id}"

        return dict(
            result=output_parts,
            message=markdown(result["message"]),
            state=self.current_state(),
            birdseye_url=birdseye_url,
        )

    def load_data(self):
        user = self.user
        if user.is_anonymous:
            return {}

        return dict(
            pages=[
                select_attrs(page, "title step_texts")
                for page in pages.values()
            ],
            state=self.current_state(),
            user=dict(
                email=user.email,
                developerMode=user.developer_mode,
            ),
        )

    def set_developer_mode(self, value: bool):
        self.user.developer_mode = value
        self.user.save()

    def current_state(self):
        return dict(
            **select_attrs(self, "hints step_index"),
            page_index=self.page.index,
            showEditor=self.page.index >= WritingPrograms.index,
            showSnoop=(self.page.index, self.step_index) >= (UnderstandingProgramsWithSnoop.index, 1),
            showPythonTutor=self.page.index >= UnderstandingProgramsWithPythonTutor.index,
            showBirdseye=True,
        )

    def move_step(self, delta: int):
        step_names = self.page.step_names
        new_index = self.step_index + delta
        if new_index >= len(step_names):
            self.next_page()
        elif new_index < 0:
            self.user.page_slug = page_slugs_list[self.page.index - 1]
            self.user.step_name = self.page.step_names[0]
        else:
            self.user.step_name = step_names[new_index]
        self.user.save()
        return self.load_data()

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

    def submit_feedback(self, title, description, state):
        """Create an issue on github.com using the given parameters."""

        body = f"""
**User Issue**
Email: {self.user.email}
User Agent: {get_user_agent(self.request)}

{description}

<details>

<summary>Redux state</summary>

<p>

```json
{json.dumps(state, indent=2)}
```

</p>
</details>
        """

        r = requests.post(
            'https://api.github.com/repos/alexmojaki/python_init/issues',
            json={'title': title,
                  'body': body,
                  'labels': ['user', 'bug']},
            headers=dict(
                Authorization='token ' + settings.GITHUB_TOKEN,
            ),
        )

        assert r.status_code == 201


class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, _request):
        try:
            with open(Path(__file__).parent / "../../frontend/build/index.html") as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app. Visit http://localhost:3000/ instead, or
                run `yarn run build` to test the production version.
                """,
                status=501,
            )
