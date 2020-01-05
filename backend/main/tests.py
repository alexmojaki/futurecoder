from django.test import TestCase, Client

from main.models import User
from main.text import pages

client = Client()


def api(method, **kwargs):
    response = client.post(f"/api/{method}/", data=kwargs, content_type="application/json")
    return response.json()


class StepsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("admin", "admin@example.com", "pass")
        client.post("/accounts/login/", dict(username="admin", password="pass"))

    def test_steps(self):
        data = api("load_data")
        state = data["state"]
        for page_index, page in enumerate(pages.values()):
            for step_index, step_name in enumerate(page.step_names[:-1]):
                assert page_index == state["page_index"]
                assert step_index == state["step_index"]
                step = getattr(page, step_name)
                program = step.program
                if "\n" in program:
                    response = api("run_program", code=program)
                else:
                    response = api("shell_line", line=program)
                state = response["state"]
            if page_index < len(pages) - 1:
                state = api("next_page")
