import sys
import traceback

from sentry_sdk import capture_exception


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

    return dict(
        passed=passed,
        message=message,
        awaiting_input=awaiting_input,
        output=output,
        output_parts=output_parts,
        birdseye_objects=birdseye_objects,
        error=error,
    )


def internal_error_result(sentry_offline=False):
    if sentry_offline:
        sentry_event = None
        # TODO https://stackoverflow.com/questions/60801638/how-to-capture-an-easily-serialisable-exception-event-with-sentry
        # exc_info = sys.exc_info()
        # sentry_event = event_from_exception(exc_info)
    else:
        sentry_event = None
        capture_exception()

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
