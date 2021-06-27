import atexit
import logging
from functools import lru_cache
from multiprocessing import Process, Queue
from threading import Thread, RLock

from core.workers.utils import internal_error_result
from core.workers.worker import check_entry_catch_internal_errors

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
            if self.awaiting_input:
                self.start_process()

            self.task_queue.put(entry)

        result = self.result_queue.get()
        self.awaiting_input = result["awaiting_input"]

        return result


def run_code_entry(entry):
    try:
        user_process = UserProcess()
        with user_process.lock:
            return user_process.handle_entry(entry)
    except Exception:
        return internal_error_result()


def worker_loop(task_queue, input_queue, result_queue):
    while True:
        entry = task_queue.get()
        check_entry_catch_internal_errors(entry, input_queue.get, result_queue.put)
