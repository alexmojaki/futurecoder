import ast
import builtins
import linecache
import logging
import sys
import time
from code import InteractiveConsole
from contextlib import redirect_stdout, redirect_stderr

from .utils import format_traceback_string

log = logging.getLogger(__name__)


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
        assert isinstance(text, str)
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


class SysStream:
    def __init__(self, output_type, output_buffer):
        self.type = output_type
        self.output_buffer = output_buffer

    def __getattr__(self, item):
        return getattr(sys.__stdout__, item)

    def write(self, s):
        self.output_buffer.put(self.type, s)

    def flush(self):
        # TODO does `print` always flush? should there be an extra layer here?
        self.output_buffer.flush()


class Runner:
    def __init__(
        self,
        callback,
        *,
        extra_locals=None,
        format_syntax_error=None,
        filename="my_program.py",
    ):
        self._callback = callback
        self.console = InteractiveConsole()
        # TODO make module object
        self.extra_locals = extra_locals = (extra_locals or {}) | {"__name__": "__main__", "__file__": filename}
        self.console.locals = dict(extra_locals)
        self.format_syntax_error = format_syntax_error
        self.filename = filename
        self.output_buffer = OutputBuffer(lambda parts: self.callback("output", parts=parts))
        self.run_type = None

    def callback(self, event_type, **data):
        if event_type != "output":
            self.output_buffer.flush()

        return self._callback(event_type, data)

    def execute(self, code_obj, source_code, run_type=None):
        try:
            exec(code_obj, self.console.locals)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.output_buffer.put("traceback", **self.serialize_traceback(e, source_code))

    def serialize_traceback(self, exc, source_code):
        return {"text": format_traceback_string(exc)}

    def run(self, run_type, source_code):
        sys.stdin.readline = self.readline
        builtins.input = self.input
        with (
            redirect_stdout(SysStream("stdout", self.output_buffer)),  # noqa
            redirect_stderr(SysStream("stderr", self.output_buffer)),  # noqa
        ):
            try:
                result = self.inner_run(run_type, source_code)
            except KeyboardInterrupt:
                result = {"interrupted": True}
        self.output_buffer.flush()
        return result

    def inner_run(self, run_type, source_code):
        if run_type == "shell":
            mode = "single"
            source_code += "\n"  # Allow compiling single-line compound statements
        else:
            mode = "exec"
            self.console.locals = dict(self.extra_locals)
            self.output_buffer.reset()

        filename = self.filename
        linecache.cache[filename] = (
            len(source_code),
            0,
            [line + "\n" for line in source_code.splitlines()],
            filename,
        )

        try:
            code_obj = compile(source_code, filename, mode)
        except SyntaxError as e:
            try:
                if not ast.parse(source_code).body:
                    # Code is only comments, which cannot be compiled in 'single' mode
                    return {}
            except SyntaxError:
                pass

            self.output_buffer.put("syntax_error", self.format_syntax_error(e))
            return {}

        return self.execute(code_obj, source_code, run_type)

    def readline(self):
        # TODO copy papyros readline?
        result = self.callback("input")
        if not isinstance(result, str):
            while True:
                pass  # wait for the interrupt
        self.output_buffer.put("input", result)
        return result

    def input(self, prompt=""):
        self.output_buffer.put("input_prompt", prompt)
        return sys.stdin.readline().rstrip("\n")
