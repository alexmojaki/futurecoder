import sys
import traceback

import sentry_sdk


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


def internal_error_result():
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
        error=dict(traceback=tb),
    )
