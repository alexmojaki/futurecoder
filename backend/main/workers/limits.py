import inspect
import os
import resource
from functools import lru_cache
from importlib import import_module


def set_limits():
    destroy_dangerous_functions()

    usage = resource.getrusage(resource.RUSAGE_SELF)

    # TODO tests can exceed this time since the process is not restarted, causing failure
    max_time = int(usage.ru_utime + usage.ru_stime) + 2
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (max_time, max_time))
    except ValueError:
        pass

    from main.workers import snoop, birdseye
    str([snoop, birdseye])

    resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))


@lru_cache
def destroy_dangerous_functions():
    import signal
    import gc

    del signal.sigwait.__doc__

    bad_module_names = "signal _signal".split()

    func = None
    get_referrers = gc.get_referrers

    funcs = [get_referrers, gc.get_referents, gc.get_objects, os.system]
    expected_refs = [locals(), funcs]

    for module_name in bad_module_names:
        module = import_module(module_name)
        funcs += [
            value for value in module.__dict__.values()
            if inspect.isroutine(value)
            if getattr(value, "__module__", None) in bad_module_names
        ]

    for func in funcs:
        for ref in get_referrers(func):
            if ref in expected_refs:
                continue

            if isinstance(ref, dict):
                for key in list(ref):
                    if ref[key] == func:
                        del ref[key]

            if isinstance(ref, list):
                while func in ref:
                    ref.remove(func)

        for ref in get_referrers(func):
            assert ref in expected_refs
