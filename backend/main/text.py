import ast
import inspect
import random
import re
from abc import ABCMeta, abstractmethod
from importlib import import_module
from textwrap import indent, dedent
from typing import get_type_hints

from astcheck import is_ast_like
from littleutils import setattrs
from markdown import markdown

from main.exercises import check_exercise, check_result, generate_short_string
from main.utils import no_weird_whitespace, snake, unwrapped_markdown

step = None


def clean_program(program):
    if callable(program):
        lines, _ = inspect.getsourcelines(program)
        program = dedent(''.join(lines[1:]))
        compile(program, "<program>", "exec")  # check validity
    no_weird_whitespace(program)
    return program.strip()


class StepMeta(ABCMeta):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.__dict__.get("abstract"):
            return

        assert issubclass(cls, Step)
        text = cls.text or cls.__doc__
        program = cls.program
        expected_program = cls.expected_program
        hints = cls.hints

        program = clean_program(program)
        expected_program = clean_program(expected_program)

        if isinstance(hints, str):
            hints = hints.strip().splitlines()
        hints = [markdown(text) for text in hints]
        no_weird_whitespace(text)
        if "__program_" in text:
            assert program
            text = text.replace("__program__", program)
            indented = indent(program, '    ')
            text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
        else:
            assert not program
        assert "__program_" not in text

        assert not (expected_program and program)
        if expected_program:
            program = expected_program

        assert text
        text = markdown(text.strip())

        setattrs(cls,
                 text=text,
                 program=program,
                 hints=hints)


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
        return cls.__dict__.get("slug", cls.__name__)

    @property
    def title(cls):
        return unwrapped_markdown(cls.__dict__.get(
            "title",
            snake(cls.slug)
                .replace("_", " ")
                .title()
        ))

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
        self.step = getattr(self, step_name)(code_entry, console)

    def before_step(self):
        return None

    def check_step(self):
        before = self.before_step()
        if before is not None:
            return before

        try:
            return self.step.check()
        except SyntaxError:
            return False


class Step(metaclass=StepMeta):
    text = ""
    program = ""
    expected_program = ""
    hints = ()
    is_step = True
    abstract = True

    def __init__(self, code_entry, console):
        self.input = code_entry.input
        self.result = code_entry.output
        self.code_source = code_entry.source
        self.console = console

    @abstractmethod
    def check(self):
        raise NotImplementedError

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
        return self.tree_matches(self.program)

    def input_matches(self, pattern, remove_spaces=True):
        inp = self.input.rstrip()
        if remove_spaces:
            inp = re.sub(r'\s', '', inp)
        return re.match(pattern + '$', inp)


class ExerciseStep(Step):
    tests = {}
    abstract = True

    def check(self):
        return self.check_exercise(
            self.solution, 
            self.test_exercise,
            self.generate_inputs, 
            functionise=True,
        )

    @abstractmethod
    def solution(self):
        raise NotImplementedError

    def arg_names(self):
        return list(inspect.signature(self.solution).parameters)

    def test_exercise(self, func):
        for inputs, result in self.tests.items():
            if not isinstance(inputs, tuple):
                inputs = (inputs,)
            inputs = dict(zip(self.arg_names(), inputs))
            check_result(func, inputs, result)

    def generate_inputs(self):
        return {
            name: {
                str: generate_short_string(),
                bool: random.choice([True, False]),
            }[typ]
            for name, typ in get_type_hints(self.solution).items()
        }


class VerbatimStep(Step):
    abstract = True

    def check(self):
        return self.matches_program()


def search_ast(node, template):
    return any(
        is_ast_like(child, template)
        for child in ast.walk(node)
    )


for chapter_name in "shell string_basics variables for_loops if_statements".split():
    import_module("main.chapters." + chapter_name)
