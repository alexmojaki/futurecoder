import ast
import inspect
import logging
from collections import defaultdict

from core.exercises import assert_equal
from core.question_wizard import question_wizard_check
from core.runner.runner import EnhancedRunner
from core.text import pages
from core.utils import highlighted_markdown, catch_internal_errors

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

    def reset(self):
        super().reset()
        self.console.locals.update(assert_equal=assert_equal)

    def non_str_input(self):
        while True:
            pass  # wait for the interrupt


FullRunner.run = catch_internal_errors(FullRunner.run)


runner = FullRunner()


@catch_internal_errors
def check_entry(entry, input_callback, output_callback):
    result = dict(
        passed=False,
        messages=[],
        error=None,
    )
    try:
        if hasattr(entry, "to_py"):
            entry = entry.to_py()

        if not entry["input"].strip():
            return result

        result["output"] = ""

        def full_output_callback(data):
            parts = []
            for part in data["parts"]:
                typ = part["type"]
                if typ == "input":
                    continue
                result["output"] += part["text"]
                parts.append(part)
            data["parts"] = parts
            return output_callback(data)

        runner.set_combined_callbacks(output=full_output_callback, input=input_callback)
        runner.question_wizard = entry.get("question_wizard")
        runner.input_nodes = defaultdict(list)

        mode = entry["source"]
        if mode == "shell":
            mode = "single"
        result["birdseye_objects"] = runner.run(entry["input"], mode)

        if runner.question_wizard:
            result["messages"] = question_wizard_check(entry, result["output"], runner)
            return result

        page = pages[entry["page_slug"]]
        step_cls = page.get_step(entry["step_name"])

        step_result = False
        if entry["step_name"] != "final_text":
            step_instance = step_cls(
                entry["input"], result["output"], entry["source"], runner.console
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
    except KeyboardInterrupt:
        result["interrupted"] = True

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
