from python_runner import PatchedStdinRunner, PatchedSleepRunner


class EnhancedRunner(PatchedStdinRunner, PatchedSleepRunner):
    def execute(self, code_obj, source_code, mode=None):
        if mode == "snoop":
            from core.runner.snoop import exec_snoop

            exec_snoop(self, source_code, code_obj)
        elif mode == "birdseye":
            from core.runner.birdseye import exec_birdseye

            exec_birdseye(self, source_code)
        else:
            super().execute(code_obj, source_code)

    def set_combined_callbacks(self, **callbacks):
        def callback(event_type, data):
            return callbacks[event_type](data)

        self.set_callback(callback)

    def serialize_traceback(self, exc, source_code):
        from .stack_data import format_traceback_stack_data
        from .stack_data_pygments import PygmentsTracebackSerializer
        import friendly_traceback.source_cache

        friendly_traceback.source_cache.cache.add(self.filename, source_code)

        serializer = PygmentsTracebackSerializer()
        serializer.filename = self.filename

        return {
            "text": format_traceback_stack_data(exc),
            "data": serializer.format_exception(exc),
        }

    def serialize_syntax_error(self, exc, source_code):
        from core.runner.friendly_traceback import friendly_syntax_error

        return {
            "text": friendly_syntax_error(exc, self.filename),
        }
