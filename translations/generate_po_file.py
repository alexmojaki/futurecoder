import ast
import builtins
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path
from textwrap import indent

from littleutils import group_by_key
from polib import POEntry, POFile

from core.text import pages
from core.utils import markdown_codes, MyASTTokens


def main():
    po = POFile(wrapwidth=120)
    code_bits = defaultdict(set)
    for page_slug, page in pages.items():
        page_link = "https://futurecoder.io/course/#" + page_slug
        for step_name, text in zip(page.step_names, page.step_texts(raw=True)):
            step_msgid = f"pages.{page_slug}.steps.{step_name}"
            po.append(make_po_entry(code_bits, page_link, f"{step_msgid}.text", text))
            if step_name == "final_text":
                continue

            step = page.get_step(step_name)
            for message_step in step.messages:
                msgid = f"{step_msgid}.messages.{message_step.__name__}.text"
                text = message_step.raw_text
                po.append(make_po_entry(code_bits, page_link, msgid, text))

            for i, hint in enumerate(step.hints):
                msgid = f"{step_msgid}.hints.{i}.text"
                po.append(make_po_entry(code_bits, page_link, msgid, hint))

    for code_bit, comments in code_bits.items():
        po.append(
            POEntry(
                msgid=f"code_bits.{code_bit}",
                msgstr=code_bit,
                comment="\n\n------\n\n".join(sorted(comments)),
            )
        )
    po.save(str(Path(__file__).parent / "english.po"))


def make_po_entry(code_bits, page_link, msgid, text):
    codes = [c for c in markdown_codes(text) if not c["no_auto_translate"]]
    codes_grouped = group_by_key(codes, "text")
    code_comments = []
    local_code_bits = set()
    for i, (code_text, group) in sorted(
        enumerate(codes_grouped.items()),
        key=lambda it: -len(it[1][0]),
    ):
        code_text = indent(code_text, "    ").rstrip()
        assert code_text in text
        text = text.replace(code_text, f"__code{i}__")
        assert code_text not in text
        code_comments.append(f"    # __code{i}__:\n{code_text}")

        code = group[0]["code"]
        atok = MyASTTokens(code, parse=1)
        for node in ast.walk(atok.tree):
            if isinstance(node, ast.Name):
                node_text = node.id
                assert atok.get_text(node) == node_text
                if node_text in builtins.__dict__ or len(node_text) == 1:
                    continue
            elif isinstance(
                node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
            ):
                node_text = node.name
            elif isinstance(node, (ast.Str, ast.JoinedStr)):
                node_text = atok.get_text(node)
                if not re.search(r"[a-zA-Z]", node_text) or re.match(
                    r"""^['"][a-zA-Z]['"]""", node_text
                ):
                    continue
            else:
                continue
            code_bits[node_text].add(f"{search_link(msgid)}\n\n{code_text}")
            local_code_bits.add(search_link(f"code_bits.{node_text}"))

    return POEntry(
        msgid=msgid,
        msgstr=text,
        comment="\n\n".join([page_link, *code_comments, *sorted(local_code_bits)]),
    )


def search_link(msgid):
    return (
        "https://poeditor.com/projects/view_terms?id=490053&search="
        + urllib.parse.quote_plus(msgid)
    )


main()
