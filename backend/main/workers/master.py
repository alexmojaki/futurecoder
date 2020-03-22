import atexit
import multiprocessing
import queue
from collections import defaultdict
from functools import lru_cache
from multiprocessing.context import Process
from threading import Thread

from main import simple_settings
from main.workers.communications import AbstractCommunications, ThreadCommunications
from main.workers.utils import internal_error_result, make_result
from main.workers.worker import worker_loop_in_thread

TESTING = False


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
            # if result["error"] and result["error"]["sentry_event"]:
            #     event, hint = result["error"]["sentry_event"]
            #     capture_event(event, hint)
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
    if simple_settings.CLOUDAMQP_URL:
        from .pika import PikaCommunications
        comms = PikaCommunications()
    else:
        comms = ThreadCommunications()

    if not simple_settings.SEPARATE_WORKER_PROCESS:
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
    main()
