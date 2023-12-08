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
        """
        Tracks input nodes during question wizard execution

        Args:
            - prompt: prompts to display

        Returns:
            - user input.
        """
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
        if self.question_wizard:
            # Delay importing stack_data in general.
            # Clear the source cache before running in the question wizard
            # for the input() magic to work properly.
            import stack_data
            stack_data.Source._class_local("__source_cache", {}).pop(self.filename, None)

        self.console.locals.update(assert_equal=assert_equal)


default_runner = FullRunner(filename="/my_program.py")


@catch_internal_errors
def check_entry(entry, callback, runner=default_runner):
    result = dict(
        passed=False,
        error=None,
        message_sections=[],
    )
    try:
        if hasattr(entry, "to_py"):
            entry = entry.to_py()

        if not entry["input"].strip():
            return result

        result["output"] = ""

        def wrapped_callback(event_type, data):
            if event_type == "output":
                parts = []
                for part in data["parts"]:
                    typ = part["type"]
                    if typ == "input":
                        continue
                    result["output"] += part["text"]
                    parts.append(part)
                data["parts"] = parts
            return callback(event_type, data)

        runner.set_callback(wrapped_callback)
        runner.question_wizard = entry.get("question_wizard")
        runner.input_nodes = defaultdict(list)

        mode = entry["source"]
        if mode == "shell":
            mode = "single"

        runner.birdseye_objects = None
        try:
            runner.run(entry["input"], mode)
        except SyntaxError as syntax_error:
            print(f"SyntaxError: {syntax_error}")
            raise syntax_error
        finally:
            result["birdseye_objects"] = runner.birdseye_objects

        if runner.question_wizard:
            (
                result["messages"],
                result["question_wizard_status"],
            ) = question_wizard_check(entry, result["output"], runner)
            return result

        page = pages[entry["page_slug"]]
        step_cls = page.get_step(entry["step_name"])

        step_result = dict(passed=False, messages=[])
        if entry["step_name"] != "final_text":
            step_instance = step_cls(
                entry["input"], result["output"], entry["source"], runner.console
            )
            try:
                step_result = step_instance.check_with_messages()
            except SyntaxError as syntax_error:
                print(f"SyntaxError: {syntax_error}")
                raise syntax_error

        result["passed"] = step_result["passed"]
        if not result["passed"]:
            if "message" in step_result:
                step_result["messages"].insert(0, step_result.pop("message"))

            result["message_sections"] = [
                dict(
                    type=typ,
                    messages=[highlighted_markdown(message) for message in step_result.get(typ, [])],
                )
                for typ in ["messages", "passed_tests", "lint"]
            ]
    except KeyboardInterrupt:
        result["interrupted"] = True

    return result
