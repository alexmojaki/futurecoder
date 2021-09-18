import ast
from textwrap import indent

from core.linting import lint

final_message_format = """
Great! Copy and paste this into the question website, and replace the first line with a description of your problem.

    __copyable__
    *Explain what you're trying to do and why*

    Here's my code:
    
{}

    This is the result:

{}
"""


def question_wizard_check(entry, output):
    if entry["source"] == "shell":
        return []

    messages = []

    if not output.strip():
        messages.append(
            "Your code didn't output anything. "
            "Add some `print()` calls so that at least it outputs *something*. "
            "Use code to show readers exactly where the problem is."
        )

    try:
        tree = ast.parse(entry["input"])
    except SyntaxError:
        pass
    else:
        messages.extend(lint(tree))

    if not messages:
        if entry["source"] == "editor":
            messages.append(
                final_message_format.format(
                    indent(entry["input"], " " * 8),
                    indent(output, " " * 8),
                )
            )
        else:
            messages.append(
                "It's great that you're using a debugger! "
                "Solving the problem on your own is ideal. "
                "If you can't, use the 'Run' button to generate the question."
            )

    return messages
