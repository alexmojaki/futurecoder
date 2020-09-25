from __future__ import annotations

import ast
import inspect
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property
from importlib import import_module
from io import StringIO
from pathlib import Path
from random import shuffle
from textwrap import dedent, indent
from tokenize import Untokenizer, generate_tokens
from types import FunctionType
from typing import Type, Union, List, get_type_hints

import pygments
from astcheck import is_ast_like
from asttokens import ASTTokens
from littleutils import setattrs, only

from main.exercises import (
    check_exercise,
    check_result,
    generate_for_type,
    inputs_string,
)
from main.utils import highlighted_markdown, lexer, html_formatter, shuffled_well, no_weird_whitespace, snake, \
    unwrapped_markdown, returns_stdout, NoMethodWrapper, bind_self


def clean_program(program, cls):
    func = program
    if isinstance(program, FunctionType):
        source = dedent(inspect.getsource(program))
        lines = source.splitlines()
        if lines[-1].strip().startswith("return "):
            func = NoMethodWrapper(program(None))
            assert lines[0] == "def solution(self):"
            assert lines[-1] == f"    return {func.__name__}"
            source = dedent("\n".join(lines[1:-1]))
            program = clean_solution_function(func, source)
        else:
            atok = ASTTokens(source, parse=True)
            func_node = atok.tree.body[0]
            lines = lines[func_node.body[0].first_token.start[0] - 1:]
            if hasattr(cls, "test_values"):
                inputs = list(cls.test_values())[0][0]
            else:
                inputs = {}
            inputs = inputs_string(inputs)
            program = inputs + '\n' + dedent('\n'.join(lines))
        compile(program, "<program>", "exec")  # check validity

        if not any(isinstance(node, ast.Return) for node in ast.walk(ast.parse(source))):
            func = returns_stdout(func)

    no_weird_whitespace(program)
    return program.strip(), func


def basic_signature(func):
    joined = ", ".join(inspect.signature(func).parameters)
    return f'({joined})'


def clean_solution_function(func, source):
    return re.sub(
        rf"def {func.__name__}\(.+?\):",
        rf"def {func.__name__}{basic_signature(func)}:",
        source,
    )


def clean_step_class(cls, clean_inner=True):
    assert cls.__name__ != "step_name_here"

    text = cls.text or cls.__doc__
    program = cls.program
    hints = cls.hints

    solution = cls.__dict__.get("solution", "")
    assert bool(solution) ^ bool(program)
    assert text
    no_weird_whitespace(text)

    if solution:
        assert cls.tests
        program, cls.solution = clean_program(solution, cls)
    else:
        program, _ = clean_program(program, cls)
    assert program

    if isinstance(hints, str):
        hints = hints.strip().splitlines()
    hints = [highlighted_markdown(hint) for hint in hints]

    if "__program_" in text:
        text = text.replace("__program__", program)
        indented = indent(program, '    ')
        text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
    else:
        assert not cls.program_in_text, "Either include __program__ or __program_indented__ in the text, " \
                                        "or set program_in_text = False in the class."

    assert "__program_" not in text

    text = highlighted_markdown(dedent(text).strip())

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
                        bind_self(inner_cls.solution),
                        bind_self(cls.solution),
                        cls.test_exercise,
                        cls.generate_inputs,
                    )

            clean_step_class(inner_cls, clean_inner=False)

    setattrs(cls,
             text=text,
             program=program,
             messages=messages,
             hints=hints)

    if hints:
        cls.get_solution = get_solution(cls)


def get_solution(step):
    if issubclass(step, ExerciseStep):
        if step.solution.__name__ == "solution":
            program, _ = clean_program(step.solution, None)
        else:
            program = clean_solution_function(step.solution, dedent(inspect.getsource(step.solution)))
    else:
        program = step.program

    untokenizer = Untokenizer()
    tokens = generate_tokens(StringIO(program).readline)
    untokenizer.untokenize(tokens)
    tokens = untokenizer.tokens

    masked_indices = []
    mask = [False] * len(tokens)
    for i, token in enumerate(tokens):
        if not token.isspace():
            masked_indices.append(i)
            mask[i] = True
    shuffle(masked_indices)

    if step.parsons_solution:
        lines = shuffled_well([
            dict(
                id=str(i),
                content=line,
            )
            for i, line in enumerate(
                pygments.highlight(program, lexer, html_formatter)
                    .splitlines()
            )
            if line.strip()
        ])
    else:
        lines = None

    return dict(
        tokens=tokens,
        maskedIndices=masked_indices,
        mask=mask,
        lines=lines,
    )


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
        cls.final_text = highlighted_markdown(cls.final_text.strip())
        cls.step_names.append("final_text")
        cls.step_texts.append(cls.final_text)
        assert "__copyable__" not in str(cls.step_texts)

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

    @property
    def step_dicts(self):
        return [
            dict(
                text=text,
                name=name,
                hints=getattr(step, "hints", []),
                solution=getattr(step, "get_solution", None),
            )
            for name, text, step in
            zip(self.step_names, self.step_texts, self.steps)
        ]


class Page(metaclass=PageMeta):
    @classmethod
    def check_step(cls, code_entry, output, console):
        step_cls: Type[Step] = getattr(cls, code_entry['step_name'])
        step = step_cls(code_entry['input'], output, code_entry['source'], console)
        try:
            return step.check_with_messages()
        except SyntaxError:
            return False

    # Workaround for Django templates which can't see metaclass properties
    @classmethod
    def title_prop(cls):
        return cls.title

    @classmethod
    def slug_prop(cls):
        return cls.slug

    @classmethod
    def index_prop(cls):
        return cls.index


class Disallowed:
    def __init__(self, template, *, label="", message="", max_count=0, predicate=lambda n: True, function_only=False):
        assert bool(label) ^ bool(message)
        if not message:
            if max_count > 0:
                label = f"more than {max_count} {label}"
            message = "Well done, you have found a solution! However, for this exercise and your learning, " \
                      f"you're not allowed to use {label}."
        message = dedent(message).strip()
        self.template = template
        self.message = message
        self.max_count = max_count
        self.predicate = predicate
        self.function_only = function_only


class Step(ABC):
    text = ""
    program = ""
    program_in_text = False
    hints = ()
    is_step = True
    messages = ()
    tests = {}
    expected_code_source = None
    disallowed: List[Disallowed] = []
    parsons_solution = False
    get_solution = None

    def __init__(self, *args):
        self.args = args
        self.input, self.result, self.code_source, self.console = args

    def check_with_messages(self):
        if self.expected_code_source not in (None, self.code_source):
            return False

        result = self.check()
        if not isinstance(result, dict):
            result = bool(result)
        for message_cls in self.messages:
            if result == message_cls.after_success and message_cls.check_message(self):
                return message_cls.message()
        if result is True:
            for d in self.disallowed:
                if search_ast(
                    self.function_tree if d.function_only else self.tree,
                    d.template,
                    d.predicate
                ) > d.max_count:
                    return dict(message=d.message)
        return result

    @abstractmethod
    def check(self) -> Union[bool, dict]:
        raise NotImplementedError

    @cached_property
    def tree(self):
        return ast.parse(self.input)

    @property
    def stmt(self):
        return self.tree.body[0]

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

    @cached_property
    def function_tree(self):
        # We define this here so MessageSteps implicitly inheriting from ExerciseStep don't complain it doesn't exist
        # noinspection PyUnresolvedReferences
        function_name = self.solution.__name__

        if function_name == "solution":
            raise ValueError("This exercise doesn't require defining a function")

        return only(
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
            if node.name == function_name
        )


class ExerciseStep(Step):
    def check(self):
        if self.code_source == "shell":
            return False

        function_name = self.solution.__name__

        if function_name == "solution":
            return check_exercise(
                self.input,
                self.solution,
                self.test_exercise,
                self.generate_inputs,
                functionise=True,
            )
        else:
            if function_name not in self.console.locals:
                return dict(message=f"You must define a function `{function_name}`")

            func = self.console.locals[function_name]
            if not inspect.isfunction(func):
                return dict(message=f"`{function_name}` is not a function.")

            actual_signature = basic_signature(func)
            needed_signature = basic_signature(self.solution)
            if actual_signature != needed_signature:
                return dict(
                    message=f"The signature should be:\n\n"
                            f"    def {function_name}{needed_signature}:\n\n"
                            f"not:\n\n"
                            f"    def {function_name}{actual_signature}:"
                )

            return check_exercise(
                func,
                self.solution,
                self.test_exercise,
                self.generate_inputs,
            )

    @abstractmethod
    def solution(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def arg_names(cls):
        return list(inspect.signature(bind_self(cls.solution)).parameters)

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


def search_ast(node, template, predicate=lambda n: True):
    """
    Returns the number of descendants of `node` that match `template`
    (either a type or tuple that is passed to `isinstance`,
    or a partial AST that is passed to `is_ast_like`)
    and satisfy the optional predicate.
    """
    return sum(
        (
            isinstance(child, template)
            if isinstance(template, (type, tuple)) else
            is_ast_like(child, template)
        )
        and predicate(child)
        and child != node
        for child in ast.walk(node)
    )


def load_chapters():
    chapters_dir = Path(__file__).parent / "chapters"
    path: Path
    for path in sorted(chapters_dir.glob("c*.py")):
        module_name = path.stem
        full_module_name = "main.chapters." + module_name
        module = import_module(full_module_name)
        title = module_name[4:].replace("_", " ").title()
        chapter_pages = [p for p in pages.values() if p.__module__ == full_module_name]
        yield title, module, chapter_pages


chapters = list(load_chapters())
