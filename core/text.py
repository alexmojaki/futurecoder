from __future__ import annotations

import ast
import inspect
import itertools
import re
import traceback
from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property, cache
from importlib import import_module
from io import StringIO
from pathlib import Path
from random import shuffle
from textwrap import dedent, indent
from tokenize import Untokenizer, generate_tokens
from types import MethodType
from typing import Union, List, get_type_hints

import pygments
from astcheck import is_ast_like
from littleutils import setattrs, only, select_attrs

from core.exercises import (
    check_result,
    generate_for_type,
    inputs_string,
    assert_equal,
    make_function,
    InvalidInitialCode,
    ExerciseError,
    match_returns_stdout,
)
from core.linting import lint
from core.runner.utils import is_valid_syntax
from core import translation as t
from core.utils import (
    highlighted_markdown,
    lexer,
    html_formatter,
    shuffled_well,
    no_weird_whitespace,
    snake,
    unwrapped_markdown,
    returns_stdout,
    NoMethodWrapper,
    add_stdin_input_arg,
)


def clean_program(program, cls):
    func = program

    if callable(program):
        source = dedent(inspect.getsource(program))
        lines = source.splitlines()
        if lines[-1].strip().startswith("return "):
            func = func()
            assert lines[0] == "def solution(self):"
            assert lines[-1] == f"    return {func.__name__}"
            source = dedent("\n".join(lines[1:-1]))
            program = clean_solution_function(func, source)
        else:
            tree = ast.parse(source)
            func_node = tree.body[0]
            assert isinstance(func_node, ast.FunctionDef)
            lines = lines[func_node.body[0].lineno - 1 :]
            if hasattr(cls, "test_values"):
                inputs = list(cls.test_values())[0][0]
                cls.stdin_input = inputs.pop("stdin_input", [])
            else:
                inputs = {}
            inputs = inputs_string(inputs)
            program = inputs + '\n' + dedent('\n'.join(lines))
        compile(program, "<program>", "exec")  # check validity

        func = NoMethodWrapper(func)
        func = add_stdin_input_arg(func)

        if not any(
            isinstance(node, ast.Return) for node in ast.walk(ast.parse(source))
        ) and not getattr(cls, "no_returns_stdout", False):
            func = returns_stdout(func)

    no_weird_whitespace(program)
    return program.strip(), func


def basic_signature(func):
    params = [t.get_code_bit(p) for p in inspect.signature(func).parameters]
    joined = ", ".join(params)
    return f'({joined})'


def clean_solution_function(func, source):
    name = t.get_code_bit(func.__name__)
    return re.sub(
        rf"def {name}\(.+?\):",
        rf"def {name}{basic_signature(func)}:",
        source,
    )


@cache
def clean_step_class(cls):
    assert cls.__name__ != "step_name_here"

    text = cls.text or cls.__doc__
    program = cls.program
    hints = cls.hints

    solution = cls.__dict__.get("solution", "")
    assert bool(solution) ^ bool(program)

    text = dedent(text).strip()
    assert text
    no_weird_whitespace(text)
    cls.raw_text = t.get(cls.text_msgid, text)

    if solution:
        assert cls.tests
        assert cls.auto_translate_program
        cls.solution = MethodType(solution, "")
        program, cls.solution = clean_program(cls.solution, cls)
    else:
        program, _ = clean_program(program, cls)
        if not is_valid_syntax(program):
            cls.auto_translate_program = False

    assert program
    if cls.auto_translate_program:
        program = t.translate_code(program)
    else:
        program = t.get(t.step_program(cls), program)

    if isinstance(hints, str):
        hints = hints.strip().splitlines()
    hints = [t.get(t.hint(cls, i), hint.strip()) for i, hint in enumerate(hints)]

    if "__program_" in text:
        text = text.replace("__program__", program)
        indented = indent(program, '    ').replace("\\", "\\\\")
        text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
    else:
        assert not cls.program_in_text, "Either include __program__ or __program_indented__ in the text, " \
                                        "or set program_in_text = False in the class."

    assert "__program_" not in text

    text = dedent(text).strip()

    messages = []
    for name, inner_cls in inspect.getmembers(cls):
        if not (isinstance(inner_cls, type) and issubclass(inner_cls, Step)):
            continue
        assert issubclass(inner_cls, MessageStep)

        inner_cls.tests = inner_cls.tests or cls.tests
        inner_cls.page = cls.page
        inner_cls.text_msgid = t.message_step_text(cls, inner_cls)
        clean_step_class(inner_cls)

        original_inner_cls = inner_cls

        # noinspection PyAbstractClass
        class inner_cls(inner_cls, cls):
            __qualname__ = inner_cls.__qualname__
            __module__ = inner_cls.__module__

        inner_cls.__name__ = original_inner_cls.__name__

        messages.append(inner_cls)

        if inner_cls.after_success and issubclass(inner_cls, ExerciseStep):
            cls.check_exercise(inner_cls.solution)

    setattrs(cls,
             text=text,
             program=program,
             messages=messages,
             hints=hints)

    if hints:
        cls.get_solution = get_solution(cls)

    if isinstance(cls.disallowed, Disallowed):
        cls.disallowed = [cls.disallowed]

    if cls.expected_code_source:
        assert cls.expected_code_source in expected_code_source_descriptions


def get_predictions(cls):
    choices = getattr(cls, "predicted_output_choices", None)
    if not choices:
        return dict(choices=None, answer=None)

    answer = cls.correct_output
    choices = [t.get(t.prediction_choice(cls, i), choice.rstrip()) for i, choice in enumerate(choices)]

    if answer:
        assert answer == "Error"
    else:
        answer = get_stdout(cls.program).rstrip()
        assert answer in choices, repr(answer)

    choices += [t.get(f"output_predictions.Error", "Error")]
    assert answer in choices, repr(answer)
    return dict(choices=choices, answer=answer)


@returns_stdout
def get_stdout(program):
    if "\n" not in program:
        program = f"print(repr({program}))"
    code = compile(program, "", "exec")
    exec(code, {"assert_equal": assert_equal})


def get_solution(step):
    if issubclass(step, ExerciseStep):
        if step.solution.__name__ == "solution":
            program, _ = clean_program(step.solution, None)  # noqa
        else:
            program = clean_solution_function(step.solution, dedent(inspect.getsource(step.solution)))
    else:
        program = step.program

    program = t.translate_code(program)

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

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.__name__ == "Page":
            return
        pages[cls.slug] = cls
        page_slugs_list.append(cls.slug)
        cls.step_names = []
        for key, value in cls.__dict__.items():
            if getattr(value, "is_step", False):
                cls.step_names.append(key)

        assert isinstance(cls.final_text, str)
        cls.final_text = t.get(t.step_text(cls.slug, "final_text"), cls.final_text.strip())
        no_weird_whitespace(cls.final_text)
        cls.step_names.append("final_text")

    def get_step(cls, step_name):
        step = getattr(cls, step_name)
        if step_name != "final_text":
            step.page = cls
            step.text_msgid = t.step_text(cls.slug, step_name)
            clean_step_class(step)
        return step

    def step_texts(cls, *, raw: bool):
        result = [step.raw_text if raw else step.text for step in cls.steps[:-1]] + [cls.final_text]
        if not raw:
            result = [highlighted_markdown(text) for text in result]
            assert "__copyable__" not in str(result)
            assert "__no_auto_translate__" not in str(result)
        return result

    @property
    def slug(cls):
        return cls.__dict__.get("slug", cls.__name__)

    @property
    def title(cls):
        return unwrapped_markdown(
            t.get(
                t.page_title(cls.slug),
                cls.raw_title,
            )
        )

    @property
    def raw_title(cls):
        return cls.__dict__.get(
            "title",
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

    @property
    def steps(self):
        return [self.get_step(step_name) for step_name in self.step_names]

    @property
    def step_dicts(self):
        return [
            dict(
                index=index,
                text=text,
                name=name,
                hints=[highlighted_markdown(hint) for hint in getattr(step, "hints", [])],
                solution=getattr(step, "get_solution", None),
                prediction=get_predictions(step),
            )
            for index, (name, text, step) in
            enumerate(zip(self.step_names, self.step_texts(raw=False), self.steps))
        ]


class Page(metaclass=PageMeta):
    pass

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


expected_code_source_descriptions = dict(
    shell="Type your code directly in the shell after `>>>` and press Enter.",
    birdseye="With your code in the editor, click the Bird's Eye button.",
    snoop="With your code in the editor, click the Snoop button.",
    pythontutor="With your code in the editor, click the Python Tutor button.",
)


class Step(ABC):
    text = ""
    program = ""
    program_in_text = False
    stdin_input = ""
    hints = ()
    is_step = True
    messages = ()
    tests = {}
    expected_code_source = None
    disallowed: List[Disallowed] = []
    parsons_solution = False
    get_solution = None
    predicted_output_choices = None
    correct_output = None
    translate_output_choices = True
    auto_translate_program = True
    page = None

    def __init__(self, *args):
        self.args = args
        self.input, self.result, self.code_source, self.console = args

    def clean_check(self) -> Union[bool, dict]:
        result = self.check()
        if not isinstance(result, dict):
            result = bool(result)
        return result

    def check_with_messages(self):
        result = self.clean_check()
        for message_cls in self.messages:
            if (result is True) == message_cls.after_success and (message_cls.check_message(self) is True):
                return message_cls.message()

        if result is True:
            for d in self.disallowed:
                if search_ast(
                    self.function_tree if d.function_only else self.tree,
                    d.template,
                    d.predicate
                ) > d.max_count:
                    return dict(message=d.message)

            if self.expected_code_source not in (None, self.code_source):
                return dict(
                    message="The code is correct, but you didn't run it as instructed. "
                    + expected_code_source_descriptions[self.expected_code_source]
                )

            return True

        if self.code_source != "shell":
            if not isinstance(result, dict):
                result = {}

            result.setdefault("messages", []).extend(lint(self.tree))

        return result

    @abstractmethod
    def check(self) -> Union[bool, dict]:
        raise NotImplementedError

    @cached_property
    def tree(self):
        return ast.parse(self.input)

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
            return self.check_exercise(self.input, functionise=True)
        else:
            function_name = t.get_code_bit(function_name)
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

            return self.check_exercise(func)

    @classmethod
    def _patch_streams(cls, func):
        func = match_returns_stdout(func, cls.solution)
        func = add_stdin_input_arg(func)
        return func

    @classmethod
    def check_exercise(cls, submission, functionise=False):
        solution = cls.wrap_solution(cls.solution)
        cls.test_exercise(solution, cls.test_values())
        inputs = [cls.generate_inputs() for _ in range(10)]
        expected_generated_results = [solution(**inp) for inp in inputs]

        if functionise:
            try:
                initial_names, func = make_function(submission, solution)
            except InvalidInitialCode:
                # There should be an exception in the usual output
                return False
            except ExerciseError as e:
                return dict(message=str(e))

            func = cls._patch_streams(func)
            initial_names["stdin_input"] = cls.stdin_input

            try:
                expected_result = solution(**initial_names)
            except Exception:
                traceback.print_exc()
                return dict(
                    message="The values of your input variables are invalid, "
                    "try using values like the example."
                )
            try:
                cls.check_result(func, initial_names, expected_result)
            except:
                # Assume that the user can tell that the output is wrong
                return False
        else:
            submission = cls.wrap_solution(submission)
            func = cls._patch_streams(submission)

        try:
            cls.test_exercise(
                func,
                itertools.chain(
                    cls.test_values(), zip(inputs, expected_generated_results)
                ),
            )
        except ExerciseError as e:
            return dict(message=str(e))

        return True

    @classmethod
    def wrap_solution(cls, func):
        return func

    @abstractmethod
    def solution(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def arg_names(cls):
        return list(inspect.signature(cls.solution).parameters)

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
    def test_exercise(cls, func, values):
        for inputs, result in values:
            cls.check_result(func, inputs, result)

    @classmethod
    def check_result(cls, func, inputs, result):
        return check_result(func, inputs, result)

    @classmethod
    def generate_inputs(cls):
        return {
            name: generate_for_type(typ)
            for name, typ in get_type_hints(cls.solution).items()
        }


class VerbatimStep(Step):
    program_in_text = True

    def check(self):
        if self.truncated_trees_match(
                self.tree,
                ast.parse(self.program),
        ):
            return True

        if self.truncated_trees_match(
                ast.parse(self.input.lower()),
                ast.parse(self.program.lower()),
        ):
            return dict(
                message="Python is case sensitive! That means that small and capital letters "
                        "matter and changing them changes the meaning of the program. The strings "
                        "`'hello'` and `'Hello'` are different, as are the variable names "
                        "`word` and `Word`."
            )

    def truncated_trees_match(self, input_tree, program_tree):
        input_tree = ast.Module(
            body=input_tree.body[:len(program_tree.body)],
            type_ignores=[],
        )
        return is_ast_like(input_tree, program_tree)


class MessageStep(Step, ABC):
    after_success = False

    @classmethod
    def message(cls):
        return dict(message=cls.text)

    @classmethod
    def check_message(cls, step):
        return cls(*step.args).clean_check()


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
        full_module_name = "core.chapters." + module_name
        import_module(full_module_name)
        slug = module_name[4:]
        title = slug.replace("_", " ").title()
        title = t.get(t.chapter_title(slug), title)
        chapter_pages = [
            select_attrs(page, "title slug")
            for page in pages.values()
            if page.__module__ == full_module_name
        ]
        yield dict(slug=slug, title=title, pages=chapter_pages)


chapters = list(load_chapters())


@cache
def get_pages():
    return dict(
        pages={
            slug: dict(
                **select_attrs(page, "slug title index step_names"),
                steps=page.step_dicts,
            )
            for slug, page in pages.items()
        },
        pageSlugsList=page_slugs_list,
    )


def iter_step_names(*, final_text: bool):
    for page in pages.values():
        step_names = page.step_names
        if not final_text:
            step_names = step_names[:-1]
        for step_name in step_names:
            yield page, step_name


def step_test_entries():
    for page, step_name in iter_step_names(final_text=False):
        step = page.get_step(step_name)

        for substep in [*step.messages, step]:
            program = substep.program

            if "\n" in program:
                code_source = step.expected_code_source or "editor"
            else:
                code_source = "shell"

            yield page, step, substep, dict(
                input=program,
                source=code_source,
                page_slug=page.slug,
                step_name=step_name,
            )
