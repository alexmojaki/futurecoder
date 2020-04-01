import atexit
import multiprocessing
import queue
from collections import defaultdict, deque
from functools import lru_cache
from multiprocessing import Queue, Process
from threading import Thread
from time import sleep, time

import flask
import psutil
import sentry_sdk

from main import simple_settings
from main.simple_settings import MONITOR
from main.workers.utils import internal_error_result, make_result
from main.workers.worker import worker_loop_in_thread

TESTING = False


class UserProcess:
    def __init__(self):
        self.user_id = None
        self.task_queue = Queue()
        self.input_queue = Queue()
        self.result_queue = Queue()
        self.awaiting_input = False
        self.process = None
        self.fresh_process = True
        self.last_used = float('inf')
        self.start_process()

        atexit.register(self.atexit_cleanup)

    def atexit_cleanup(self):
        if self.process:
            self.process.terminate()

    def close(self):
        atexit.unregister(self.atexit_cleanup)
        for q in [self.task_queue, self.input_queue, self.result_queue]:
            q.close()
        self.process.terminate()

    @property
    def ps(self):
        return psutil.Process(self.process.pid)

    def start_process(self):
        self.fresh_process = True
        self.process = Process(
            target=worker_loop_in_thread,
            args=(self.task_queue, self.input_queue, self.result_queue),
            daemon=True,
        )
        self.process.start()

    def handle_entry(self, entry):
        self.last_used = time()
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
        if result["error"] and result["error"]["sentry_event"]:
            sentry_sdk.capture_event(result["error"]["sentry_event"])
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


def monitor_processes():
    history = deque([], MONITOR.NUM_MEASUREMENTS)
    while True:
        sleep(MONITOR.SLEEP_TIME)
        percent = psutil.virtual_memory().percent
        history.append(percent)
        print(f"Recent memory usage: {history}")
        print(f"Number of user processes: {len(user_processes)}")
        if (
                len(history) == history.maxlen
                and min(history) > MONITOR.THRESHOLD
                and len(user_processes) > MONITOR.MIN_PROCESSES
        ):
            oldest = min(user_processes.values(), key=lambda p: p.last_used)
            print(f"Terminating process last used {int(time() - oldest.last_used)} seconds ago")
            del user_processes[oldest.user_id]
            oldest.close()
            history.clear()


@lru_cache()
def start_monitor():
    if MONITOR.ACTIVE:
        Thread(
            target=monitor_processes,
            name=monitor_processes.__name__,
            daemon=True,
        ).start()


@app.route("/run", methods=["POST"])
def run():
    start_monitor()
    try:
        entry = flask.request.json
        user_id = entry["user_id"]
        user_process = user_processes[user_id]
        user_process.user_id = user_id
        user_process.handle_entry(entry)
        return user_process.await_result()
    except Exception:
        return internal_error_result()


@app.route("/health")
def health():
    return "ok"


def run_server():
    app.run(host="0.0.0.0")


@lru_cache()
def master_session():
    import requests
    session = requests.Session()

    if not simple_settings.Root.SEPARATE_WORKER_PROCESS:
        Thread(
            target=run_server,
            daemon=True,
            name=run_server.__name__,
        ).start()

        # Wait until alive
        while True:
            try:
                session.get(simple_settings.Root.MASTER_URL + "health")
                break
            except requests.exceptions.ConnectionError:
                sleep(1)

    return session


def worker_result(entry):
    session = master_session()
    return session.post(simple_settings.Root.MASTER_URL + "run", json=entry).json()


if __name__ == '__main__':
    run_server()
