from __future__ import annotations

import ast
import inspect
import re
from abc import abstractmethod, ABC
from copy import deepcopy
from functools import partial
from importlib import import_module
from textwrap import indent, dedent
from typing import get_type_hints, Union, Type

from astcheck import is_ast_like
from asttokens import ASTTokens
from littleutils import setattrs
from markdown import markdown

from main.exercises import check_exercise, check_result, inputs_string, generate_for_type
from main.utils import no_weird_whitespace, snake, unwrapped_markdown


def clean_program(program, inputs=None):
    if callable(program):
        inputs = inputs_string(inputs or {})
        source = dedent(inspect.getsource(program))
        atok = ASTTokens(source, parse=True)
        func = atok.tree.body[0]
        lines = source.splitlines()[func.body[0].first_token.start[0] - 1:]
        program = inputs + '\n' + dedent('\n'.join(lines))
        compile(program, "<program>", "exec")  # check validity
    no_weird_whitespace(program)
    return program.strip()


def clean_step_class(cls, clean_inner=True):
    text = cls.text or cls.__doc__
    program = cls.program
    hints = cls.hints

    solution = cls.__dict__.get("solution", "")
    assert bool(solution) ^ bool(program)
    assert text
    no_weird_whitespace(text)

    if solution:
        assert cls.tests
        # noinspection PyUnresolvedReferences
        inputs = list(cls.test_values())[0][0]
        program = clean_program(solution, inputs)
    else:
        program = clean_program(program)
    assert program

    if isinstance(hints, str):
        hints = hints.strip().splitlines()
    hints = [markdown(hint) for hint in hints]

    if "__program_" in text:
        text = text.replace("__program__", program)
        indented = indent(program, '    ')
        text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
    else:
        assert not cls.program_in_text, "Either include __program__ or __program_indented__ in the text, " \
                                        "or set program_in_text = False in the class."

    assert "__program_" not in text

    text = markdown(dedent(text).strip())

    messages = []
    if clean_inner:
        for name, inner_cls in inspect.getmembers(cls):
            if not (isinstance(inner_cls, type) and issubclass(inner_cls, Step)):
                continue

            if issubclass(inner_cls, MessageStep):
                inner_cls.tests = inner_cls.tests or cls.tests
                clean_step_class(inner_cls)

                # noinspection PyAbstractClass
                class inner_cls(inner_cls, cls):
                    __name__ = inner_cls.__name__
                    __qualname__ = inner_cls.__qualname__
                    __module__ = inner_cls.__module__
                    program_in_text = inner_cls.program_in_text

                messages.append(inner_cls)

                if inner_cls.after_success and issubclass(inner_cls, ExerciseStep):
                    check_exercise(
                        partial(inner_cls.solution, None),
                        partial(cls.solution, None),
                        cls.test_exercise,
                        cls.generate_inputs,
                    )

            clean_step_class(inner_cls, clean_inner=False)

    setattrs(cls,
             text=text,
             program=program,
             messages=messages,
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
                clean_step_class(value)
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

    @property
    def steps(self):
        return [getattr(self, step_name) for step_name in self.step_names]


class Page(metaclass=PageMeta):
    @classmethod
    def check_step(cls, step_name, code_entry, console):
        step_cls: Type[Step] = getattr(cls, step_name)
        step = step_cls(code_entry.input, code_entry.output, code_entry.source, console)
        try:
            return step.check_with_messages()
        except SyntaxError:
            return False


class Step(ABC):
    text = ""
    program = ""
    program_in_text = False
    hints = ()
    is_step = True
    messages = ()
    tests = {}

    def __init__(self, *args):
        self.args = args
        self.input, self.result, self.code_source, self.console = args

    def check_with_messages(self):
        result = self.check()
        if not isinstance(result, dict):
            result = bool(result)
        for message_cls in self.messages:
            if result == message_cls.after_success and message_cls.check_message(self):
                return message_cls.message()
        return result

    @abstractmethod
    def check(self) -> Union[bool, dict]:
        raise NotImplementedError

    def check_exercise(self, *args, **kwargs):
        if self.code_source != "shell":
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

    def check(self):
        return self.check_exercise(
            self.solution, 
            self.test_exercise,
            self.generate_inputs, 
            functionise=True,
        )

    @abstractmethod
    def solution(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def arg_names(cls):
        return list(inspect.signature(cls.solution).parameters)[1:]

    @classmethod
    def test_values(cls):
        tests = cls.tests
        if isinstance(tests, dict):
            tests = tests.items()
        for inputs, result in tests:
            if not isinstance(inputs, dict):
                if not isinstance(inputs, tuple):
                    inputs = (inputs,)
                arg_names = cls.arg_names()
                assert len(arg_names) == len(inputs)
                inputs = dict(zip(arg_names, inputs))
            inputs = deepcopy(inputs)
            yield inputs, result

    @classmethod
    def test_exercise(cls, func):
        for inputs, result in cls.test_values():
            check_result(func, inputs, result)

    @classmethod
    def generate_inputs(cls):
        return {
            name: generate_for_type(typ)
            for name, typ in get_type_hints(cls.solution).items()
        }


class VerbatimStep(Step):
    program_in_text = True

    def check(self):
        return self.matches_program()


class MessageStep(Step, ABC):
    after_success = False

    @classmethod
    def message(cls):
        return dict(message=cls.text)

    @classmethod
    def check_message(cls, step):
        return cls(*step.args).check()


def search_ast(node, template):
    return any(
        is_ast_like(child, template)
        for child in ast.walk(node)
    )


for chapter_name in "shell string_basics variables for_loops if_statements lists".split():
    import_module("main.chapters." + chapter_name)
