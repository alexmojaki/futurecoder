from __future__ import annotations

import ast
import builtins
import gettext
import json
import os
import re
import unicodedata
from functools import cache
from pathlib import Path
from textwrap import indent

import asttokens.util
from asttokens import ASTTokens

from core.runner.utils import is_valid_syntax
import core.utils

translation: gettext.GNUTranslations | None = None
current_language = None

root_path = Path(__file__).parent.parent / "translations"
codes_path = root_path / "codes.json"

try:
    code_blocks = codes_path.read_text()
except FileNotFoundError:
    code_blocks = None
else:
    code_blocks = json.loads(code_blocks)


def set_language(language):
    global current_language
    global translation

    if language == "None":
        # Hack to explicitly set the language to None with an env var, which must be a string
        return

    current_language = language
    translation = gettext.translation(
        "futurecoder",
        str(root_path / "locales"),
        languages=[language],
    )
    for key, value in misc_terms():
        setattr(Terms, key, get(misc_term(key), value))


def get(msgid, default):
    assert msgid
    assert default
    if current_language is None:
        return default

    result = translation.gettext(msgid)
    if result == msgid:
        # assert (
        #     msgid.startswith(("code_bits."))
        #     or "output_prediction_choices" in msgid
        #     or ".disallowed." in msgid
        # )
        return default

    if os.environ.get("CHECK_INLINE_CODES"):
        original = inline_codes(default)
        inline1 = {translate_code(c) for c in original}
        inline2 = inline_codes(result)
        if inline1 != inline2:
            print("Inline codes don't match auto-translation in", msgid)
            print("original:", original)
            print("expected (auto-translated):", sorted(inline1))
            print("actual:", sorted(inline2))
            print("expected - actual:", inline1 - inline2)
            print("actual - expected:", inline2 - inline1)
            print()

    def replace(match):
        block_num = match[1]
        assert isinstance(code_blocks, dict)
        code_block = code_blocks[msgid][block_num]
        code = code_block["code"]
        suffix_length = len(code) - code_block["code_text_length"]
        translated = translate_code(code)[:-suffix_length]
        return indent(translated, "    " + code_block["prefix"])

    result = re.sub(r"^ *__code(\d+)__", replace, result, flags=re.MULTILINE)
    assert result
    special1 = re.findall(r"__\w+__", result)
    special2 = re.findall(r"__\w+__", default)
    if special1 != special2:
        core.utils.qa_error(
            f"Mismatched special strings for {msgid}: {special1} != {special2}"
        )
    if current_language == "en" or (
        current_language in ["ta", "zh"]
        and (
            msgid.startswith(("code_bits."))
            or "output_prediction_choices" in msgid
            or msgid.endswith(".program")
        )
    ):
        assert result == default

    return result


def translate_code(code):
    replacements = []
    for node, node_text in get_code_bits(code):
        start = code.find(node_text, node.first_token.startpos)
        end = start + len(node_text)
        text_range = (start, end)
        replacements.append((*text_range, get_code_bit(node_text)))
    return asttokens.util.replace(code, replacements)


def translate_program(cls, program):
    from core.utils import clean_spaces

    program = clean_spaces(program)
    if cls.auto_translate_program:
        result = translate_code(program)
    else:
        result = get(step_program(cls), program)
    return clean_spaces(result)


def get_code_bits(code):
    atok = ASTTokens(code, parse=1)

    for node in ast.walk(atok.tree):
        if isinstance(node, ast.Name):
            if not atok.get_text(node):
                continue
            node_text = node.id
            assert (
                unicodedata.normalize("NFKD", node_text) ==
                unicodedata.normalize("NFKD", atok.get_text(node))
            )
            if node_text in builtins.__dict__ or len(node_text) == 1:
                continue
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            for arg in node.args.args:
                if len(arg.arg) == 1:
                    continue
                yield arg, arg.arg
            node_text = node.name
        elif isinstance(node, (ast.Str, ast.JoinedStr)):
            node_text = atok.get_text(node)
            if not re.search(r"[a-zA-Z]", node_text) or re.match(
                r"""^['"][a-zA-Z]['"]""", node_text
            ):
                continue
        else:
            continue

        yield node, node_text


def translate_dict_keys(d):
    return {get_code_bit(k): v for k, v in d.items()}


def chapter_title(chapter_slug):
    return f"chapters.{chapter_slug}.title"


def page(page_slug):
    return f"pages.{page_slug}"


def page_title(page_slug):
    return f"{page(page_slug)}.title"


def step(page_slug, step_name):
    return f"{page(page_slug)}.steps.{step_name}"


def step_cls(cls):
    return step(cls.page.slug, cls.__name__)


def step_text(page_slug, step_name):
    return f"{step(page_slug, step_name)}.text"


def step_program(cls):
    return f"{step_cls(cls)}.program"


def prediction_choice(cls, i):
    return f"{step_cls(cls)}.output_prediction_choices.{i}"


def message_step_text(cls, message_step):
    return f"{step_cls(cls)}.messages.{message_step.__name__}.text"


def special_message_text(cls, special_message):
    return f"{step_cls(cls)}.special_messages.{special_message.__name__}.text"


def hint(cls, i):
    return f"{step_cls(cls)}.hints.{i}.text"


def disallowed(cls, i):
    return f"{step_cls(cls)}.disallowed.{i}"


def disallowed_message(cls, i):
    return f"{disallowed(cls, i)}.message"


def disallowed_label(cls, i):
    return f"{disallowed(cls, i)}.label"


def requirements(cls):
    return f"{step_cls(cls)}.requirements"

def code_bit(node_text):
    return f"code_bits.{node_text}"


@cache
def get_code_bit(node_text):
    result = get(code_bit(node_text), node_text)
    try:
        node1 = ast.parse(node_text).body[0].value
        node2 = ast.parse(result).body[0].value
        assert type(node1) == type(node2)
        assert isinstance(node1, (ast.Name, ast.Str, ast.JoinedStr))
        for quote in ['"', "'"]:
            assert result.startswith(quote) == node_text.startswith(quote)
            assert result.endswith(quote) == node_text.endswith(quote)
            quote = 'f' + quote
            assert result.startswith(quote) == node_text.startswith(quote)

        if isinstance(node1, ast.JoinedStr):
            parts1 = fstring_parts(node1, node_text)
            parts2 = fstring_parts(node2, result)
            assert parts2 == {translate_code(part) for part in parts1}

    except (AssertionError, SyntaxError):
        core.utils.qa_error(f"Invalid translation from {node_text} to {result}")
    return result


def fstring_parts(node, source):
    return {
        ast.get_source_segment(source, part.value)  # noqa
        for part in node.values
        if isinstance(part, ast.FormattedValue)
    }


def inline_codes(text):
    return {c for c in re.findall(r"`(.+?)`", text) if is_valid_syntax(c)}


def pyflakes_message(message_cls):
    return f"linting_messages.pyflakes.{message_cls.__name__}.message_format"


class Terms:
    disallowed_default_message = (
        "Well done, you have found a solution! However, for this exercise and your learning, "
        "you're not allowed to use {label}."
    )
    disallowed_default_label = "more than {max_count} {label}"

    expected_mode_shell = (
        "Type your code directly in the shell after `>>>` and press Enter."
    )
    expected_mode_birdseye = (
        "With your code in the editor, click the `birdseye` button."
    )
    expected_mode_snoop = "With your code in the editor, click the `snoop` button."
    expected_mode_pythontutor = (
        "With your code in the editor, click the Python Tutor button."
    )

    incorrect_mode = "The code is correct, but you didn't run it as instructed."

    must_define_function = "You must define a function `{function_name}`"
    not_a_function = "`{function_name}` is not a function."
    signature_should_be = (
        "The signature should be:\n\n"
        "    def {function_name}{needed_signature}:\n\n"
        "not:\n\n"
        "    def {function_name}{actual_signature}:"
    )

    invalid_inputs = "The values of your input variables are invalid, try using values like the example."

    case_sensitive = (
        "Python is case sensitive! That means that small and capital letters "
        "matter and changing them changes the meaning of the program. The strings "
        "`'hello'` and `'Hello'` are different, as are the variable names "
        "`word` and `Word`."
    )

    string_spaces_differ = (
        "Check that the strings in your code have the correct spaces. "
        "For example, `'Hello'` is different from `'Hello '` because of the space at the end."
    )

    code_should_start_like = """\
Your code should start like this:

{expected_start}
"""

    blank_result = "<nothing>"

    your_code_outputs_given_values = """\
Given these values:

{given_values}

your code outputs:"""

    your_code_outputs = "Your code outputs:"

    when_it_should_output = "when it should output:"

    which_is_correct = "which is correct!"

    copy_button = "Copy"

    q_wiz_final_message = """
Great! Here's some final tips:

- Make sure the output is showing the problem you have and not something else.
- Reduce your code to a **minimal** example. Remove any code that isn't directly related to the problem.
- Run your code through the `snoop`, `birdseye`, and Python Tutor debuggers to understand what it's doing.
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
    q_wiz_input_message_start = (
        "`input()` makes it harder to ask and answer questions about code. "
        "Replace calls to input with strings so that everyone can run the code instantly "
        "and get the same results."
    )

    q_wiz_input_replace_with = """Replace:

{original_lines}

with

{replaced_lines}"""

    q_wiz_input_and_add = """and add

    {list_line}

to the top of your code."""

    q_wiz_no_output = (
        "Your code didn't output anything. "
        "Add some `print()` calls so that at least it outputs *something*. "
        "Use code to show readers exactly where the problem is."
    )
    q_wiz_same_as_expected_output = (
        "Your output is the same as your expected output! "
        "If your problem is still there, adjust your code and/or "
        "your expected output so that the two outputs don't match. "
        "Make it clear what would be different if the code worked "
        "the way you want it to."
    )

    q_wiz_debugger = (
        "It's great that you're using a debugger! "
        "Solving the problem on your own is ideal. "
        "If you can't, use the 'Run' button to generate the question."
    )

    no_more_test_inputs = "No more test inputs - solution should have finished by now"

    syntax_error_at_line = "at line"


def misc_term(key):
    return f"misc_terms.{key}"


def misc_terms():
    for key, value in Terms.__dict__.items():
        if key.startswith("_"):
            continue
        assert isinstance(value, str)
        yield key, value
