import json
import logging
import traceback
from pathlib import Path
from time import sleep
from typing import get_type_hints

import requests
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ModelForm
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import CreateView
from django_user_agents.utils import get_user_agent
from sentry_sdk import capture_exception

from core.text import get_pages
from core.workers.master import run_code_entry
from main.models import ListEmail
from main.utils import PlaceHolderForm

log = logging.getLogger(__name__)


def api_view(request, method_name):
    try:
        if method_name == "get_pages":
            method = get_pages
        elif method_name == "run_code" and settings.DEBUG:
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

    def submit_feedback(self, title, description, state, email):
        """Create an issue on github.com using the given parameters."""

        body = f"""
**User Issue**
Email: {email or "(not given)"}
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


class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, _request):
        try:
            with open(Path(__file__).parent / "../../frontend/build/index.html") as f:
                response = HttpResponse(f.read())
                response["Cross-Origin-Opener-Policy"] = "same-origin"
                response["Cross-Origin-Embedder-Policy"] = "require-corp"
                return response
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
