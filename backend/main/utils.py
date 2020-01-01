import functools
from io import StringIO
import re
import sys

from littleutils import withattrs


def assign(**attrs):
    def decorator(f):
        return withattrs(f, **attrs)

    return decorator


def no_weird_whitespace(string):
    spaces = set(re.findall(r"\s", string))
    assert spaces <= {" ", "\n"}, spaces


def returns_stdout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        original = sys.stdout
        sys.stdout = result = StringIO()
        try:
            func(*args, **kwargs)
            return result.getvalue()
        finally:
            sys.stdout = original

    wrapper.returns_stdout = True
    return wrapper
