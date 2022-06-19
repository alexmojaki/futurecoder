import sys

from markdown import markdown

from core import translation as t

for attr in "type value traceback".split():
    sys.__dict__.pop("last_" + attr, None)

from friendly_traceback.core import FriendlyTraceback
import friendly_traceback

friendly_traceback.set_lang(t.current_language or "en")



def friendly_message(e, double_newline: bool):
    try:
        fr = FriendlyTraceback(type(e), e, e.__traceback__)
        fr.assign_generic()
        fr.assign_cause()

        return markdown(fr.info["generic"] + "\n" + double_newline * "\n" + fr.info.get("cause", ""))
    except (Exception, SystemExit):
        return ""
