import json
import os
import re
from pathlib import Path

from django.test import Client, TestCase

from main.chapters.c05_if_statements import UnderstandingProgramsWithSnoop
from main.chapters.c06_lists import UnderstandingProgramsWithPythonTutor
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
                        if step == UnderstandingProgramsWithSnoop.print_tail_snoop:
                            code_source = "snoop"
                        elif step == UnderstandingProgramsWithPythonTutor.run_with_python_tutor:
                            code_source = "pythontutor"
                        else:
                            code_source = "editor"
                    else:
                        code_source = "shell"
                    response = api(
                        "run_code",
                        code=program,
                        source=code_source,
                        page_index=page_index,
                        step_index=step_index,
                    )
                    state = response.pop("state")
                    for line in response["result"]:
                        line["text"] = normalise_output(line["text"])
                    transcript.append(dict(
                        program=program.splitlines(),
                        page=page.title,
                        step=step_name,
                        response=response,
                    ))
                    is_message = substep in step.messages
                    if is_message:
                        self.assertEqual(response["message"], substep.text)

                    self.assertEqual(
                        response["passed"],
                        not is_message,
                        transcript[-1],
                    )

                    self.assertEqual(
                        step_index + response["passed"],
                        state["pages_progress"][page_index],
                        transcript[-1],
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
