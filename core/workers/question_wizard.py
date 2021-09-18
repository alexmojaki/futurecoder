import ast
from textwrap import indent

from core.linting import lint

final_message_format = """
Great! Here's some final tips:

- Make sure the output is showing the problem you have and not something else.
- Reduce your code to a **minimal** example. Remove any code that isn't directly related to the problem.
- Run your code through the Snoop, Birdseye, and Python Tutor debuggers to understand what it's doing.
- Search for your problem online.
- Read [How do I ask a good question?](https://stackoverflow.com/help/how-to-ask)

If you're really ready, copy and paste the below into the question website,
and replace the first line with a description of your problem.

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
