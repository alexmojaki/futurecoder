import html
import logging
import sys
import traceback
from collections import Counter
from typing import Union, Iterable, List

import stack_data
from cheap_repr import cheap_repr
from stack_data import (
    Options,
    Line,
    FrameInfo,
    Variable,
    RepeatedFrames,
)

from core.runner.didyoumean import didyoumean_suggestions
from core.runner.friendly_traceback import friendly_message

log = logging.getLogger(__name__)


class TracebackSerializer:
    pygments_formatter = None
    filename = None

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
                frames=self.format_stack(e.__traceback__ or sys.exc_info()[2]),
                exception=dict(
                    type=type(e).__name__,
                    message=traceback._some_str(e),
                ),
                tail="",
                didyoumean=didyoumean_suggestions(e),
                friendly=friendly_message(e, double_newline=True),
            )
        )
        return result

    def format_stack(self, frame_or_tb) -> List[dict]:
        return list(
            self.format_stack_data(
                FrameInfo.stack_data(
                    frame_or_tb,
                    Options(
                        before=0, after=0, pygments_formatter=self.pygments_formatter
                    ),
                    collapse_repeated_frames=True,
                )
            )
        )

    def format_stack_data(
        self, stack: Iterable[Union[FrameInfo, RepeatedFrames]]
    ) -> Iterable[dict]:
        for item in stack:
            if isinstance(item, FrameInfo):
                if item.filename != self.filename:
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
                pygmented=bool(self.pygments_formatter),
                escape_html=True,
                strip_leading_indent=True,
            ),
        )

    def format_variables(self, frame_info: FrameInfo) -> Iterable[str]:
        try:
            for var in sorted(frame_info.variables, key=lambda v: v.name):
                yield self.format_variable(var)
        except Exception:
            log.exception("Error in getting frame variables")
            return []

    def format_variable(self, var: Variable) -> dict:
        return dict(
            name=self.format_variable_part(var.name),
            value=self.format_variable_part(cheap_repr(var.value)),
        )

    def format_variable_part(self, text):
        return html.escape(text)


class TracebackFormatter(stack_data.Formatter):
    def format_stack_data(
        self, stack: Iterable[Union[FrameInfo, RepeatedFrames]]
    ) -> Iterable[str]:
        from core.runner.snoop import snoop

        for item in stack:
            if isinstance(item, FrameInfo):
                if item.filename.startswith(snoop.tracer.internal_directories):
                    continue
                yield from self.format_frame(item)
            else:
                yield self.format_repeated_frames(item)
            yield '\n'

    def format_variable_value(self, value) -> str:
        return cheap_repr(value)


def format_traceback_stack_data(e):
    return "".join(
        TracebackFormatter(
            options=stack_data.Options(before=1, after=0),
            show_variables=True,
        ).format_exception(e)
    )
