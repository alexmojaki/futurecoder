import functools
import os
import re
import sys
import threading
import traceback
from functools import lru_cache
from io import StringIO

import stack_data
from littleutils import strip_required_prefix, strip_required_suffix, withattrs
from markdown import markdown
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

get_lexer_by_name("python3")
get_style_by_name("monokai")
str(HtmlFormatter)

internal_dir = os.path.dirname(os.path.dirname(
    (lambda: 0).__code__.co_filename
))


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


def snake(camel_string):
    return re.sub(r'([a-z0-9])([A-Z])',
                  lambda m: (m.group(1).lower() + '_' +
                             m.group(2).lower()),
                  camel_string).lower()


assert snake('fooBar') == snake('FooBar') == 'foo_bar'


def unwrapped_markdown(s):
    s = markdown(s)
    s = strip_required_prefix(s, "<p>")
    s = strip_required_suffix(s, "</p>")
    return s


def format_exception_string():
    return ''.join(traceback.format_exception_only(*sys.exc_info()[:2]))


class Formatter(stack_data.Formatter):
    def format_frame(self, frame):
        if frame.filename.startswith(internal_dir):
            return
        yield from super().format_frame(frame)


formatter = Formatter(
    options=stack_data.Options(before=0, after=0),
    pygmented=True,
    show_executing_node=True,
)


def print_exception():
    formatter.print_exception()


def row_to_dict(row):
    d = row.__dict__.copy()
    del d["_sa_instance_state"]
    return d


def rows_to_dicts(rows):
    return [row_to_dict(row) for row in rows]


def thread_separate_lru_cache(*cache_args, **cache_kwargs):
    def decorator(func):
        @lru_cache(*cache_args, **cache_kwargs)
        def cached(_thread_id, *args, **kwargs):
            return func(*args, **kwargs)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cached(threading.get_ident(), *args, **kwargs)

        return wrapper

    return decorator
