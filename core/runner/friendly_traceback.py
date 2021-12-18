from friendly_traceback.core import FriendlyTraceback

from core.basic_runner.utils import format_traceback_list


def friendly_syntax_error(e, filename):
    lines = iter(format_traceback_list(e))
    for line in lines:
        if line.strip().startswith(f'File "{filename}"'):
            break
    return f"""\
{''.join(lines).rstrip()}
at line {e.lineno}

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
