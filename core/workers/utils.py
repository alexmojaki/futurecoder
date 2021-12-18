import functools
import os
import traceback

from core.runner.utils import truncate_string

TESTING = False

def get_exception_event():
    import sentry_sdk

    os.environ["SENTRY_RELEASE"] = "stubbed"  # TODO get git commit?

    event = {}

    def transport(e):
        nonlocal event
        event = e

    client = sentry_sdk.Client(transport=transport)
    hub = sentry_sdk.Hub(client)
    hub.capture_exception()

    assert event
    return event


def safe_traceback(e: Exception):
    import stack_data

    try:
        return "".join(
            stack_data.Formatter(show_variables=True, chain=True).format_exception(e)
        )
    except Exception:
        pass
    try:
        return "".join(
            stack_data.Formatter(show_variables=False, chain=True).format_exception(e)
        )
    except Exception:
        pass
    try:
        return "".join(
            stack_data.Formatter(show_variables=True, chain=False).format_exception(e)
        )
    except Exception:
        pass
    try:
        return "".join(
            stack_data.Formatter(show_variables=False, chain=False).format_exception(e)
        )
    except Exception:
        return "".join(traceback.format_exception(type(e), e, e.__traceback__))


def internal_error_result(e: Exception):
    exception_string = "".join(traceback.format_exception_only(type(e), e))

    return dict(
        error=dict(
            details=safe_traceback(e),
            title=f"Internal error: {truncate_string(exception_string, 100)}",
            sentry_event=get_exception_event(),
        ),
    )


def catch_internal_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if TESTING:
                raise
            return internal_error_result(e)
    return wrapper
