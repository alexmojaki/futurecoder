import sys
import time
from contextlib import contextmanager, redirect_stdout, redirect_stderr


class OutputBuffer:
    def __init__(self, flush):
        self._flush = flush
        self.reset()

    def reset(self):
        self.parts = []
        self.last_time = time.time()

    def put(self, output_type, text, **extra):
        if isinstance(text, bytes):
            text = text.decode("utf8", "replace")
        if not isinstance(text, str):
            raise TypeError(f"Can only write str, not {type(text).__name__}")
        assert isinstance(output_type, str)

        if not self.parts or self.parts[-1]["type"] != output_type:
            self.parts.append(dict(type=output_type, text=text, **extra))
        else:
            self.parts[-1]["text"] += text

        if self.should_flush():
            self.flush()

    def should_flush(self):
        return (
            len(self.parts) > 1
            or self.last_time and self.last_time - time.time() > 1
            or sum(len(p["text"]) for p in self.parts) > 1000
        )

    def flush(self):
        if not self.parts:
            return
        self._flush(self.parts)
        self.reset()

    @contextmanager
    def redirect_std_streams(self):
        with (
            redirect_stdout(SysStream("stdout", self)),  # noqa
            redirect_stderr(SysStream("stderr", self)),  # noqa
        ):
            yield


class SysStream:
    def __init__(self, output_type, output_buffer):
        self.type = output_type
        self.output_buffer = output_buffer

    def __getattr__(self, item):
        return getattr(sys.__stdout__, item)

    def write(self, s):
        self.output_buffer.put(self.type, s)

    def flush(self):
        self.output_buffer.flush()
