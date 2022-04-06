from python_runner import PyodideRunner


class EnhancedRunner(PyodideRunner):
    def execute(self, code_obj, mode=None):
        if mode == "snoop":
            from core.runner.snoop import exec_snoop

            exec_snoop(self, code_obj)
        elif mode == "birdseye":
            from core.runner.birdseye import exec_birdseye

            exec_birdseye(self)
        else:
            super().execute(code_obj)

    def serialize_traceback(self, exc):
        if isinstance(exc, KeyboardInterrupt):
            raise

        from .stack_data import format_traceback_stack_data
        from .stack_data_pygments import PygmentsTracebackSerializer
        import friendly_traceback.source_cache

        friendly_traceback.source_cache.cache.add(self.filename, self.source_code)

        serializer = PygmentsTracebackSerializer()
        serializer.filename = self.filename

        return {
            "text": format_traceback_stack_data(exc),
            "data": serializer.format_exception(exc),
        }

    def serialize_syntax_error(self, exc):
        from core.runner.friendly_traceback import friendly_syntax_error

        return {
            "text": friendly_syntax_error(exc, self.filename),
        }
