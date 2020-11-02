import json
import os
import re
from pathlib import Path

import pytest
from littleutils import only

from main.text import pages
from main.workers import master

master.TESTING = True


@pytest.fixture
def api(admin_client):
    def post(method, **kwargs):
        response = admin_client.post(
            f"/api/{method}/", data=kwargs, content_type="application/json"
        )
        return response.json()

    return post


def test_steps(api):
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

                assert "state" in response
                state = response.pop("state")
                for line in response["result"]:
                    line["text"] = normalise_output(line["text"])
                del response["birdseye_url"]
                if not response["prediction"]["choices"]:
                    del response["prediction"]

                transcript_item = dict(
                    program=program.splitlines(),
                    page=page.title,
                    step=step_name,
                    response=response,
                )
                transcript.append(transcript_item)
                is_message = substep in step.messages

                if is_message:
                    response["message"] = only(response.pop("messages"))
                    assert response["message"] == substep.text
                else:
                    assert response.pop("messages") == []
                    response["message"] = ""

                    if step.get_solution:
                        get_solution = "".join(step.get_solution["tokens"])
                        assert "def solution(" not in get_solution
                        assert "returns_stdout" not in get_solution
                        assert get_solution.strip() in program
                        transcript_item["get_solution"] = get_solution.splitlines()
                        if step.parsons_solution:
                            is_function = transcript_item["get_solution"][0].startswith(
                                "def "
                            )
                            assert len(step.get_solution["lines"]) >= 4 + is_function

                assert response["passed"] == (not is_message)
                assert step_index + response["passed"] == state["pages_progress"][page_index]

    path = Path(__file__).parent / "test_transcript.json"
    if os.environ.get("FIX_TESTS", 0):
        dump = json.dumps(transcript, indent=4, sort_keys=True)
        path.write_text(dump)
    else:
        assert transcript == json.loads(path.read_text())


def normalise_output(s):
    s = re.sub(r" at 0x\w+>", " at 0xABC>", s)
    return s
