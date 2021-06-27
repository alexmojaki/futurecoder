import builtins
import linecache
import logging
import sys
from code import InteractiveConsole
from contextlib import redirect_stdout, redirect_stderr

import stack_data

from core.exercises import assert_equal
from core.text import pages
from core.utils import highlighted_markdown, friendly
from core.workers.tracebacks import TracebackSerializer, print_friendly_syntax_error
from core.workers.utils import internal_error_result, make_result, output_buffer

log = logging.getLogger(__name__)

console = InteractiveConsole()
console.locals = {"assert_equal": assert_equal}


def execute(code_obj):
    try:
        exec(code_obj, console.locals)
    except (Exception, KeyboardInterrupt) as e:
        return TracebackSerializer().format_exception(e)


def runner(code_source, code):
    if code_source == "shell":
        mode = "single"
        code += "\n"  # Allow compiling single-line compound statements
    else:
        mode = "exec"
        console.locals = {"assert_equal": assert_equal}

    filename = "my_program.py"
    linecache.cache[filename] = (
        len(code),
        None,
        [line + '\n' for line in code.splitlines()],
        filename,
    )

    stack_data.Source._class_local('__source_cache', {}).pop(filename, None)

    friendly.source_cache.cache.add(filename, code)

    try:
        code_obj = compile(code, filename, mode)
    except SyntaxError as e:
        print_friendly_syntax_error(e)
        return {}

    birdseye_objects = None

    if code_source == "snoop":
        from core.workers.snoop import exec_snoop
        traceback_info = exec_snoop(filename, code, code_obj)
    elif code_source == "birdseye":
        from core.workers.birdseye import exec_birdseye
        traceback_info, birdseye_objects = exec_birdseye(filename, code)
    else:
        traceback_info = execute(code_obj)

    if traceback_info:
        exception = traceback_info[-1]["exception"]
        traceback_info = dict(
            isTraceback=True,
            codeSource=code_source,
            tracebacks=traceback_info,
            text=f"{exception['type']}: {exception['message']}",
            color="red",
        )
        output_buffer.parts.append(traceback_info)

    return birdseye_objects


def run_code_catch_internal_errors(entry, input_callback, result_callback):
    try:
        run_code(entry, input_callback, result_callback)
    except Exception:
        result_callback(internal_error_result())


def run_code(entry, input_callback, result_callback):
    if hasattr(entry, "to_py"):
        entry = entry.to_py()

    patch_stdin(input_callback, result_callback)

    with redirect_stdout(output_buffer.stdout), redirect_stderr(output_buffer.stderr):
        birdseye_objects = runner(entry["source"], entry["input"])

    output = output_buffer.string()

    page = pages[entry["page_slug"]]
    step_cls = page.get_step(entry["step_name"])
    step_instance = step_cls(entry["input"], output, entry["source"], console)

    step_result = False
    if entry["step_name"] != "final_text":
        try:
            step_result = step_instance.check_with_messages()
        except SyntaxError:
            pass

    messages = []
    passed = step_result
    if isinstance(step_result, dict):
        passed = step_result.get("passed", False)
        messages = step_result.get("messages", [])
        if "message" in step_result:
            messages.append(step_result["message"])

    messages = [highlighted_markdown(message) for message in messages]

    if passed:
        prediction = dict(
            choices=getattr(step_cls, "predicted_output_choices", None),
            answer=getattr(step_cls, "correct_output", None),
        )
    else:
        prediction = None

    result_callback(
        make_result(
            passed=passed,
            messages=messages,
            output=output,
            birdseye_objects=birdseye_objects,
            prediction=prediction,
        )
    )


def patch_stdin(input_callback, result_callback):
    def readline(*_):
        result_callback(make_result(awaiting_input=True))
        result = input_callback()
        if not isinstance(result, str):
            while True:
                pass  # wait for the interrupt
        return result

    sys.stdin.readline = readline

    def patched_input(prompt=""):
        print(prompt, end="")
        return sys.stdin.readline().rstrip("\n")

    builtins.input = patched_input
