import logging

from core.exercises import assert_equal
from core.runner.friendly_traceback import friendly_syntax_error
from core.runner.runner import EnhancedRunner
from core.text import pages
from core.utils import highlighted_markdown
from core.workers.utils import catch_internal_errors

log = logging.getLogger(__name__)


def make_runner():
    # TODO move into class
    def format_syntax_error(e):
        return friendly_syntax_error(e, result.filename)

    result = EnhancedRunner(
        callback=None,
        extra_locals={"assert_equal": assert_equal},
        format_syntax_error=format_syntax_error,
    )
    result.run = catch_internal_errors(result.run)

    return result

runner = make_runner()


@catch_internal_errors
def check_entry(entry, input_callback, output_callback):
    if hasattr(entry, "to_py"):
        entry = entry.to_py()

    result = dict(
        passed=False,
        messages=[],
        error=None,
    )

    if not entry["input"].strip():
        return result

    output = ""
    def full_callback(event_type, data):
        nonlocal output
        if event_type == "output":
            parts = []
            for part in data["parts"]:
                typ = part.pop("type")

                if typ in ("stderr", "traceback", "syntax_error"):
                    color = "red"
                else:
                    color = "white"

                part["color"] = color
                if typ == "traceback":
                    part["isTraceback"] = True
                    part["tracebacks"] = part.pop("data")
                    part["codeSource"] = entry["source"]

                if typ == "input":
                    continue
                output += part["text"]
                parts.append(part)
            data["parts"] = parts
            return output_callback(data)
        else:
            assert event_type == "input"
            return input_callback()

    runner._callback = full_callback
    result.update(runner.run(entry["source"], entry["input"]))

    if result.get("interrupted"):
        return result

    page = pages[entry["page_slug"]]
    step_cls = page.get_step(entry["step_name"])

    step_result = False
    if entry["step_name"] != "final_text":
        step_instance = step_cls(
            entry["input"], output, entry["source"], runner.console
        )
        try:
            step_result = step_instance.check_with_messages()
        except SyntaxError:
            pass

    step_result = normalise_step_result(step_result)
    result.update(
        passed=step_result["passed"],
        messages=[highlighted_markdown(message) for message in step_result["messages"]],
    )

    return result


def normalise_step_result(step_result):
    if not isinstance(step_result, dict):
        assert isinstance(step_result, bool)
        step_result = dict(passed=step_result, messages=[])

    step_result.setdefault("passed", False)

    messages = step_result.setdefault("messages", [])
    if "message" in step_result:
        messages.append(step_result.pop("message"))

    return step_result

# TODO
# question_wizard = entry.get("question_wizard")
#
# patch_stdin(input_callback, result_callback, question_wizard)
# input_nodes = defaultdict(list)

# input_nodes.clear()

# try:
#     assert question_wizard
#     frame = inspect.currentframe().f_back
#     assert frame.f_code.co_filename == "my_program.py"
#     ex = stack_data.Source.executing(frame)
#     node = ex.node
#     assert isinstance(node, ast.Call)
#     input_nodes[node].append((result, ex))
# except Exception:
#     pass

# if question_wizard:
#     messages = question_wizard_check(entry, output)
#     result_callback(
#         make_result(
#             messages=messages,
#             output=output,
#             **run_results,
#         )
#     )
#     return
