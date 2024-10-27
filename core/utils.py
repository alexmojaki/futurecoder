import builtins
import functools
import os
import re
import sys
import traceback
from io import StringIO
from itertools import combinations
from random import shuffle
from textwrap import dedent
from tokenize import generate_tokens, TokenError
from types import ModuleType
from typing import Union

import asttokens
from littleutils import strip_required_prefix, strip_required_suffix
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from core import translation as t

TESTING = False


def qa_error(message, cls=AssertionError):
    if os.environ.get("PRINT_ERRORS"):
        print(message)
        print("\n-----------------------------------------------------\n")
    else:
        raise cls(message)


def stub_module(name):
    sys.modules[name] = ModuleType(name)


assert "selenium" in sys.modules or not ("urllib3" in sys.modules or "certifi" in sys.modules)
stub_module("urllib3")
stub_module("certifi")

lexer = get_lexer_by_name("python3")
monokai = get_style_by_name("monokai")
html_formatter = HtmlFormatter(nowrap=True)

internal_dir = os.path.dirname(os.path.dirname(
    (lambda: 0).__code__.co_filename
))


def clean_spaces(string):
    if isinstance(string, list):
        string = "\n".join(string)
    string = dedent(string).strip()
    spaces = set(re.findall(r"\s", string))
    assert spaces <= {" ", "\n"}, (spaces, string)
    # In translation, special codes like `__copyable__` often get the wrong indentation.
    # They must be preceded by 0 or 4 spaces.
    if re.search(r"^( {1,3}| {5,})_", string, re.MULTILINE):
        qa_error("Incorrect indentation of code:\n" + string)
    return string


def returns_stdout(func):
    if getattr(func, "returns_stdout", False):
        return func

    @wrap_solution(func)
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


class NoMethodWrapper:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def match(cls, source, target):
        if isinstance(source, cls):
            return cls(target)
        else:
            return target


def wrap_solution(func):
    def decorator(wrapper):
        wrapper = functools.wraps(func)(wrapper)
        wrapper = NoMethodWrapper.match(func, wrapper)
        return wrapper

    return decorator


def make_test_input_callback(stdin_input: Union[str, list]):
    if isinstance(stdin_input, str):
        stdin_input = stdin_input.splitlines()
    assert isinstance(stdin_input, list), repr(stdin_input)
    assert not any("\n" in s for s in stdin_input), repr(stdin_input)

    stdin_input = stdin_input[::-1]

    def input_callback(_data=None):
        if stdin_input:
            result = stdin_input.pop()
            print(f"<input: {result}>")
            return result
        else:
            raise ValueError(t.Terms.no_more_test_inputs)

    return input_callback


def add_stdin_input_arg(func):
    @wrap_solution(func)
    def wrapper(stdin_input="", **kwargs):
        # TODO also deal with sys.stdin directly,
        #   especially breakpoint()

        input_callback = make_test_input_callback(stdin_input)

        def patched_input(prompt=""):
            print(prompt, end="")
            return input_callback()

        builtins.input = patched_input

        return func(**kwargs)

    return NoMethodWrapper.match(func, wrapper)


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


def highlighted_markdown_and_codes(text):
    from markdown import markdown
    from .markdown_extensions import HighlightPythonExtension

    extension = HighlightPythonExtension()
    extension.codes = []
    return markdown(text, extensions=[extension, 'markdown.extensions.tables']), extension.codes


def highlighted_markdown(text):
    result = highlighted_markdown_and_codes(text)[0]
    if "__copyable__" in result or "__no_auto_translate__" in result:
        qa_error(f"Markdown contains __copyable__ or __no_auto_translate__:\n{result}")
    return result


def markdown_codes(text):
    return highlighted_markdown_and_codes(text)[1]


def new_tab_links(s):
    return s.replace("<a href=", '<a target="_blank" rel="noreferrer" href=')


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


def check_and_remove_prefix(string, prefix):
    if startswith := string.startswith(prefix):
        string = strip_required_prefix(string, prefix)
    if prefix in string:
        qa_error(f"String still contains {prefix!r}: {string!r}")
    return string, startswith


def get_exception_event():
    import sentry_sdk
    from sentry_sdk.integrations.pure_eval import PureEvalIntegration
    from sentry_sdk.integrations.executing import ExecutingIntegration

    os.environ["SENTRY_RELEASE"] = "stubbed"  # TODO get git commit?

    event = {}

    def transport(e):
        nonlocal event
        event = e

    sentry_sdk.init(
        transport=transport,
        integrations=[PureEvalIntegration(), ExecutingIntegration()],
    )
    sentry_sdk.capture_exception()

    assert event

    # https://github.com/getsentry/sentry-python/issues/1536
    breadcrumbs = event.get("breadcrumbs", {})
    if isinstance(breadcrumbs, dict):
        event["breadcrumbs"] = breadcrumbs.get("values", [])

    return event


def truncate(seq, max_length, middle):
    if len(seq) > max_length:
        left = (max_length - len(middle)) // 2
        right = max_length - len(middle) - left
        seq = seq[:left] + middle + seq[-right:]
    return seq


def truncate_string(string, max_length):
    return truncate(string, max_length, "...")


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
            title=f"{truncate_string(exception_string, 100)}",
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


def token_text_range(token_info, linenos):
    tok_type, tok_str, start, end, line = token_info
    return (
        linenos.line_to_offset(*start),
        linenos.line_to_offset(*end),
    )


def split_into_tokens_gen(s):
    linenos = asttokens.LineNumbers(s)
    try:
        tokens = list(generate_tokens(StringIO(s).readline))
    except (SyntaxError, TokenError):
        yield from s
        return
    for t1, t2 in zip(tokens, tokens[1:]):
        start1, end1 = token_text_range(t1, linenos)
        start2, end2 = token_text_range(t2, linenos)
        end1 = min(end1, start2)  # workaround a specific unicode bug in 3.12.1
        assert start1 <= end1 <= start2 <= end2
        yield s[start1:end1]
        yield s[end1:start2]
    start, end = token_text_range(tokens[-1], linenos)
    yield s[start:end]
    yield s[end:]


def split_into_tokens(s):
    nonempty = filter(None, split_into_tokens_gen(s))
    result = list(nonempty)
    assert "".join(result) == s
    return result
