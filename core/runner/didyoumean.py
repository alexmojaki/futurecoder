import sys
from typing import List

from core.runner.utils import site_packages

sys.path.append(site_packages + "didyoumean")

from didyoumean.didyoumean_internal import get_suggestions_for_exception


def didyoumean_suggestions(e) -> List[str]:
    if "maximum recursion depth exceeded" in str(e):
        return []
    try:
        return list(get_suggestions_for_exception(e, e.__traceback__))
    except Exception:
        # log.exception("Failed to get didyoumean suggestions")
        return []
