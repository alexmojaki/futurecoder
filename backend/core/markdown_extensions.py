import xml.etree.ElementTree as etree
from html import unescape
from textwrap import dedent

from littleutils import strip_required_prefix
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from core.utils import is_valid_syntax

lexer = get_lexer_by_name("python3")
monokai = get_style_by_name("monokai")
html_formatter = HtmlFormatter(nowrap=True)


class HighlightPythonTreeProcessor(Treeprocessor):
    def run(self, root):
        for node in root.findall(".//pre/code"):
            text = unescape(node.text)

            prefix = "__copyable__\n"
            if copyable := text.startswith(prefix):
                text = strip_required_prefix(text, prefix)

            if (
                    is_valid_syntax(text) or
                    is_valid_syntax(text + "\n 0") or
                    is_valid_syntax(dedent(text))
            ):
                self.highlight_node(node, text)
            else:
                node.text = text

            if copyable:
                node.append(etree.fromstring('<button class="btn btn-primary">Copy</button>'))
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
    def extendMarkdown(self, md):
        md.treeprocessors.register(HighlightPythonTreeProcessor(), "highlight_python", 0)
