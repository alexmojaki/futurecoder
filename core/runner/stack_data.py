import logging
from typing import Union, Iterable

import pygments
from cheap_repr import cheap_repr
from pygments.lexers import get_lexer_by_name
from stack_data import (
    Formatter,
    FrameInfo,
    RepeatedFrames,
    Serializer,
    Options,
)

from core.runner.didyoumean import didyoumean_suggestions
from core.runner.friendly_traceback import friendly_message
from core.runner.utils import is_valid_syntax

log = logging.getLogger(__name__)
lexer = get_lexer_by_name("python3")


class TracebackSerializer(Serializer):
    filename = None

    def format_traceback_part(self, e: BaseException) -> dict:
        return dict(
            **super().format_traceback_part(e),
            didyoumean=didyoumean_suggestions(e),
            friendly=friendly_message(e, double_newline=True),
        )

    def format_line(self, line):
        result = super().format_line(line)
        result["content"] = result.pop("text")
        return result

    def format_variable_value(self, value) -> str:
        return cheap_repr(value)

    def should_include_frame(self, frame_info: FrameInfo) -> bool:
        return self.filename == frame_info.filename

    def format_variable_part(self, text):
        if is_valid_syntax(text):
            return pygments.highlight(text, lexer, self.options.pygments_formatter)
        else:
            return super().format_variable_part(text)


serializer = TracebackSerializer(
    options=Options(before=0, after=0),
    pygmented=True,
    pygments_formatter_kwargs=dict(nowrap=True),
    html=True,
    show_variables=True,
)


class TracebackFormatter(Formatter):
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


formatter = TracebackFormatter(
    options=Options(before=1, after=0),
    show_variables=True,
)


def format_traceback_stack_data(e):
    return "".join(formatter.format_exception(e))
