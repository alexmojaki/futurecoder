import ast
import builtins
import linecache
import logging
import sys
from code import InteractiveConsole
from types import ModuleType

from .output import OutputBuffer
from .utils import format_traceback_string

log = logging.getLogger(__name__)


class Runner:
    OutputBufferClass = OutputBuffer

    def __init__(
        self,
        *,
        callback=None,
        extra_locals=None,
        filename="my_program.py",
    ):
        self.set_callback(callback)
        self.extra_locals = extra_locals or {}
        self.filename = filename

        self.line = ""
        self.console = InteractiveConsole()
        self.output_buffer = self.OutputBufferClass(
            lambda parts: self.callback("output", parts=parts)
        )

    def set_callback(self, callback):
        self._callback = callback

    def set_combined_callbacks(self, **callbacks):
        def callback(event_type, data):
            return callbacks[event_type](data)

        self.set_callback(callback)

    def callback(self, event_type, **data):
        if event_type != "output":
            self.output_buffer.flush()

        return self._callback(event_type, data)

    def output(self, output_type, text, **extra):
        return self.output_buffer.put(output_type, text, **extra)

    def execute(self, code_obj, source_code, run_type=None):
        try:
            exec(code_obj, self.console.locals)  # noqa
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.output("traceback", **self.serialize_traceback(e, source_code))

    def serialize_traceback(self, exc, source_code):
        return {"text": format_traceback_string(exc)}

    def serialize_syntax_error(self, exc, source_code):
        return self.serialize_traceback(exc, source_code)

    def run(self, run_type, source_code):
        sys.stdin.readline = self.readline
        builtins.input = self.input
        with self.output_buffer.redirect_std_streams():
            result = self.inner_run(run_type, source_code)
        self.output_buffer.flush()
        return result

    def inner_run(self, run_type, source_code):
        if run_type == "shell":
            mode = "single"
            source_code += "\n"  # Allow compiling single-line compound statements
        else:
            mode = "exec"
            mod = ModuleType("__main__")
            mod.__file__ = self.filename
            sys.modules["__main__"] = mod
            self.console.locals = mod.__dict__
            self.console.locals.update(self.extra_locals)
            self.output_buffer.reset()
            self.line = ""

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

            self.output("syntax_error", **self.serialize_syntax_error(e, source_code))
            return {}

        return self.execute(code_obj, source_code, run_type)

    def readline(self, n=-1, prompt=""):
        if not self.line and n:
            self.line = self.callback("input", prompt=prompt)
            if not isinstance(self.line, str):
                while True:
                    pass  # wait for the interrupt
            if not self.line.endswith("\n"):
                self.line += "\n"
            self.output("input", self.line)

        if n < 0 or n > len(self.line):
            n = len(self.line)
        to_return = self.line[:n]
        self.line = self.line[n:]
        return to_return

    def input(self, prompt=""):
        self.output("input_prompt", prompt)
        return sys.stdin.readline()[:-1]  # Remove trailing newline
