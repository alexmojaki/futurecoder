import ast
import atexit
import inspect
import linecache
import logging
import multiprocessing
import os
import queue
import resource
import sys
from code import InteractiveConsole
from functools import lru_cache
from importlib import import_module
from multiprocessing import Pool, Pipe
from multiprocessing.connection import Connection
from threading import Thread

import snoop
import snoop.formatting
import snoop.tracer

from main.text import pages
from main.utils import format_exception_string

log = logging.getLogger(__name__)

TESTING = False

snoop.install(out=sys.__stderr__, columns=['thread'])


class SysStream:
    def __init__(self, output, color):
        self.output = output
        self.color = color

    def __getattr__(self, item):
        return getattr(sys.__stdout__, item)

    def write(self, s):
        # TODO limit output length
        self.output.parts.append(
            dict(text=s, color=self.color)
        )


class OutputBuffer:
    def __init__(self):
        self.parts = []
        self.stdout = SysStream(self, "white")
        self.stderr = SysStream(self, "red")

    def pop(self):
        parts = self.parts.copy()
        self.parts.clear()
        return parts

    def string(self):
        return "".join(part["text"] for part in self.parts)


output_buffer = OutputBuffer()

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


@lru_cache
def destroy_dangerous_functions():
    import signal
    import gc

    del signal.sigwait.__doc__

    bad_module_names = "signal _signal".split()

    func = None
    get_referrers = gc.get_referrers

    funcs = [get_referrers, gc.get_referents, gc.get_objects, os.system]
    expected_refs = [locals(), funcs]

    for module_name in bad_module_names:
        module = import_module(module_name)
        funcs += [
            value for value in module.__dict__.values()
            if inspect.isroutine(value)
            if getattr(value, "__module__", None) in bad_module_names
        ]

    for func in funcs:
        for ref in get_referrers(func):
            if ref in expected_refs:
                continue

            if isinstance(ref, dict):
                for key in list(ref):
                    if ref[key] == func:
                        del ref[key]

            if isinstance(ref, list):
                while func in ref:
                    ref.remove(func)

        for ref in get_referrers(func):
            assert ref in expected_refs


def set_limits():
    destroy_dangerous_functions()

    usage = resource.getrusage(resource.RUSAGE_SELF)

    # TODO tests can exceed this time since the process is not restarted, causing failure
    max_time = int(usage.ru_utime + usage.ru_stime) + 2
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (max_time, max_time))
    except ValueError:
        pass

    # TODO
    # resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))


def run_code_in_thread(*args):
    # run_code(*args)
    Thread(target=run_code, args=args).start()


def put_result(
        q, *,
        passed=False,
        message='',
        awaiting_input=False,
        output=None,
        output_parts=None,
):
    if output is None:
        output = output_buffer.string()

    if output_parts is None:
        output_parts = output_buffer.pop()

    q.put(dict(
        passed=passed,
        message=message,
        awaiting_input=awaiting_input,
        output=output,
        output_parts=output_parts,
    ))

    return output


def run_code(entry, input_queue, result_queue):
    # Open the queue files before setting the file limit
    result_queue.put(None)
    input_queue.empty()

    set_limits()

    def readline():
        put_result(
            result_queue,
            awaiting_input=True,
        )
        return input_queue.get()

    sys.stdin.readline = readline

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    try:
        sys.stdout = output_buffer.stdout
        sys.stderr = output_buffer.stderr
        runner(entry['source'], entry['input'])
    finally:
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

    message = ""
    passed = False
    output = output_buffer.string()

    if entry['step_name'] != "final_text":
        page = pages[entry['page_slug']]
        step_result = page.check_step(entry, output, console)
        if isinstance(step_result, dict):
            passed = step_result.get("passed", False)
            message = step_result.get("message", "")
        else:
            passed = step_result

    put_result(
        result_queue,
        passed=passed,
        message=message,
        output=output,
    )


class ManagedPool:
    def __init__(self):
        self.pool = Pool(1)
        self.original_pid = self.current_pid

    def restart(self):
        Thread(target=self.terminate).start()
        self.__init__()

    @property
    def current_pid(self):
        return self._pool[0].pid

    @property
    def died(self):
        return self.original_pid != self.current_pid

    def __getattr__(self, item):
        return getattr(self.pool, item)


def consumer(connection: Connection):
    pool = ManagedPool()

    def cleanup():
        pool.terminate()

    atexit.register(cleanup)

    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    result_queue = manager.Queue()

    awaiting_input = False

    def run():
        # run_code_in_thread(entry, input_queue, result_queue)
        pool.apply_async(run_code_in_thread, (entry, input_queue, result_queue))

    while True:
        entry = connection.recv()
        if entry["source"] == "shell":
            if awaiting_input:
                input_queue.put(entry["input"])
            else:
                run()
        else:
            if not TESTING and awaiting_input:
                pool.restart()

            run()
        result = None
        while result is None:
            try:
                result = result_queue.get(timeout=3)
            except queue.Empty:
                if pool.died:
                    pool.restart()
                    result = dict(
                        output_parts=[
                            dict(color='red', text='The process died.\n'),
                            dict(color='red', text='Your code probably took too long.\n'),
                            dict(color='red', text='Maybe you have an infinite loop?\n'),
                        ],
                        passed=False,
                        message='',
                        output='The process died.',
                        awaiting_input=False,
                    )
        awaiting_input = result["awaiting_input"]
        connection.send(result)


@lru_cache
def worker_connection():
    parent_connection, child_connection = Pipe()
    p = Thread(target=consumer, args=(child_connection,), daemon=True)
    p.start()
    return parent_connection
