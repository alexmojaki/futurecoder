import ast
import os
import executing


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

site_packages = strip_required_suffix(
    executing.__file__, f"executing{os.path.sep}__init__.py"
)

def truncate(seq, max_length, middle):
    if len(seq) > max_length:
        left = (max_length - len(middle)) // 2
        right = max_length - len(middle) - left
        seq = seq[:left] + middle + seq[-right:]
    return seq


def truncate_string(string, max_length):
    return truncate(string, max_length, "...")


def is_valid_syntax(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False
