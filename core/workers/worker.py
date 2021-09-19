import ast
import builtins
import importlib
import inspect
import linecache
import logging
import sys
from asyncio import get_event_loop
from code import InteractiveConsole
from collections import defaultdict
from contextlib import redirect_stdout, redirect_stderr

import friendly_traceback.source_cache
import stack_data

from core.exercises import assert_equal
from core.text import pages
from core.utils import highlighted_markdown
from core.workers.question_wizard import question_wizard_check
from core.workers.tracebacks import (
    TracebackSerializer,
    print_friendly_syntax_error,
    TracebackFormatter,
)
from core.workers.utils import (
    internal_error_result,
    make_result,
    output_buffer,
    run_async,
)

log = logging.getLogger(__name__)

console = InteractiveConsole()
console.locals = {"assert_equal": assert_equal}


def execute(code_obj):
    try:
        exec(code_obj, console.locals)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        output_buffer.parts.append(
            dict(
                isTraceback=True,
                tracebacks=TracebackSerializer().format_exception(e),
                text="".join(
                    TracebackFormatter(
                        options=stack_data.Options(before=1, after=0),
                        show_variables=True,
                    ).format_exception(e)
                ),
                color="red",
            )
        )


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

        exec_snoop(filename, code, code_obj)
    elif code_source == "birdseye":
        from core.workers.birdseye import exec_birdseye

        result["birdseye_objects"] = exec_birdseye(filename, code)
    else:
        execute(code_obj)

    if output_buffer.parts and (part := output_buffer.parts[-1]).get("isTraceback"):
        part["codeSource"] = code_source

    return result


def check_entry_catch_internal_errors(entry, input_callback, result_callback):
    get_event_loop().set_exception_handler(
        lambda loop, context: result_callback(
            internal_error_result(context["exception"])
        )
    )
    check_entry(entry, input_callback, result_callback)


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

    if not entry["input"].strip():
        result_callback(make_result())
        return

    question_wizard = entry.get("question_wizard")

    patch_stdin(input_callback, result_callback, question_wizard)

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

    if question_wizard:
        messages = question_wizard_check(entry, output)
        result_callback(
            make_result(
                messages=messages,
                output=output,
                **run_results,
            )
        )
        return

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


input_nodes = defaultdict(list)


def patch_stdin(input_callback, result_callback, question_wizard):
    def readline(*_):
        result_callback(make_result(awaiting_input=True))
        result = input_callback()
        if not isinstance(result, str):
            while True:
                pass  # wait for the interrupt
        return result

    sys.stdin.readline = readline

    input_nodes.clear()

    def patched_input(prompt=""):
        print(prompt, end="")
        result = sys.stdin.readline().rstrip("\n")

        try:
            assert question_wizard
            frame = inspect.currentframe().f_back
            assert frame.f_code.co_filename == "my_program.py"
            ex = stack_data.Source.executing(frame)
            node = ex.node
            assert isinstance(node, ast.Call)
            input_nodes[node].append((result, ex))
        except Exception:
            pass

        return result

    builtins.input = patched_input
