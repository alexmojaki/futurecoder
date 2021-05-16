from birdseye.bird import BirdsEye

from .worker import console, execute


def exec_birdseye(filename, code):
    eye = BirdsEye()
    traced_file = eye.trace_string_deep(filename, code)
    console.locals.update(eye._trace_methods_dict(traced_file))
    traceback_info = execute(traced_file.code)
    return traceback_info, dict(call_id=eye._last_call_id, store=eye.store)
