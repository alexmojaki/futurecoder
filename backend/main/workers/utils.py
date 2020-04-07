import json
import multiprocessing.queues
import sys
import traceback

import sentry_sdk
from littleutils import DecentJSONEncoder


class SysStream:
    def __init__(self, output, color):
        self.output = output
        self.color = color

    def __getattr__(self, item):
        return getattr(sys.__stdout__, item)

    def write(self, s):
        if not s:
            return
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

json_encoder = DecentJSONEncoder()


def make_result(
        passed=False,
        message='',
        awaiting_input=False,
        output=None,
        output_parts=None,
        birdseye_objects=None,
        error=None,
):
    if output is None:
        output = output_buffer.string()

    if output_parts is None:
        output_parts = output_buffer.pop()

    result = dict(
        passed=passed,
        message=message,
        awaiting_input=awaiting_input,
        output=output,
        output_parts=output_parts,
        birdseye_objects=birdseye_objects,
        error=error,
    )
    # Check that JSON encoding works here
    # because failures in the queue pickling are silent
    json_pickler.dumps(result)
    return result


# Import eagerly
sentry_sdk.Hub(sentry_sdk.Client(transport=lambda e: None))


def get_exception_event():
    event = {}

    def transport(e):
        nonlocal event
        event = e

    client = sentry_sdk.Client(transport=transport)
    hub = sentry_sdk.Hub(client)
    hub.capture_exception()

    assert event
    return event


def internal_error_result(sentry_offline=False):
    if sentry_offline:
        sentry_event = get_exception_event()
    else:
        sentry_event = None
        sentry_sdk.capture_exception()

    tb = traceback.format_exc()
    output = f"""
INTERNAL ERROR IN COURSE:
=========================

{tb}

This is an error in our code, not yours.
"""
    return make_result(
        output=output,
        output_parts=[dict(color="red", text=output)],
        error=dict(traceback=tb, sentry_event=sentry_event),
    )


# Queues don't communicate in pickle so that the worker
# can't put something malicious for the master to unpickle
class JsonPickler:
    def loads(self, b):
        return json.loads(b.decode("utf8"))

    def dumps(self, x):
        return json_encoder.encode(x).encode("utf8")


multiprocessing.queues._ForkingPickler = json_pickler = JsonPickler()
