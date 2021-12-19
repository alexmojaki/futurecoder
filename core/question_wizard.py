import ast
from textwrap import indent, dedent

import asttokens.util
from littleutils import only

from core.linting import lint
from core.utils import highlighted_markdown

final_message_format = """
Great! Here's some final tips:

- Make sure the output is showing the problem you have and not something else.
- Reduce your code to a **minimal** example. Remove any code that isn't directly related to the problem.
- Run your code through the Snoop, Birdseye, and Python Tutor debuggers to understand what it's doing.
- Search for your problem online.
- Read [How do I ask a good question?](https://stackoverflow.com/help/how-to-ask)

If you're really ready, copy and paste the below into the question website,
and replace the first line with a description of your problem.

You can still change your code or expected output and click Run again to regenerate the question.

    __copyable__
    *Explain what you're trying to do and why*

    Here's my code:

{}

    This is the result:

{}

    The expected output is:

{}
"""


def input_messages(input_nodes):
    if not input_nodes:
        return []

    message = "`input()` makes it harder to ask and answer questions about code. " \
              "Replace calls to input with strings so that everyone can run the code instantly " \
              "and get the same results.\n"

    multi_nodes = [node for node, group in input_nodes.items() if len(group) > 1]
    for node, group in input_nodes.items():
        strings, exs = zip(*group)

        if len(strings) > 1:
            if len(multi_nodes) > 1:
                list_name = f"test_inputs_{multi_nodes.index(node) + 1}"
            else:
                list_name = f"test_inputs"
            list_line = f"{list_name} = {list(strings)}"
            replacement_text = f"{list_name}.pop(0)"
        else:
            list_line = None
            replacement_text = repr(only(strings))

        source = only({ex.source for ex in exs})
        text_range = only({ex.text_range() for ex in exs})
        piece = only(piece for piece in source.pieces if node.lineno in piece and node.end_lineno in piece)

        def piece_lines(lines):
            return indent(dedent("\n".join(lines[lineno - 1] for lineno in piece)), ' ' * 4)

        replaced_text = asttokens.util.replace(source.text, [(*text_range, replacement_text)])
        replaced_lines = piece_lines(replaced_text.splitlines())
        original_lines = piece_lines(source.lines)

        message += f"""
Replace:

{original_lines}

with

{replaced_lines}
"""
        if list_line:
            message += f"""
and add

    {list_line}

to the top of your code.
"""
    return [message]


def question_wizard_check(entry, output, runner):
    if entry["source"] == "shell":
        return None

    messages = input_messages(runner.input_nodes)

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
        if not entry["expected_output"].strip():
            return "__expected_output__"

        if entry["expected_output"].strip() == output.strip():
            messages.append(
                "Your output is the same as your expected output! "
                "If your problem is still there, adjust your code and/or "
                "your expected output so that the two outputs don't match. "
                "Make it clear what would be different if the code worked "
                "the way you want it to."
            )
        elif entry["source"] == "editor":
            messages.append(
                final_message_format.format(
                    indent(entry["input"], " " * 8).rstrip(),
                    indent(output, " " * 8).rstrip(),
                    indent(entry["expected_output"], " " * 8).rstrip(),
                )
            )
        else:
            messages.append(
                "It's great that you're using a debugger! "
                "Solving the problem on your own is ideal. "
                "If you can't, use the 'Run' button to generate the question."
            )

    messages = [highlighted_markdown(message) for message in messages]
    return messages
