import ast
import os

import executing
from littleutils import strip_required_suffix

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
