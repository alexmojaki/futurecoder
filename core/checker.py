import ast
import inspect
import logging
from collections import defaultdict

from core.exercises import assert_equal
from core.runner.runner import EnhancedRunner
from core.text import pages
from core.utils import highlighted_markdown
from core.question_wizard import question_wizard_check
from core.utils import catch_internal_errors

log = logging.getLogger(__name__)


class FullRunner(EnhancedRunner):
    question_wizard = False
    input_nodes = {}

    def input(self, prompt=""):
        result = super().input(prompt)
        try:
            assert self.question_wizard
            frame = inspect.currentframe().f_back
            assert frame.f_code.co_filename == self.filename
            import stack_data
            ex = stack_data.Source.executing(frame)
            node = ex.node
            assert isinstance(node, ast.Call)
            self.input_nodes[node].append((result, ex))
        except Exception:
            pass
        return result


FullRunner.run = catch_internal_errors(FullRunner.run)


runner = FullRunner(
    extra_locals={"assert_equal": assert_equal},
)


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
                typ = part["type"]
                if typ == "traceback":
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
    runner.question_wizard = entry.get("question_wizard")
    runner.input_nodes = defaultdict(list)

    result.update(runner.run(entry["source"], entry["input"]))

    if result.get("interrupted"):
        return result

    if runner.question_wizard:
        result["messages"] = question_wizard_check(entry, output, runner)
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
