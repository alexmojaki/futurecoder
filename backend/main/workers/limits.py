import inspect
import linecache
import os
import sys
from functools import lru_cache
from importlib import import_module
import friendly.runtime_errors
import friendly.syntax_errors
from main.workers.tracebacks import TracebackSerializer
from main.workers.utils import import_submodules


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

    patch_cwd()

    # Trigger imports before limiting access to files
    from main.workers import birdseye, snoop  # noqa
    import_submodules(friendly.runtime_errors)
    import_submodules(friendly.syntax_errors)

    for bad_code in ["nameerror", "syntax error", "1 + '2'", "list.set", "[][0]", "{}[0]"]:
        try:
            eval(bad_code)  # noqa
        except Exception as e:
            TracebackSerializer().format_exception(e)

    # Put some modules in linecache so that tracebacks work
    for name, mod in list(sys.modules.items()):
        try:
            if name.startswith(
                (
                    "main",
                    "birdseye",
                    "snoop",
                    "friendly",
                    "executing",
                    "pure_eval",
                    "stack_data",
                    "asttokens",
                )
            ):
                linecache.getlines(mod.__file__, mod.__dict__)
        except Exception:
            pass

    print(f"Size of linecache: {sys.getsizeof(linecache.cache)}")

    usage = resource.getrusage(resource.RUSAGE_SELF)

    # TODO tests can exceed this time since the process is not restarted, causing failure
    max_time = int(usage.ru_utime + usage.ru_stime) + 2
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (max_time, max_time))
    except ValueError:
        pass

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
