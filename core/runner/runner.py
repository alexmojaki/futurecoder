import stack_data

from core.basic_runner.runner import Runner


class EnhancedRunner(Runner):
    def execute(self, code_obj, source_code, run_type=None):
        stack_data.Source._class_local("__source_cache", {}).pop(self.filename, None)

        result = {}
        if run_type == "snoop":
            from core.runner.snoop import exec_snoop

            exec_snoop(self, source_code, code_obj)
        elif run_type == "birdseye":
            from core.runner.birdseye import exec_birdseye

            result["birdseye_objects"] = exec_birdseye(self, source_code)
        else:
            super().execute(code_obj, source_code)

        return result

    def serialize_traceback(self, exc, source_code):
        import friendly_traceback.source_cache
        from .stack_data import format_traceback_stack_data
        from .stack_data_pygments import PygmentsTracebackSerializer

        friendly_traceback.source_cache.cache.add(self.filename, source_code)

        serializer = PygmentsTracebackSerializer()
        serializer.filename = self.filename

        return {
            "text": format_traceback_stack_data(exc),
            "data": serializer.format_exception(exc),
        }
