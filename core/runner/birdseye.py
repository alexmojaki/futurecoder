from birdseye.bird import BirdsEye


def exec_birdseye(runner, code):
    eye = BirdsEye()
    traced_file = eye.trace_string_deep(runner.filename, code)
    runner.console.locals.update(eye._trace_methods_dict(traced_file))
    runner.execute(traced_file.code)
    return dict(call_id=eye._last_call_id, store=eye.store)
