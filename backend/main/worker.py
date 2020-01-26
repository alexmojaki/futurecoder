import ast
import linecache
import logging
import multiprocessing
import os
import sys
from code import InteractiveConsole
from functools import lru_cache
from multiprocessing import Pool, Pipe
from multiprocessing.connection import Connection
from threading import Thread

import atexit
import snoop
import snoop.formatting
import snoop.tracer

from main.text import pages
from main.utils import format_exception_string

log = logging.getLogger(__name__)

TESTING = False

output_lines = []

snoop.install(out=sys.__stderr__)


class SysStream:
    def __init__(self, color):
        self.color = color
        self.buf = ''

    def __getattr__(self, item):
        return getattr(sys.__stdout__, item)

    def write(self, s):
        self.buf += s
        lines = self.buf.split('\n')
        output_lines.extend(
            dict(text=line or ' ', color=self.color)
            for line in lines[:-1]
        )
        self.buf = lines[-1]

    # TODO return last bit of output without \n


snoop.tracer.internal_directories += (os.path.dirname((lambda: 0).__code__.co_filename),)


class PatchedFrameInfo(snoop.tracer.FrameInfo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        code = self.frame.f_code
        self.is_ipython_cell = (
                code.co_name == '<module>' and
                code.co_filename == "my_program.py"
        )


snoop.tracer.FrameInfo = PatchedFrameInfo

console = InteractiveConsole()


def runner(code_source, code):
    if code_source == "shell":
        return console.push(code)

    use_snoop = code_source == "snoop"
    console.locals = {}
    filename = "my_program.py"
    linecache.cache[filename] = (
        len(code),
        None,
        [line + '\n' for line in code.splitlines()],
        filename,
    )
    snoop.formatting.Source._class_local('__source_cache', {}).pop(filename, None)

    try:
        code_obj = compile(code, filename, "exec")
    except SyntaxError as e:
        print(format_exception_string(e), file=sys.stderr)
        return

    try:
        if use_snoop:
            config = snoop.Config(
                columns=(),
                out=sys.stdout,
                color=True,
            )
            tracer = config.snoop()
            tracer.variable_whitelist = set()
            for node in ast.walk(ast.parse(code)):
                if isinstance(node, ast.Name):
                    name = node.id
                    tracer.variable_whitelist.add(name)
            tracer.target_codes.add(code_obj)
            with tracer:
                exec(code_obj, console.locals)
        else:
            exec(code_obj, console.locals)

    except Exception as e:
        print(format_exception_string(e), file=sys.stderr)


def run_code(entry, input_queue, result_queue):
    def readline():
        result_queue.put(dict(
            lines=output_lines.copy(),
            passed=False,
            message='',
            output='',
            awaiting_input=True,
        ))
        output_lines.clear()
        return input_queue.get()

    sys.stdin.readline = readline

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    try:
        sys.stdout = SysStream("white")
        sys.stderr = SysStream("red")
        runner(entry['source'], entry['input'])
    finally:
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

    # TODO include all lines from multiple steps
    output = "\n".join(line["text"] for line in output_lines)

    message = ""
    passed = False

    if entry['step_name'] != "final_text":
        page = pages[entry['page_slug']]
        step_result = page.check_step(entry, output, console)
        if isinstance(step_result, dict):
            passed = step_result.get("passed", False)
            message = step_result.get("message", "")
        else:
            passed = step_result

    result_queue.put(dict(
        lines=output_lines.copy(),
        passed=passed,
        message=message,
        output=output,
        awaiting_input=False,
    ))
    output_lines.clear()


def consumer(connection: Connection):
    pool = Pool(1)

    def cleanup():
        pool.terminate()

    atexit.register(cleanup)

    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    result_queue = manager.Queue()

    awaiting_input = False

    def run():
        pool.apply_async(run_code, (entry, input_queue, result_queue))

    while True:
        entry = connection.recv()
        if entry["source"] == "shell":
            if awaiting_input:
                input_queue.put(entry["input"])
            else:
                run()
        else:
            if not TESTING:
                pool.terminate()
                pool = Pool(1)

            run()
        result = result_queue.get()
        awaiting_input = result["awaiting_input"]
        connection.send(result)


@lru_cache
def worker_connection():
    parent_connection, child_connection = Pipe()
    p = Thread(target=consumer, args=(child_connection,), daemon=True)
    p.start()
    return parent_connection
