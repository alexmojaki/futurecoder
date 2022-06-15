import logging
from typing import Union, Iterable

import stack_data
from cheap_repr import cheap_repr
from stack_data import (
    FrameInfo,
    RepeatedFrames,
    Serializer,
)

from core.runner.didyoumean import didyoumean_suggestions
from core.runner.friendly_traceback import friendly_message

log = logging.getLogger(__name__)


class TracebackSerializer(Serializer):
    filename = None

    def format_traceback_part(self, e: BaseException) -> dict:
        return dict(
            **super().format_traceback_part(e),
            didyoumean=didyoumean_suggestions(e),
            friendly=friendly_message(e, double_newline=True),
        )

    def format_frame(self, frame):
        result = super().format_frame(frame)
        del result["filename"]
        del result["lineno"]
        return result

    def format_line(self, line):
        result = super().format_line(line)
        result["content"] = result.pop("text")
        return result

    def format_variable_value(self, value) -> str:
        return cheap_repr(value)

    def should_include_frame(self, frame_info: FrameInfo) -> bool:
        return self.filename == frame_info.filename


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
