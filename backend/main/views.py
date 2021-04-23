import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
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
from littleutils import only
from sentry_sdk import capture_exception

from main.models import CodeEntry, ListEmail, User
from main.text import get_pages
from main.utils.django import PlaceHolderForm
from main.workers.master import run_code_entry

log = logging.getLogger(__name__)


def api_view(request, method_name):
    try:
        if method_name == "get_pages":
            method = get_pages
        elif method_name == "run_code":
            method = run_code_entry
        else:
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

    def ran_code_entry(self, entry, output):
        # TODO call in frontend, add passed and maybe other info
        if settings.SAVE_CODE_ENTRIES:
            CodeEntry.objects.create(**entry, output=output, user=self.user)

    def insert_birdseye_objects(self, functions, calls):
        top_old_function_id = only(
            f["id"] for f in functions if f["name"] == "<module>"
        )
        function_ids = [d.pop("id") for d in functions]
        functions = [eye.db.Function(**{**d, "hash": uuid4().hex}) for d in functions]
        with eye.db.session_scope() as session:
            for func in functions:
                session.add(func)
            session.commit()
            function_ids = {old: func.id for old, func in zip(function_ids, functions)}

            call_id = None
            for call in calls:
                old_function_id = call["function_id"]
                is_top_call = old_function_id == top_old_function_id
                call["function_id"] = function_ids[old_function_id]
                call["start_time"] = datetime.fromisoformat(call["start_time"])
                call = eye.db.Call(**call)
                session.add(call)
                if is_top_call:
                    call_id = call.id

        return f"/birdseye/call/{call_id}"

    def get_user(self):
        user = self.user
        if user.is_anonymous:
            return {}

        return dict(
            email=user.email,
            developerMode=user.developer_mode,
            pageSlug=user.page_slug,
            pagesProgress=user.json["pages_progress"],
        )

    def set_developer_mode(self, value: bool):
        self.user.developer_mode = value
        self.user.save()

    def set_pages_progress(self, pages_progress):
        self.user.json["pages_progress"] = pages_progress
        self.user.save()

    def set_page(self, page_slug):
        self.user.page_slug = page_slug
        self.user.save()

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
