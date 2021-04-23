import atexit
import logging
import multiprocessing
import queue
from functools import lru_cache
from multiprocessing import Process, Queue
from threading import Thread, RLock

from main.workers.utils import internal_error_result, make_result
from main.workers.worker import worker_loop

TESTING = False

log = logging.getLogger(__name__)


@lru_cache
class UserProcess:
    def __init__(self):
        self.lock = RLock()
        self.task_queue = None
        self.input_queue = None
        self.result_queue = None
        self.awaiting_input = False
        self.process = None
        self.start_process()

        atexit.register(self.cleanup)

    def cleanup(self, *, in_background=False):
        process = self.process
        queues = [self.task_queue, self.input_queue, self.result_queue]

        if process is None:
            assert not any(queues), (process, queues)
            return

        def do():
            if process:
                process.terminate()
            for q in queues:
                if q:
                    q.close()

        if in_background:
            Thread(target=do).start()
        else:
            do()

    def close(self):
        atexit.unregister(self.cleanup)
        self.cleanup(in_background=True)

    def start_process(self):
        self.cleanup(in_background=True)
        self.awaiting_input = False
        self.task_queue = Queue()
        self.input_queue = Queue()
        self.result_queue = Queue()
        self.process = Process(
            target=worker_loop,
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
                self.start_process()

            self.task_queue.put(entry)

        result = self._await_result()
        self.awaiting_input = result["awaiting_input"]

        return result

    def _await_result(self):
        # TODO cancel if result was cancelled by a newer handle_entry
        result = None
        while result is None:
            try:
                result = self.result_queue.get()
            except queue.Empty:
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


try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    # noinspection PyArgumentList
    assert multiprocessing.get_start_method() == "spawn"


def run_code_entry(entry):
    try:
        user_process = UserProcess()
        with user_process.lock:
            return user_process.handle_entry(entry)
    except Exception:
        return internal_error_result()
