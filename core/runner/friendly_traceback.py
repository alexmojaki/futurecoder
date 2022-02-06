import sys
import traceback

from core import translation as t

for attr in "type value traceback".split():
    sys.__dict__.pop("last_" + attr, None)

from friendly_traceback.core import FriendlyTraceback


def friendly_syntax_error(e, filename):
    lines = iter(traceback.format_exception(type(e), e, e.__traceback__))
    for line in lines:
        if line.strip().startswith(f'File "{filename}"'):
            break
    return f"""\
{''.join(lines).rstrip()}
{t.Terms.syntax_error_at_line} {e.lineno}

{friendly_message(e, double_newline=False)}

"""


def friendly_message(e, double_newline: bool):
    try:
        fr = FriendlyTraceback(type(e), e, e.__traceback__)
        fr.assign_generic()
        fr.assign_cause()

        return fr.info["generic"] + "\n" + double_newline * "\n" + fr.info.get("cause", "")
    except (Exception, SystemExit):
        # log.exception("Failed to build friendly message")
        return ""
