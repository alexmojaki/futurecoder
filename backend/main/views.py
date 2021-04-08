import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from threading import Thread
from time import sleep
from typing import get_type_hints
from uuid import uuid4

import birdseye.server
import requests
from birdseye import eye
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ModelForm
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import CreateView
from django_user_agents.utils import get_user_agent
from littleutils import select_attrs, only
from sentry_sdk import capture_exception

from main.models import CodeEntry, ListEmail, User
from main.text import page_slugs_list, pages
from main.utils import highlighted_markdown
from main.utils.django import PlaceHolderForm
from main.workers.master import worker_result

log = logging.getLogger(__name__)


def api_view(request, method_name):
    try:
        method = getattr(API(request), method_name)
        body = request.body
        body = body.decode('utf8')
        args = json.loads(body)
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
    except Exception:
        capture_exception()
        result = dict(
            error=dict(
                traceback=traceback.format_exc(),
            )
        )
    return JsonResponse(result)


class API:
    def __init__(self, request):
        self.request = request

    @property
    def user(self) -> User:
        return self.request.user

    def run_code(self, code, source, page_index, step_index):
        page_slug = page_slugs_list[page_index]
        page = pages[page_slug]
        step_name = pages[page_slug].step_names[step_index]
        step = getattr(page, step_name)
        entry_dict = dict(
            input=code,
            source=source,
            page_slug=page_slug,
            step_name=step_name,
            user_id=self.user.id,
        )

        entry = None
        if settings.SAVE_CODE_ENTRIES:
            entry = CodeEntry.objects.create(**entry_dict)

        result = worker_result(entry_dict)

        if settings.SAVE_CODE_ENTRIES:
            entry.output = result["output"]
            entry.save()

        if result["error"]:
            return dict(error=result["error"])

        if passed := result["passed"]:
            self.move_step(page_index, step_index + 1)

        output_parts = result["output_parts"]
        if not result["awaiting_input"]:
            output_parts.append(dict(text=">>> ", color="white"))

        birdseye_url = None
        birdseye_objects = result["birdseye_objects"]
        if birdseye_objects:
            functions = birdseye_objects["functions"]
            top_old_function_id = only(
                f["id"]
                for f in functions
                if f["name"] == "<module>"
            )
            function_ids = [d.pop('id') for d in functions]
            functions = [eye.db.Function(**{**d, 'hash': uuid4().hex}) for d in functions]
            with eye.db.session_scope() as session:
                for func in functions:
                    session.add(func)
                session.commit()
                function_ids = {old: func.id for old, func in zip(function_ids, functions)}

                call_id = None
                for call in birdseye_objects["calls"]:
                    old_function_id = call["function_id"]
                    is_top_call = old_function_id == top_old_function_id
                    call["function_id"] = function_ids[old_function_id]
                    call["start_time"] = datetime.fromisoformat(call["start_time"])
                    call = eye.db.Call(**call)
                    session.add(call)
                    if is_top_call:
                        call_id = call.id

            birdseye_url = f"/birdseye/call/{call_id}"

        return dict(
            result=output_parts,
            messages=list(map(highlighted_markdown, result["messages"])),
            state=self.current_state(),
            birdseye_url=birdseye_url,
            passed=passed,
            prediction=dict(
                choices=getattr(step, "predicted_output_choices", None),
                answer=getattr(step, "correct_output", None),
            ) if passed else dict(choices=None, answer=None),
        )

    def load_data(self):
        user = self.user
        if user.is_anonymous:
            return {}

        Thread(target=self.warmup_user_process).start()

        return dict(
            pages=[
                dict(**select_attrs(page, "slug title index"), steps=page.step_dicts)
                for page in pages.values()
            ],
            state=self.current_state(),
            user=dict(
                email=user.email,
                developerMode=user.developer_mode,
            ),
            page_index=pages[self.user.page_slug].index,
        )

    def warmup_user_process(self):
        page_slug = page_slugs_list[0]
        step_name = pages[page_slug].step_names[0]
        entry_dict = dict(
            input="'dummy startup code'",
            source="shell",
            page_slug=page_slug,
            step_name=step_name,
            user_id=self.user.id,
        )
        worker_result(entry_dict)

    def set_developer_mode(self, value: bool):
        self.user.developer_mode = value
        self.user.save()

    def current_state(self):
        pages_progress = self.user.pages_progress
        return dict(
            pages_progress=[
                page.step_names.index(pages_progress[page_slug]["step_name"])
                for page_slug, page in pages.items()
            ],
        )

    def move_step(self, page_index, step_index: int):
        page_slug = page_slugs_list[page_index]
        step_names = pages[page_slug].step_names
        if 0 <= step_index < len(step_names):
            new_step_name = step_names[step_index]
            self.user.pages_progress[page_slug]["step_name"] = new_step_name
            self.user.save()

        return self.current_state()

    def set_page(self, index):
        self.user.page_slug = page_slugs_list[index]
        self.user.save()

    def get_solution(self, page_index, step_index: int):
        # TODO deprecated
        page = pages[page_slugs_list[page_index]]
        step = getattr(page, page.step_names[step_index])
        return step.get_solution

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
            'https://api.github.com/repos/alexmojaki/futurecoder/issues',
            json={'title': title,
                  'body': body,
                  'labels': ['user', 'bug']},
            headers=dict(
                Authorization='token ' + settings.GITHUB_TOKEN,
            ),
        )

        assert r.status_code == 201


class FrontendAppView(LoginRequiredMixin, View):
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


class HomePageView(SuccessMessageMixin, CreateView):
    template_name = "home.html"
    success_message = "Success! We will email %(email)s when the time is right..."

    def get_success_url(self):
        return self.request.path_info

    class form_class(ModelForm, PlaceHolderForm):
        helper_attrs = dict(form_tag=False)

        class Meta:
            model = ListEmail
            fields = ["email"]


def timeout_view(request):
    sleep(35)


def fix_birdseye_server():
    views = birdseye.server.app.view_functions
    birdseye.server.app.view_functions = {
        "call_view": views["ipython_call_view"],
        "static": views["static"],
    }


fix_birdseye_server()
