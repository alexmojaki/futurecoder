import pygments
from pygments.lexers import get_lexer_by_name

from core.runner.stack_data import TracebackSerializer
from core.runner.utils import is_valid_syntax

lexer = get_lexer_by_name("python3")


class PygmentsTracebackSerializer(TracebackSerializer):
    def format_variable_part(self, text):
        if is_valid_syntax(text):
            return pygments.highlight(text, lexer, self.options.pygments_formatter)
        else:
            return super().format_variable_part(text)
