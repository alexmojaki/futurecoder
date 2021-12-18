import pygments
from pygments.formatters.html import HtmlFormatter
from stack_data import style_with_executing_node

from core.runner.stack_data import TracebackSerializer
from core.runner.utils import is_valid_syntax
from pygments.lexers import get_lexer_by_name

lexer = get_lexer_by_name("python3")


class PygmentsTracebackSerializer(TracebackSerializer):
    def __init__(
        self,
        pygments_style=style_with_executing_node("monokai", "bg:#005080"),
    ):
        self.pygments_formatter = HtmlFormatter(
            style=pygments_style,
            nowrap=True,
        )

    def format_variable_part(self, text):
        if is_valid_syntax(text):
            return pygments.highlight(text, lexer, self.pygments_formatter)
        else:
            return super().format_variable_part(text)
