import ast
import os
import traceback


def strip_required_suffix(string, suffix):
    """
    >>> strip_required_suffix('abcdef', 'def')
    'abc'
    >>> strip_required_suffix('abcdef', '123')
    Traceback (most recent call last):
    ...
    AssertionError: String ends with 'def', not '123'
    """
    if string.endswith(suffix):
        return string[: -len(suffix)]
    raise AssertionError(
        "String ends with %r, not %r" % (string[-len(suffix):], suffix)
    )


def truncate(seq, max_length, middle):
    if len(seq) > max_length:
        left = (max_length - len(middle)) // 2
        right = max_length - len(middle) - left
        seq = seq[:left] + middle + seq[-right:]
    return seq


def truncate_string(string, max_length):
    return truncate(string, max_length, "...")


def get_site_packages_path(module):
    return strip_required_suffix(
        module.__file__, f"{module.__name__}{os.path.sep}__init__.py"
    )


def is_valid_syntax(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def format_traceback_string(e: Exception):
    return "".join(format_traceback_list(e))


def format_traceback_list(e: Exception):
    return traceback.format_exception(type(e), e, e.__traceback__)
