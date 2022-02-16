import ast
from textwrap import indent, dedent
from core import translation as t

import asttokens.util
from littleutils import only

from core.linting import lint
from core.utils import highlighted_markdown, new_tab_links


def input_messages(input_nodes):
    if not input_nodes:
        return []

    message = t.Terms.q_wiz_input_message_start

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

        message += f"\n\n{t.Terms.q_wiz_input_replace_with.format(**locals())}\n\n"

        if list_line:
            message += f"\n\n{t.Terms.q_wiz_input_and_add.format(**locals())}\n\n"

    return [message]


def question_wizard_check(entry, output, runner):
    if entry["source"] == "shell":
        return [], "shell"

    messages = input_messages(runner.input_nodes)

    if not output.strip():
        messages.append(t.Terms.q_wiz_no_output)

    try:
        tree = ast.parse(entry["input"])
    except SyntaxError:
        pass
    else:
        messages.extend(lint(tree))

    if not messages:
        if not entry["expected_output"].strip():
            return [], "expected_output"

        if entry["expected_output"].strip() == output.strip():
            messages.append(t.Terms.q_wiz_same_as_expected_output)
        elif entry["source"] == "editor":
            messages.append(
                t.Terms.q_wiz_final_message.format(
                    indent(entry["input"], " " * 8).rstrip(),
                    indent(output, " " * 8).rstrip(),
                    indent(entry["expected_output"], " " * 8).rstrip(),
                )
            )
        else:
            messages.append(t.Terms.q_wiz_debugger)

    messages = [new_tab_links(highlighted_markdown(message)) for message in messages]
    return messages, "messages"
