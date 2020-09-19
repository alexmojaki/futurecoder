import ast
import functools
import os
import re
import sys
import threading
import traceback
import xml.etree.ElementTree as etree
from functools import lru_cache, partial
from html import unescape
from io import StringIO
from textwrap import dedent

import pygments
import stack_data
from littleutils import strip_required_prefix, strip_required_suffix, withattrs
from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

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


class HighlightPythonExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(HighlightPythonTreeProcessor(), "highlight_python", 0)


def is_valid_syntax(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


class HighlightPythonTreeProcessor(Treeprocessor):
    def run(self, root):
        for node in root.findall(".//pre/code"):
            text = unescape(node.text)

            prefix = "__copyable__\n"
            if copyable := text.startswith(prefix):
                text = strip_required_prefix(text, prefix)

            if (
                    is_valid_syntax(text) or
                    is_valid_syntax(text + "\n 0") or
                    is_valid_syntax(dedent(text))
            ):
                self.highlight_node(node, text)

            if copyable:
                node.append(etree.fromstring('<button class="btn btn-primary">Copy</button>'))
                node.set("class", node.get("class") + " copyable")

    @staticmethod
    def highlight_node(node, text):
        highlighted = pygments.highlight(text, lexer, html_formatter)
        tail = node.tail
        node.clear()
        node.set("class", "codehilite")
        node.append(etree.fromstring(f"<span>{highlighted}</span>"))
        node.tail = tail


def highlighted_markdown(text):
    return markdown(text, extensions=[HighlightPythonExtension()])
