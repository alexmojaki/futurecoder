from core import translation as t
from core.text import load_chapters


def init(lang):
    if lang and lang != "en":
        t.set_language(lang)

    list(load_chapters())
