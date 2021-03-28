import linecache
import logging
import os
import sys
from code import InteractiveConsole
from threading import Thread
from time import sleep

import friendly.source_cache
import stack_data

from main import simple_settings
from main.exercises import assert_equal
from main.text import pages
from main.workers.limits import set_limits
from main.workers.tracebacks import TracebackSerializer, print_friendly_syntax_error
from main.workers.utils import internal_error_result, make_result, output_buffer

log = logging.getLogger(__name__)

console = InteractiveConsole()
console.locals = {"assert_equal": assert_equal}


def execute(code_obj):
    sys.setrecursionlimit(100)
    try:
        # noinspection PyTypeChecker
        exec(code_obj, console.locals)
    except Exception as e:
        sys.setrecursionlimit(1000)
        return TracebackSerializer().format_exception(e)
    finally:
        sys.setrecursionlimit(1000)


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
        from main.workers.snoop import exec_snoop
        traceback_info = exec_snoop(filename, code, code_obj)
    elif code_source == "birdseye":
        from main.workers.birdseye import exec_birdseye
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


def worker_loop_in_thread(*args):
    Thread(target=worker_loop, args=args).start()


def worker_loop(task_queue, input_queue, result_queue):
    os.environ.clear()
    os.environ.update(
        OUTDATED_IGNORE="1",
    )

    # Open the queue files before setting the file limit
    sleep(0.01)
    result_queue.put(None)
    sleep(0.01)
    input_queue.empty()
    task_queue.empty()

    if simple_settings.Root.SET_LIMITS:
        set_limits()

    while True:
        entry = task_queue.get()
        try:
            run_code(entry, input_queue, result_queue)
        except Exception:
            result_queue.put(internal_error_result(sentry_offline=True))


def run_code(entry, input_queue, result_queue):
    def readline():
        result_queue.put(make_result(awaiting_input=True))
        return input_queue.get()

    sys.stdin.readline = readline

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    try:
        sys.stdout = output_buffer.stdout
        sys.stderr = output_buffer.stderr
        birdseye_objects = runner(entry['source'], entry['input'])
    finally:
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

    messages = []
    passed = False
    output = output_buffer.string()

    if entry['step_name'] != "final_text":
        page = pages[entry['page_slug']]
        step_result = page.check_step(entry, output, console)
        if isinstance(step_result, dict):
            passed = step_result.get("passed", False)
            messages = step_result.get("messages", [])
            if "message" in step_result:
                messages.append(step_result["message"])
        else:
            passed = step_result

    result_queue.put(make_result(
        passed=passed,
        messages=messages,
        output=output,
        birdseye_objects=birdseye_objects,
    ))
