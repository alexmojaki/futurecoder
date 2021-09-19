import json
import os
import re
from pathlib import Path

from littleutils import only

from core.text import pages
from core.utils import highlighted_markdown, make_test_input_callback
from core.workers.worker import check_entry


def test_steps():
    transcript = []
    for page_index, page in enumerate(pages.values()):
        for step_index, step_name in enumerate(page.step_names[:-1]):
            step = page.get_step(step_name)

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
                response = {}

                def result_callback(r):
                    nonlocal response
                    response = r

                check_entry(
                    entry,
                    input_callback=make_test_input_callback(step.stdin_input),
                    result_callback=result_callback,
                )
                normalise_response(response, is_message, substep)

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
        if line.get("isTraceback"):
            line["text"] = line["text"].splitlines()

    del response["birdseye_objects"]
    del response["awaiting_input"]
    del response["error"]
    del response["output"]
    if not response["prediction"]["choices"]:
        del response["prediction"]

    if is_message:
        response["message"] = only(response.pop("messages"))
        assert response["message"] == highlighted_markdown(substep.text)
    else:
        assert response.pop("messages") == []
        response["message"] = ""
