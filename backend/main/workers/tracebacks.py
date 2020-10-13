import json
import logging
import traceback
from collections import Counter
from typing import Union, Iterable, List

import pygments
from cheap_repr import cheap_repr
from friendly_traceback.core import get_generic_explanation
from friendly_traceback.info_specific import get_likely_cause
from markdown import markdown
from pygments.formatters.html import HtmlFormatter
from stack_data import (
    style_with_executing_node,
    Options,
    Line,
    FrameInfo,
    Variable,
    RepeatedFrames,
)

from main.utils import is_valid_syntax, lexer, get_suggestions_for_exception

pygments_style = style_with_executing_node("monokai", "bg:#005080")
pygments_formatter = HtmlFormatter(
    style=pygments_style,
    nowrap=True,
)

log = logging.getLogger(__name__)


def didyoumean_suggestions(e) -> List[str]:
    if "maximum recursion depth exceeded" in str(e):
        return []
    try:
        return list(get_suggestions_for_exception(e, e.__traceback__))
    except Exception:
        log.exception("Failed to get didyoumean suggestions")
        return []


def friendly_traceback_info(e):
    etype = type(e)
    try:
        generic = get_generic_explanation(etype.__name__, etype, e)
    except Exception:
        log.exception("Failed to get generic friendly explanation")
        return ""

    info = {}
    frame = e.__traceback__.tb_frame
    try:
        get_likely_cause(etype, e, info, frame)
    except Exception:
        log.exception("Failed to get likely cause of exception")
        cause = ""
    else:
        cause = info.get("cause", "")

    return markdown(generic + "\n\n" + cause)


class TracebackSerializer:
    def format_exception(self, e) -> List[dict]:
        if e.__cause__ is not None:
            result = self.format_exception(e.__cause__)
            result[-1]["tail"] = traceback._cause_message
        elif e.__context__ is not None and not e.__suppress_context__:
            result = self.format_exception(e.__context__)
            result[-1]["tail"] = traceback._context_message
        else:
            result = []

        result.append(
            dict(
                frames=self.format_stack(e.__traceback__),
                exception=dict(
                    type=type(e).__name__,
                    message=traceback._some_str(e),
                ),
                tail="",
                didyoumean=didyoumean_suggestions(e),
                friendly=friendly_traceback_info(e),
            )
        )
        return result

    def format_stack(self, frame_or_tb) -> List[dict]:
        return list(
            self.format_stack_data(
                FrameInfo.stack_data(
                    frame_or_tb,
                    Options(before=0, after=0, pygments_formatter=pygments_formatter),
                    collapse_repeated_frames=True,
                )
            )
        )

    def format_stack_data(
        self, stack: Iterable[Union[FrameInfo, RepeatedFrames]]
    ) -> Iterable[dict]:
        for item in stack:
            if isinstance(item, FrameInfo):
                if item.filename != "my_program.py":
                    continue
                yield self.format_frame(item)
            else:
                yield dict(
                    type="repeated_frames", data=self.format_repeated_frames(item)
                )

    def format_repeated_frames(self, repeated_frames: RepeatedFrames) -> List[dict]:
        counts = sorted(
            Counter(repeated_frames.frame_keys).items(),
            key=lambda item: (-item[1], item[0][0].co_name),
        )
        return [
            dict(
                name=code.co_name,
                lineno=lineno,
                count=count,
            )
            for (code, lineno), count in counts
        ]

    def format_frame(self, frame: FrameInfo) -> dict:
        return dict(
            type="frame",
            name=frame.executing.code_qualname(),
            variables=list(self.format_variables(frame)),
            lines=list(self.format_lines(frame.lines)),
        )

    def format_lines(self, lines):
        for line in lines:
            if isinstance(line, Line):
                yield self.format_line(line)
            else:
                yield dict(type="line_gap")

    def format_line(self, line: Line) -> dict:
        return dict(
            type="line",
            is_current=line.is_current,
            lineno=line.lineno,
            content=line.render(
                pygmented=True,
                escape_html=True,
                strip_leading_indent=True,
            ),
        )

    def format_variables(self, frame_info: FrameInfo) -> Iterable[str]:
        for var in sorted(frame_info.variables, key=lambda v: v.name):
            yield self.format_variable(var)

    def format_variable(self, var: Variable) -> dict:
        return dict(
            name=maybe_highlight(var.name),
            value=maybe_highlight(cheap_repr(var.value)),
        )


def maybe_highlight(text):
    if is_valid_syntax(text):
        return pygments.highlight(text, lexer, pygments_formatter)
    else:
        return text


def test():
    def foo():
        print(1 / 0)

    try:
        foo()
    except Exception as e:
        print(json.dumps(TracebackSerializer().format_exception(e), indent=4))


if __name__ == "__main__":
    test()
