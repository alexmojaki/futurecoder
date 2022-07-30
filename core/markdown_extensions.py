import xml.etree.ElementTree as etree
from html import unescape
from textwrap import dedent

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from core.utils import check_and_remove_prefix
from core.runner.utils import is_valid_syntax
from core import translation as t

lexer = get_lexer_by_name("python3")
monokai = get_style_by_name("monokai")
html_formatter = HtmlFormatter(nowrap=True)


class HighlightPythonTreeProcessor(Treeprocessor):
    codes = None

    def run(self, root):
        for node in root.findall(".//pre/code"):
            text = unescape(node.text)
            text = dedent(text)

            # TODO: this assumes that __copyable__ never comes after __no_auto_translate__
            text, copyable = check_and_remove_prefix(text, "__copyable__\n")
            text, no_auto_translate = check_and_remove_prefix(text, "__no_auto_translate__\n")

            for code in [text, text + "\n 0", dedent(text)]:
                if is_valid_syntax(code):
                    self.highlight_node(node, text)
                    self.codes.append(dict(
                        code=code,
                        text=text,
                        no_auto_translate=no_auto_translate,
                    ))
                    break
            else:
                node.text = text

            if copyable:
                node.append(
                    etree.fromstring(
                        f'<button class="btn btn-primary copy-button">{t.Terms.copy_button}</button>'
                    )
                )
                node.set("class", node.get("class", "") + " copyable")

    @staticmethod
    def highlight_node(node, text):
        import xml.etree.ElementTree as etree
        import pygments

        highlighted = pygments.highlight(text, lexer, html_formatter)
        tail = node.tail
        node.clear()
        node.set("class", "codehilite")
        node.append(etree.fromstring(f"<span>{highlighted}</span>"))
        node.tail = tail


class HighlightPythonExtension(Extension):
    codes = None

    def extendMarkdown(self, md):
        processor = HighlightPythonTreeProcessor()
        processor.codes = self.codes
        md.treeprocessors.register(processor, "highlight_python", 0)
