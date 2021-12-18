import traceback


def format_traceback_string(e: Exception):
    return "".join(format_traceback_list(e))


def format_traceback_list(e: Exception):
    return traceback.format_exception(type(e), e, e.__traceback__)
