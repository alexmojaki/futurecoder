import ast
import functools
import os
import re
import sys
import threading
import traceback
from functools import lru_cache, partial
from io import StringIO
from itertools import combinations
from random import shuffle
from types import ModuleType

import pygments
from littleutils import strip_required_prefix, strip_required_suffix, withattrs
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

site_packages = strip_required_suffix(pygments.__file__, f"pygments{os.path.sep}__init__.py")
sys.path.append(site_packages + "didyoumean")

from didyoumean.didyoumean_internal import get_suggestions_for_exception  # noqa

def stub_module(name):
    assert name not in sys.modules
    sys.modules[name] = ModuleType(name)

stub_module("urllib3")
stub_module("certifi")
stub_module("friendly.theme.friendly_rich")

import friendly.source_cache  # noqa
import friendly.core  # noqa

lexer = get_lexer_by_name("python3")
monokai = get_style_by_name("monokai")
html_formatter = HtmlFormatter(nowrap=True)

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
    if getattr(func, "returns_stdout", False):
        return func

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
    if isinstance(func, NoMethodWrapper):
        return NoMethodWrapper(wrapper)
    else:
        return wrapper


class NoMethodWrapper:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def bind_self(func):
    if isinstance(func, NoMethodWrapper):
        return func
    else:
        return partial(func, None)


def snake(camel_string):
    return re.sub(r'([a-z0-9])([A-Z])',
                  lambda m: (m.group(1).lower() + '_' +
                             m.group(2).lower()),
                  camel_string).lower()


assert snake('fooBar') == snake('FooBar') == 'foo_bar'


def unwrapped_markdown(s):
    s = highlighted_markdown(s)
    s = strip_required_prefix(s, "<p>")
    s = strip_required_suffix(s, "</p>")
    return s


def format_exception_string():
    return ''.join(traceback.format_exception_only(*sys.exc_info()[:2]))


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


def is_valid_syntax(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def highlighted_markdown(text):
    from markdown import markdown
    from .markdown_extensions import HighlightPythonExtension

    return markdown(text, extensions=[HighlightPythonExtension(), 'markdown.extensions.tables'])


def shuffled(it):
    result = list(it)
    shuffle(result)
    return result


def shuffled_well(seq):
    original = range(len(seq))
    permutations = {
        tuple(shuffled(original))
        for _ in range(10)
    }

    def inversions(perm):
        return sum(
            perm[i] > perm[j]
            for i, j in combinations(original, 2)
        )

    permutation = sorted(permutations, key=inversions)[-2]
    return [seq[i] for i in permutation]
