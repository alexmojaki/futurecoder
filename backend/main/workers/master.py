import atexit
import multiprocessing
import queue
from collections import defaultdict
from functools import lru_cache
from multiprocessing import Queue, Process
from threading import Thread
from time import sleep

import flask

from main import simple_settings
from main.workers.utils import internal_error_result, make_result
from main.workers.worker import worker_loop_in_thread

TESTING = False


class UserProcess:
    def __init__(self):
        self.task_queue = Queue()
        self.input_queue = Queue()
        self.result_queue = Queue()
        self.awaiting_input = False
        self.process = None
        self.fresh_process = True
        self.start_process()

        @atexit.register
        def cleanup():
            if self.process:
                self.process.terminate()

    def start_process(self):
        self.fresh_process = True
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

    def await_result(self):
        result = self._await_result()
        # if result["error"] and result["error"]["sentry_event"]:
        #     event, hint = result["error"]["sentry_event"]
        #     capture_event(event, hint)
        self.awaiting_input = result["awaiting_input"]
        return result

    def _await_result(self):
        # TODO cancel if result was cancelled by a newer handle_entry
        result = None
        while result is None:
            timeout = 10 if self.fresh_process else 3
            try:
                result = self.result_queue.get(timeout=timeout)
                assert (result is None) == self.fresh_process
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
            self.fresh_process = False
        return result


user_processes = defaultdict(UserProcess)

app = flask.Flask(__name__)

try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    # noinspection PyArgumentList
    assert multiprocessing.get_start_method() == "spawn"


@app.route("/run", methods=["POST"])
def run():
    try:
        entry = flask.request.json
        user_process = user_processes[entry["user_id"]]
        user_process.handle_entry(entry)
        return user_process.await_result()
    except Exception:
        return internal_error_result()


@app.route("/health")
def health():
    return "ok"


def run_server():
    app.run(host="0.0.0.0")


master_url = "http://localhost:5000/"


@lru_cache()
def master_session():
    import requests
    session = requests.Session()

    if not simple_settings.SEPARATE_WORKER_PROCESS:
        Thread(
            target=run_server,
            daemon=True,
            name=run_server.__name__,
        ).start()

        # Wait until alive
        while True:
            try:
                session.get(master_url + "health")
                break
            except requests.exceptions.ConnectionError:
                sleep(1)

    return session


def worker_result(entry):
    session = master_session()
    return session.post(master_url + "run", json=entry).json()


if __name__ == '__main__':
    run_server()
