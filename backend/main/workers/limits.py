import inspect
import os
from functools import lru_cache
from importlib import import_module

from main.utils import get_suggestions_for_exception


def patch_cwd():
    """
    os.getcwd() requires opening a file, which fails under the limits,
    so this removes the need for that.
    """

    cwd = os.getcwd()

    def chdir(d):
        nonlocal cwd
        cwd = d

    def getcwd():
        return cwd

    os.getcwd = getcwd
    os.chdir = chdir


def set_limits():
    import resource
    destroy_dangerous_functions()

    usage = resource.getrusage(resource.RUSAGE_SELF)

    # TODO tests can exceed this time since the process is not restarted, causing failure
    max_time = int(usage.ru_utime + usage.ru_stime) + 2
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (max_time, max_time))
    except ValueError:
        pass

    patch_cwd()

    # Trigger imports before limiting access to files
    from main.workers import birdseye, snoop  # noqa
    from friendly_traceback.runtime_errors import (  # noqa
        type_error,
        attribute_error,
        stdlib,
    )
    from friendly_traceback.syntax_errors import (  # noqa
        analyze_syntax,
        line_analyzer,
        message_analyzer,
        source_analyzer,
    )

    try:
        sdfsdfsdfsd  # noqa
    except NameError as e:
        list(get_suggestions_for_exception(e, e.__traceback__))

    resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))


@lru_cache
def destroy_dangerous_functions():
    import gc
    import signal

    del signal.sigwait.__doc__

    bad_module_names = "signal _signal ctypes _ctypes".split()

    get_referrers = gc.get_referrers

    funcs = {
        get_referrers,
        gc.get_referents,
        gc.get_objects,
        os.system,
        *[v for k, v in os.__dict__.items() if k.startswith("exec")],
    }

    for module_name in bad_module_names:
        module = import_module(module_name)
        funcs.update(
            value for value in module.__dict__.values()
            if inspect.isroutine(value)
            if getattr(value, "__module__", None) in bad_module_names
        )
        module.__dict__.clear()

    for func in list(funcs):
        funcs.remove(func)
        for ref in get_referrers(func):
            if isinstance(ref, dict):
                for key in list(ref):
                    if ref[key] == func:
                        del ref[key]

            if isinstance(ref, (list, set)):
                while func in ref:
                    ref.remove(func)

        assert not get_referrers(func)
