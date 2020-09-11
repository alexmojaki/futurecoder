import json
import os
import re
from pathlib import Path

from django.test import Client, TestCase

from main.text import pages
from main.workers import master

client = Client()
master.TESTING = True


def api(method, **kwargs):
    response = client.post(f"/api/{method}/", data=kwargs, content_type="application/json")
    return response.json()


class StepsTestCase(TestCase):
    def setUp(self):
        from main.models import User

        self.user = User.objects.create_user("admin", "admin@example.com", "pass")
        client.post("/accounts/login/", dict(login="admin@example.com", password="pass"))

    def test_steps(self):
        transcript = []
        for page_index, page in enumerate(pages.values()):
            for step_index, step_name in enumerate(page.step_names[:-1]):
                step = getattr(page, step_name)

                for substep in [*step.messages, step]:
                    program = substep.program
                    if "\n" in program:
                        code_source = step.expected_code_source or "editor"
                    else:
                        code_source = "shell"
                    response = api(
                        "run_code",
                        code=program,
                        source=code_source,
                        page_index=page_index,
                        step_index=step_index,
                    )
                    if "state" not in response:
                        self.fail(response)
                    state = response.pop("state")
                    for line in response["result"]:
                        line["text"] = normalise_output(line["text"])
                    del response["birdseye_url"]
                    transcript_item = dict(
                        program=program.splitlines(),
                        page=page.title,
                        step=step_name,
                        response=response,
                    )
                    transcript.append(transcript_item)
                    is_message = substep in step.messages
                    if is_message:
                        self.assertEqual(response["message"], substep.text, transcript_item)
                    elif step.hints:
                        solution_response = api(
                            "get_solution",
                            page_index=page_index,
                            step_index=step_index,
                        )
                        get_solution = "".join(solution_response["tokens"])
                        assert "def solution(" not in get_solution
                        assert "returns_stdout" not in get_solution
                        assert get_solution.strip() in program
                        transcript_item["get_solution"] = get_solution.splitlines()
                    self.assertEqual(
                        response["passed"],
                        not is_message,
                        transcript_item,
                    )

                    self.assertEqual(
                        step_index + response["passed"],
                        state["pages_progress"][page_index],
                        transcript_item,
                    )
        path = Path(__file__).parent / "test_transcript.json"
        if os.environ.get("FIX_TESTS", 0):
            dump = json.dumps(transcript, indent=4, sort_keys=True)
            path.write_text(dump)
        else:
            self.assertEqual(transcript, json.loads(path.read_text()))


def normalise_output(s):
    s = re.sub(r" at 0x\w+>", " at 0xABC>", s)
    return s
