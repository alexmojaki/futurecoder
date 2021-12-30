import ast
import os

import executing
from littleutils import strip_required_suffix

site_packages = strip_required_suffix(
    executing.__file__, f"executing{os.path.sep}__init__.py"
)


def is_valid_syntax(text):
    try:
        ast.parse(text)
        return True
    except Exception:
        return False
