import functools
import os
import sys
import traceback
from asyncio import get_event_loop

import stack_data


class SysStream:
    def __init__(self, output, color):
        self.output = output
        self.color = color

    def __getattr__(self, item):
        return getattr(sys.__stdout__, item)

    def write(self, s):
        if not s:
            return

        if isinstance(s, bytes):
            s = s.decode("utf8", "replace")

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


def make_result(
        passed=False,
        messages=(),
        awaiting_input=False,
        output=None,
        output_parts=None,
        birdseye_objects=None,
        error=None,
        prediction=None,
):
    if output is None:
        output = output_buffer.string()

    if output_parts is None:
        output_parts = output_buffer.pop()

    if not awaiting_input:
        output_parts.append(dict(text=">>> ", color="white"))

    if prediction is None:
        prediction = dict(choices=None, answer=None)

    result = dict(
        passed=passed,
        messages=messages,
        awaiting_input=awaiting_input,
        output=output,
        output_parts=output_parts,
        birdseye_objects=birdseye_objects,
        error=error,
        prediction=prediction,
    )
    return result


def get_exception_event():
    import sentry_sdk

    os.environ["SENTRY_RELEASE"] = "stubbed"  # TODO get git commit?

    event = {}

    def transport(e):
        nonlocal event
        event = e

    client = sentry_sdk.Client(transport=transport)
    hub = sentry_sdk.Hub(client)
    hub.capture_exception()

    assert event
    return event


def safe_traceback(e: Exception):
    try:
        return "".join(
            stack_data.Formatter(show_variables=True, chain=True).format_exception(e)
        )
    except Exception:
        pass
    try:
        return "".join(
            stack_data.Formatter(show_variables=False, chain=True).format_exception(e)
        )
    except Exception:
        pass
    try:
        return "".join(
            stack_data.Formatter(show_variables=True, chain=False).format_exception(e)
        )
    except Exception:
        pass
    try:
        return "".join(
            stack_data.Formatter(show_variables=False, chain=False).format_exception(e)
        )
    except Exception:
        return "".join(traceback.format_exception(type(e), e, e.__traceback__))


def internal_error_result(e: Exception):
    from snoop.utils import truncate

    exception_string = "".join(traceback.format_exception_only(type(e), e))

    return make_result(
        output="",
        output_parts=[],
        error=dict(
            details=safe_traceback(e),
            title=f"Error running Python code: {truncate(exception_string, 100, '...')}",
            sentry_event=get_exception_event(),
        ),
    )


def run_async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        get_event_loop().run_until_complete(result)

    return wrapper
