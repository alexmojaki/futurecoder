import atexit
import inspect
import linecache
import logging
import multiprocessing
import os
import queue
import resource
import sys
import traceback
from code import InteractiveConsole
from collections import defaultdict
from functools import lru_cache
from importlib import import_module
from multiprocessing.context import Process
from threading import Thread

from littleutils import setup_quick_console_logging

from main.text import pages
from main.utils import print_exception
from main.workers.communications import AbstractCommunications, ThreadCommunications


log = logging.getLogger(__name__)

TESTING = False


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


console = InteractiveConsole()


def execute(code_obj):
    try:
        # noinspection PyTypeChecker
        exec(code_obj, console.locals)
    except Exception:
        print_exception()


def runner(code_source, code):
    if code_source == "shell":
        console.push(code)
        return {}

    console.locals = {}
    filename = "my_program.py"
    linecache.cache[filename] = (
        len(code),
        None,
        [line + '\n' for line in code.splitlines()],
        filename,
    )

    try:
        code_obj = compile(code, filename, "exec")
    except SyntaxError:
        print_exception()
        return {}

    birdseye_objects = None

    if code_source == "snoop":
        from main.workers.snoop import exec_snoop
        exec_snoop(filename, code, code_obj)
    elif code_source == "birdseye":
        from main.workers.birdseye import exec_birdseye
        birdseye_objects = exec_birdseye(filename, code)
    else:
        execute(code_obj)

    return birdseye_objects


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

    from main.workers import snoop, birdseye
    str([snoop, birdseye])

    resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))


def make_result(
        passed=False,
        message='',
        awaiting_input=False,
        output=None,
        output_parts=None,
        birdseye_objects=None,
):
    if output is None:
        output = output_buffer.string()

    if output_parts is None:
        output_parts = output_buffer.pop()

    return dict(
        passed=passed,
        message=message,
        awaiting_input=awaiting_input,
        output=output,
        output_parts=output_parts,
        birdseye_objects=birdseye_objects,
    )


def internal_error_result():
    output = f"""
INTERNAL ERROR IN COURSE:
=========================

{"".join(traceback.format_exception(*sys.exc_info()))}

This is an error in our code, not yours.
Consider using the Feedback button in the top-right menu
to explain what led up to this.
"""
    return make_result(
        output=output,
        output_parts=[dict(color="red", text=output)],
    )


def worker_loop_in_thread(*args):
    Thread(target=worker_loop, args=args).start()


def worker_loop(task_queue, input_queue, result_queue):
    # Open the queue files before setting the file limit
    result_queue.put(None)
    input_queue.empty()
    task_queue.empty()

    set_limits()

    while True:
        entry = task_queue.get()
        try:
            run_code(entry, input_queue, result_queue)
        except Exception:
            result_queue.put(internal_error_result())


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

    result_queue.put(make_result(
        passed=passed,
        message=message,
        output=output,
        birdseye_objects=birdseye_objects,
    ))


class UserProcess:
    def __init__(self, manager):
        self.task_queue = manager.Queue()
        self.input_queue = manager.Queue()
        self.result_queue = manager.Queue()
        self.awaiting_input = False
        self.process = None
        self.start_process()

        @atexit.register
        def cleanup():
            if self.process:
                self.process.terminate()

    def start_process(self):
        self.process = Process(
            target=worker_loop_in_thread,
            args=(self.task_queue, self.input_queue, self.result_queue),
            daemon=True,
        )
        self.process.start()

    def handle_entry(self, entry):
        if entry["source"] == "shell":
            if self.awaiting_input:
                self.input_queue.put(entry["input"])
            else:
                self.task_queue.put(entry)
        else:
            if not TESTING and self.awaiting_input:
                self.process.terminate()
                self.start_process()

            self.task_queue.put(entry)

    def await_result(self, callback):
        try:
            result = self._await_result()
        except Exception:
            result = internal_error_result()
        self.awaiting_input = result["awaiting_input"]
        callback(result)

    def _await_result(self):
        # TODO cancel if result was cancelled by a newer handle_entry
        result = None
        while result is None:
            try:
                result = self.result_queue.get(timeout=3)
            except queue.Empty:
                alive = self.process.is_alive()
                print(f"Process {alive=}")
                if alive:
                    self.process.terminate()
                self.start_process()
                result = make_result(
                    output_parts=[
                        dict(color='red', text='The process died.\n'),
                        dict(color='red', text='Your code probably took too long.\n'),
                        dict(color='red', text='Maybe you have an infinite loop?\n'),
                    ],
                    output='The process died.',
                )
        return result


def master_consumer_loop(comms: AbstractCommunications):
    comms = comms.make_master_side_communications()
    manager = multiprocessing.Manager()
    user_processes = defaultdict(lambda: UserProcess(manager))

    while True:
        entry = comms.recv_entry()
        user_id = str(entry["user_id"])

        def callback(result):
            comms.send_result(user_id, result)

        try:
            user_process = user_processes[user_id]
            user_process.handle_entry(entry)
            Thread(
                target=user_process.await_result,
                args=[callback],
            ).start()
        except Exception:
            callback(internal_error_result())


@lru_cache()
def master_communications() -> AbstractCommunications:
    from django.conf import settings
    if os.environ.get('CLOUDAMQP_URL'):
        from .workers.pika import PikaCommunications
        comms = PikaCommunications()
    else:
        comms = ThreadCommunications()

    if not settings.SEPARATE_WORKER_PROCESS:
        Thread(
            target=master_consumer_loop,
            args=[comms],
            daemon=True,
            name=master_consumer_loop.__name__,
        ).start()

    return comms


def worker_result(entry):
    comms: AbstractCommunications = master_communications()
    comms.send_entry(entry)
    user_id = str(entry["user_id"])
    return comms.recv_result(user_id)


def main():
    from main.workers.pika import PikaCommunications
    comms = PikaCommunications()
    master_consumer_loop(comms)


if __name__ == '__main__':
    setup_quick_console_logging()
    main()
