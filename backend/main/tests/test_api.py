import json
import os
import re
from pathlib import Path

import pytest
from littleutils import only

from main.text import pages
from main.workers import master
from main.workers.worker import run_code

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
                is_message = substep in step.messages

                if "\n" in program:
                    code_source = step.expected_code_source or "editor"
                else:
                    code_source = "shell"

                entry = dict(
                    input=program,
                    source=code_source,
                    page_slug=page.slug,
                    step_name=step_name,
                )
                response = api("run_code", entry=entry)

                normalise_response(response, is_message, substep)

                raw_response = {}

                def result_callback(r):
                    nonlocal raw_response
                    raw_response = r

                run_code(entry, input_callback=None, result_callback=result_callback)
                normalise_response(raw_response, is_message, substep)

                assert response == raw_response

                transcript_item = dict(
                    program=program.splitlines(),
                    page=page.title,
                    step=step_name,
                    response=response,
                )
                transcript.append(transcript_item)

                if step.get_solution and not is_message:
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

    path = Path(__file__).parent / "test_transcript.json"
    if os.environ.get("FIX_TESTS", 0):
        dump = json.dumps(transcript, indent=4, sort_keys=True)
        path.write_text(dump)
    else:
        assert transcript == json.loads(path.read_text())


def normalise_output(s):
    s = re.sub(r" at 0x\w+>", " at 0xABC>", s)
    return s


def normalise_response(response, is_message, substep):
    response["result"] = response.pop("output_parts")
    for line in response["result"]:
        line["text"] = normalise_output(line["text"])
    del response["birdseye_objects"]
    del response["awaiting_input"]
    del response["error"]
    del response["output"]
    if not response["prediction"]["choices"]:
        del response["prediction"]

    if is_message:
        response["message"] = only(response.pop("messages"))
        assert response["message"] == substep.text
    else:
        assert response.pop("messages") == []
        response["message"] = ""
