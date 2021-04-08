import atexit
import json
import logging
import multiprocessing
import queue
from collections import defaultdict, deque
from functools import lru_cache
from multiprocessing import Process, Queue
from threading import Thread, RLock
from time import sleep, time

import flask
import psutil
import sentry_sdk
from littleutils import select_attrs, DecentJSONEncoder, select_keys

from main import simple_settings
from main.simple_settings import MONITOR
from main.workers.utils import internal_error_result, make_result
from main.workers.worker import worker_loop_in_thread

TESTING = False

log = logging.getLogger(__name__)


class UserProcess:
    def __init__(self):
        self.user_id = None
        self.lock = RLock()
        self.task_queue = None
        self.input_queue = None
        self.result_queue = None
        self.awaiting_input = False
        self.process = None
        self.fresh_process = True
        self.last_used = float('inf')
        self.start_process()
        self.history = deque(maxlen=MONITOR.PROCESS_HISTORY_SIZE)

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

    @property
    def ps(self):
        return psutil.Process(self.process.pid)

    @property
    def time_since_last_used(self):
        return int(time() - self.last_used)

    def start_process(self):
        self.cleanup(in_background=True)
        self.fresh_process = True
        self.awaiting_input = False
        self.task_queue = Queue()
        self.input_queue = Queue()
        self.result_queue = Queue()
        self.process = Process(
            target=worker_loop_in_thread,
            args=(self.task_queue, self.input_queue, self.result_queue),
            daemon=True,
        )
        self.process.start()

    def handle_entry(self, entry):
        self.last_used = time()
        history_item = dict(start_time=self.last_used, entry=entry)
        self.history.append(history_item)
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
        if result["error"] and result["error"]["sentry_event"]:
            sentry_sdk.capture_event(result["error"]["sentry_event"])
        self.awaiting_input = result["awaiting_input"]

        history_item.update(
            end_time=time(),
            elapsed=time() - history_item["start_time"],
            result=select_keys(result, "passed output awaiting_input"),
        )
        return result

    def _await_result(self):
        # TODO cancel if result was cancelled by a newer handle_entry
        result = None
        while result is None:
            if simple_settings.Root.SET_LIMITS:
                timeout = 10 if self.fresh_process else 3
            else:
                timeout = None
            try:
                result = self.result_queue.get(timeout=timeout)
                assert (result is None) == self.fresh_process
                self.fresh_process = False
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


user_processes = defaultdict(UserProcess)

app = flask.Flask(__name__)

try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    # noinspection PyArgumentList
    assert multiprocessing.get_start_method() == "spawn"


def monitor_processes():
    while True:
        sleep(MONITOR.SLEEP_TIME)
        log.info(f"Number of user processes: {len(user_processes)}")
        for func in [kill_old_processes, dump_process_info]:
            try:
                func()
            except Exception:
                log.exception(f"Error in {func.__name__}")


def kill_old_processes():
    for user_id, process in list(user_processes.items()):
        since = process.time_since_last_used
        if since > MONITOR.MAX_SINCE:
            log.info(f"Terminating process of user {user_id} last used {since} seconds ago")
            del user_processes[user_id]
            with process.lock:
                process.close()


def dump_process_info():
    user_processes_by_pid = {p.process.pid: p for p in user_processes.values()}

    def user_process_info(pid):
        if pid not in user_processes_by_pid:
            return None
        user_process = user_processes_by_pid[pid]
        return select_attrs(
            user_process,
            "user_id time_since_last_used awaiting_input fresh_process history",
        )

    process_infos = [
        dict(
            **p.as_dict(["cmdline", "pid", "status"]),
            user_process=user_process_info(p.pid),
            memory_info=p.memory_info()._asdict(),
            cpu_times=p.cpu_times()._asdict(),
        )
        for p in psutil.process_iter()
        if p
    ]
    log.info(
        f"Process info dump: {json.dumps(process_infos, cls=DecentJSONEncoder)}"
    )


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
        with user_process.lock:
            return user_process.handle_entry(entry)
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
