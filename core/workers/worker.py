import builtins
import importlib
import linecache
import logging
import sys
from code import InteractiveConsole
from contextlib import redirect_stdout, redirect_stderr

import friendly_traceback.source_cache
import stack_data

from core.exercises import assert_equal
from core.text import pages
from core.utils import highlighted_markdown
from core.workers.tracebacks import TracebackSerializer, print_friendly_syntax_error
from core.workers.utils import internal_error_result, make_result, output_buffer, run_async

log = logging.getLogger(__name__)

console = InteractiveConsole()
console.locals = {"assert_equal": assert_equal}


def execute(code_obj):
    try:
        exec(code_obj, console.locals)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        return TracebackSerializer().format_exception(e)


def run_code(code_source, code):
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

    friendly_traceback.source_cache.cache.add(filename, code)

    try:
        code_obj = compile(code, filename, mode)
    except SyntaxError as e:
        print_friendly_syntax_error(e)
        return {}

    result = {}

    if code_source == "snoop":
        from core.workers.snoop import exec_snoop
        traceback_info = exec_snoop(filename, code, code_obj)
    elif code_source == "birdseye":
        from core.workers.birdseye import exec_birdseye

        traceback_info, result["birdseye_objects"] = exec_birdseye(filename, code)
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

    return result


def check_entry_catch_internal_errors(entry, input_callback, result_callback):
    try:
        check_entry(entry, input_callback, result_callback)
    except Exception:
        result_callback(internal_error_result())


def find_imports_to_install(imports):
    to_install = []
    for module in imports:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            to_install.append(module)
    return to_install


@run_async
async def check_entry(entry, input_callback, result_callback):
    if hasattr(entry, "to_py"):
        entry = entry.to_py()

        # Try automatically installing imports but don't interrupt the course
        # in case of failure, e.g. https://github.com/alexmojaki/futurecoder/issues/175
        try:
            import pyodide_js  # noqa
            import pyodide     # noqa

            imports = pyodide.find_imports(entry["input"])
            to_install = find_imports_to_install(imports)
            if to_install:
                await pyodide_js.loadPackage("micropip")
                import micropip  # noqa

                to_package_name = pyodide_js._module._import_name_to_package_name.to_py()
                packages_names = [to_package_name.get(mod, mod) for mod in to_install]
                await micropip.install(packages_names)
        except Exception:
            log.exception("Error installing imports")

    patch_stdin(input_callback, result_callback)

    with redirect_stdout(output_buffer.stdout), redirect_stderr(output_buffer.stderr):
        try:
            run_results = run_code(entry["source"], entry["input"])
        except KeyboardInterrupt:
            result_callback(
                make_result(
                    output='',
                    output_parts=[],
                )
            )
            return

    output = output_buffer.string()

    page = pages[entry["page_slug"]]
    step_cls = page.get_step(entry["step_name"])

    step_result = False
    if entry["step_name"] != "final_text":
        step_instance = step_cls(entry["input"], output, entry["source"], console)
        try:
            step_result = step_instance.check_with_messages()
        except SyntaxError:
            pass

    step_result = normalise_step_result(step_result)
    passed = step_result["passed"]
    messages = [highlighted_markdown(message) for message in step_result["messages"]]

    if passed:
        prediction = dict(
            choices=step_cls.predicted_output_choices,
            answer=step_cls.correct_output,
        )
    else:
        prediction = None

    result_callback(
        make_result(
            passed=passed,
            messages=messages,
            output=output,
            prediction=prediction,
            **run_results,
        )
    )


def normalise_step_result(step_result):
    if not isinstance(step_result, dict):
        assert isinstance(step_result, bool)
        step_result = dict(passed=step_result, messages=[])

    step_result.setdefault("passed", False)

    messages = step_result.setdefault("messages", [])
    if "message" in step_result:
        messages.append(step_result.pop("message"))

    return step_result


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
