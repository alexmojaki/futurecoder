import ast
import re
from importlib import import_module
from textwrap import indent

from astcheck import is_ast_like
from markdown import markdown

from main.exercises import check_exercise
from main.utils import no_weird_whitespace, snake


def step(text, *, program="", hints=()):
    if isinstance(hints, str):
        hints = hints.strip().splitlines()
    hints = [markdown(text) for text in hints]
    no_weird_whitespace(text)
    no_weird_whitespace(program)
    program = program.strip()
    if "__program_" in text:
        assert program
        text = text.replace("__program__", program)
        indented = indent(program, '    ')
        text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
    else:
        assert not program
    assert "__program_" not in text

    text = markdown(text.strip())

    def decorator(f):
        f.is_step = True
        f.hints = hints
        f.text = text
        f.program = program
        return f

    return decorator


pages = {}
page_slugs_list = []


class PageMeta(type):
    final_text = None
    step_names = []
    step_texts = []

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.__name__ == "Page":
            return
        pages[cls.slug] = cls
        page_slugs_list.append(cls.slug)
        cls.step_names = []
        cls.step_texts = []
        for key, value in cls.__dict__.items():
            if getattr(value, "is_step", False):
                cls.step_names.append(key)
                cls.step_texts.append(value.text)

        assert isinstance(cls.final_text, str)
        no_weird_whitespace(cls.final_text)
        cls.final_text = markdown(cls.final_text.strip())
        cls.step_names.append("final_text")
        cls.step_texts.append(cls.final_text)

    @property
    def slug(cls):
        return cls.__name__

    @property
    def title(cls):
        return (
            snake(cls.slug)
                .replace("_", " ")
                .title()
        )

    @property
    def index(self):
        return page_slugs_list.index(self.slug)

    @property
    def next_page(self):
        return pages[page_slugs_list[self.index + 1]]

    @property
    def previous_page(self):
        return pages[page_slugs_list[self.index - 1]]


class Page(metaclass=PageMeta):
    def __init__(self, code_entry, console, step_name):
        self.input = code_entry.input
        self.result = code_entry.output
        self.code_source = code_entry.source
        self.console = console
        self.step_name = step_name
        self.step = getattr(self, step_name)

    def before_step(self):
        return None

    def check_step(self):
        before = self.before_step()
        if before is not None:
            return before

        try:
            return self.step()
        except SyntaxError:
            return False

    def check_exercise(self, *args, **kwargs):
        if self.code_source == "editor":
            return check_exercise(self.input, *args, **kwargs)

    @property
    def tree(self):
        return ast.parse(self.input)

    @property
    def stmt(self):
        return self.tree.body[0]

    @property
    def expr(self):
        return self.stmt.value

    def tree_matches(self, template):
        if is_ast_like(self.tree, ast.parse(template)):
            return True

        if is_ast_like(ast.parse(self.input.lower()), ast.parse(template.lower())):
            return dict(
                message="Python is case sensitive! That means that small and capital letters "
                        "matter and changing them changes the meaning of the program. The strings "
                        "`'hello'` and `'Hello'` are different, as are the variable names "
                        "`word` and `Word`."
            )

    def matches_program(self):
        return self.tree_matches(self.step.program)

    def input_matches(self, pattern, remove_spaces=True):
        inp = self.input.rstrip()
        if remove_spaces:
            inp = re.sub(r'\s', '', inp)
        return re.match(pattern + '$', inp)


def search_ast(node, template):
    return any(
        is_ast_like(child, template)
        for child in ast.walk(node)
    )


for chapter_name in "shell string_basics variables for_loops".split():
    import_module("main.chapters." + chapter_name)
