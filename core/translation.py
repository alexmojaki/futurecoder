from __future__ import annotations

import ast
import builtins
import gettext
import json
import re
from pathlib import Path
from textwrap import indent

import asttokens.util
from asttokens import ASTTokens

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
    current_language = language
    translation = gettext.translation(
        "futurecoder",
        str(root_path / "locales"),
        languages=[language],
    )


def get(msgid, default):
    assert msgid
    assert default
    if current_language is None:
        return default

    result = translation.gettext(msgid)
    if result == msgid:
        # TODO chapters and special messages should be translated
        assert msgid.startswith(("code_bits.", "chapters.")) or "output_prediction_choices" in msgid or ".special_messages." in msgid
        return default

    def replace(match):
        block_num = match[1]
        assert isinstance(code_blocks, dict)
        code_block = code_blocks[msgid][block_num]
        code = code_block["code"]
        suffix_length = len(code) - code_block["code_text_length"]
        translated = translate_code(code)[:-suffix_length]
        return indent(translated, "    " + code_block["prefix"])

    result = re.sub(r"__code(\d+)__", replace, result)
    assert result
    if current_language == "en":
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
    if cls.auto_translate_program:
        return translate_code(program)
    else:
        return get(step_program(cls), program)


def get_code_bits(code):
    atok = ASTTokens(code, parse=1)

    for node in ast.walk(atok.tree):
        if isinstance(node, ast.Name):
            if not atok.get_text(node):
                continue
            node_text = node.id
            assert atok.get_text(node) == node_text
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


def code_bit(node_text):
    return f"code_bits.{node_text}"


def get_code_bit(node_text):
    return get(code_bit(node_text), node_text)


def pyflakes_message(message_cls):
    return f"linting_messages.pyflakes.{message_cls.__name__}.message_format"
