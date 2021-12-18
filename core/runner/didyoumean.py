import sys
from typing import List

from core.runner.utils import get_site_packages_path


def get_didyoumean_suggestions_func(site_package):
    sys.path.append(get_site_packages_path(site_package) + "didyoumean")
    try:
        from didyoumean.didyoumean_internal import get_suggestions_for_exception
    except ImportError:
        def get_suggestions_for_exception(*_):
            return []

    def didyoumean_suggestions(e) -> List[str]:
        if "maximum recursion depth exceeded" in str(e):
            return []
        try:
            return list(get_suggestions_for_exception(e, e.__traceback__))
        except Exception:
            # log.exception("Failed to get didyoumean suggestions")
            return []

    return didyoumean_suggestions
