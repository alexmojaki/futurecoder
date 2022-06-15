import traceback

from python_runner import PyodideRunner

import core.translation as t


class EnhancedRunner(PyodideRunner):
    def execute(self, code_obj, mode=None, snoop_config=None):
        if mode == "birdseye":
            from core.runner.birdseye import exec_birdseye

            exec_birdseye(self)
        else:
            super().execute(code_obj, mode=mode, snoop_config={"color": True})

    def serialize_traceback(self, exc):
        if isinstance(exc, KeyboardInterrupt):
            raise

        from .stack_data import format_traceback_stack_data, serializer
        import friendly_traceback.source_cache

        friendly_traceback.source_cache.cache.add(self.filename, self.source_code)

        serializer.filename = self.filename

        return {
            "text": format_traceback_stack_data(exc),
            "data": serializer.format_exception(exc),
        }

    def serialize_syntax_error(self, e):
        from core.runner.friendly_traceback import friendly_message

        lines = iter(traceback.format_exception(type(e), e, e.__traceback__))
        for line in lines:
            if line.strip().startswith(f'File "{self.filename}"'):
                break
        text = f"""\
{''.join(lines).rstrip()}
{t.Terms.syntax_error_at_line} {e.lineno}
"""

        return {
            "text": text,
            "friendly": friendly_message(e, double_newline=False)
        }
