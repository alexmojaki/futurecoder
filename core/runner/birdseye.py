from birdseye.bird import BirdsEye


def exec_birdseye(runner):
    code = runner.source_code
    eye = BirdsEye()
    traced_file = eye.trace_string_deep(runner.filename, code)
    runner.console.locals.update(eye._trace_methods_dict(traced_file))
    try:
        runner.execute(traced_file.code, code)
    finally:
        runner.birdseye_objects = dict(call_id=eye._last_call_id, store=eye.store)
