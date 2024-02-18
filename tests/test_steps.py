import json
import os
import random
import re
from pathlib import Path


import core.utils
from core import translation as t
from core.checker import check_entry, FullRunner
from core.text import step_test_entries, get_predictions, load_chapters
from core.utils import highlighted_markdown, make_test_input_callback

core.utils.TESTING = True

random.seed(0)


def test_steps():
    lang = os.environ.get("FUTURECODER_LANGUAGE", "en")
    t.set_language(lang)
    list(load_chapters())
    runner = FullRunner(filename="/my_program.py")
    transcript = []
    for page, step, substep, entry in step_test_entries():
        program = substep.program
        is_message = substep != step

        output_parts = []
        input_callback = make_test_input_callback(step.stdin_input)

        def callback(event_type, data):
            if event_type == "input":
                return input_callback(data)
            elif event_type == "output":
                output_parts.extend(data["parts"])

        step.pre_run(runner)

        response = check_entry(entry, callback, runner)
        response["output_parts"] = output_parts
        normalise_response(response, is_message, substep)

        transcript_item = dict(
            program=program.splitlines(),
            page=page.title,
            step=step.__name__,
            response=response,
        )
        transcript.append(transcript_item)

        if step.get_solution and not is_message:
            get_solution = "".join(step.get_solution["tokens"])
            assert "def solution(" not in get_solution
            assert "returns_stdout" not in get_solution
            assert get_solution.strip() in program
            if get_solution == program:
                transcript_item["get_solution"] = "program"
            else:
                transcript_item["get_solution"] = get_solution.splitlines()
                if step.parsons_solution:
                    is_function = transcript_item["get_solution"][0].startswith(
                        "def "
                    )
                    assert len(step.get_solution["lines"]) >= 4 + is_function

        assert response["passed"] == (not is_message), step

    dirpath = Path(__file__).parent / "golden_files" / lang
    dirpath.mkdir(parents=True, exist_ok=True)
    path = dirpath / "test_transcript.json"
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
        if line["type"] == "traceback":
            line["text"] = line["text"].splitlines()

    response.pop("birdseye_objects", None)
    del response["error"]
    del response["output"]

    response["prediction"] = get_predictions(substep)
    if not response["prediction"]["choices"]:
        del response["prediction"]

    message_sections = response.pop("message_sections")
    if not is_message:
        assert not message_sections
    else:
        section = message_sections[0]
        assert set(section.keys()) == {"type", "messages"}
        assert section["type"] == "messages"
        assert len(section["messages"]) == 1
        message = response["message"] = section["messages"][0]
        expected = highlighted_markdown(substep.text)
        if getattr(substep, "expected_exact_match", True):
            assert expected == message
        else:
            assert expected in message
