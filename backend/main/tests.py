import json
import os
from pathlib import Path

from django.test import TestCase, Client

from main.chapters.c05_if_statements import UnderstandingProgramsWithSnoop
from main.text import pages
from main import worker

client = Client()
worker.TESTING = True

def api(method, **kwargs):
    response = client.post(f"/api/{method}/", data=kwargs, content_type="application/json")
    return response.json()


class StepsTestCase(TestCase):
    def setUp(self):
        from main.models import User

        self.user = User.objects.create_user("admin", "admin@example.com", "pass")
        client.post("/accounts/login/", dict(username="admin", password="pass"))

    def test_steps(self):
        data = api("load_data")
        state = data["state"]
        transcript = []
        for page_index, page in enumerate(pages.values()):
            for step_index, step_name in enumerate(page.step_names[:-1]):
                assert page_index == state["page_index"]
                assert step_index == state["step_index"]
                step = getattr(page, step_name)

                for substep in [*step.messages, step]:
                    program = substep.program
                    if "\n" in program:
                        if step == UnderstandingProgramsWithSnoop.print_tail_snoop:
                            code_source = "snoop"
                        else:
                            code_source = "editor"
                    else:
                        code_source = "shell"
                    response = api("run_code", code=program, source=code_source)
                    state = response["state"]
                    transcript.append(dict(
                        program=program.splitlines(),
                        page=page.title,
                        step=step_name,
                        response=response,
                    ))
                    is_message = substep in step.messages
                    if is_message:
                        self.assertEqual(response["message"], substep.text)

                    self.assertEqual(step_index + (not is_message), state["step_index"], transcript[-1])

            if page_index < len(pages) - 1:
                state = api("next_page")
        path = Path(__file__).parent / "test_transcript.json"
        if os.environ.get("FIX_TESTS", 0):
            dump = json.dumps(transcript, indent=4, sort_keys=True)
            path.write_text(dump)
        else:
            self.assertEqual(transcript, json.loads(path.read_text()))
