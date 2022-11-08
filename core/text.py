from __future__ import annotations

import ast
import inspect
import itertools
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property, cache
from importlib import import_module
from io import StringIO
from pathlib import Path
from random import shuffle
from textwrap import indent
from tokenize import Untokenizer, generate_tokens
from types import MethodType
from typing import Union, List, get_type_hints

import pygments
from astcheck import is_ast_like
from littleutils import setattrs, only, select_attrs

from core import translation as t
from core.exercises import (
    check_result,
    generate_for_type,
    inputs_string,
    assert_equal,
    make_function,
    InvalidInitialCode,
    ExerciseError,
    match_returns_stdout,
    indented_inputs_string,
)
from core.linting import lint
from core.runner.utils import is_valid_syntax
from core.utils import (
    highlighted_markdown,
    lexer,
    html_formatter,
    shuffled_well,
    clean_spaces,
    snake,
    unwrapped_markdown,
    returns_stdout,
    NoMethodWrapper,
    add_stdin_input_arg,
    qa_error,
    split_into_tokens,
)


def clean_program(program, cls):
    if callable(program) and not cls.auto_translate_program:
        program = inspect.getsource(program).splitlines()[1:]

    if not callable(program):
        program = clean_spaces(program)
        if not is_valid_syntax(program):
            cls.auto_translate_program = False

        cls.show_solution_program = program = t.translate_program(cls, program)
        return program

    func = program
    source = t.translate_program(cls, inspect.getsource(program))
    globs = func.__globals__  # noqa
    exec(source, globs)
    func = globs[t.get_code_bit(func.__name__)]
    func = MethodType(func, "")

    lines = source.splitlines()
    cls.is_function_exercise = lines[-1].strip().startswith("return ")
    if cls.is_function_exercise:
        func = func()
        assert lines[0] == f"def {t.get_code_bit('solution')}(self):"
        assert lines[-1] == f"    return {func.__name__}"
        source = clean_spaces(lines[1:-1])
        source = program = clean_solution_function(func, source)

    tree = ast.parse(source)
    if not any(
        isinstance(node, ast.Return) for node in ast.walk(tree)
    ) and not getattr(cls, "no_returns_stdout", False):
        func = returns_stdout(func)
    func = add_stdin_input_arg(func)
    func = NoMethodWrapper(func)
    cls.solution = func
    func_node = function_node(func, tree)

    if cls.is_function_exercise:
        cls.show_solution_program = ast.get_source_segment(source, func_node)
    else:
        lines = lines[func_node.body[0].lineno - 1 :]
        cls.show_solution_program = program = clean_spaces(lines)
        if hasattr(cls, "test_values"):
            inputs = cls.example_inputs()
            cls.stdin_input = inputs.pop("stdin_input", [])
            if inputs:
                inputs = inputs_string(inputs)
                program = inputs + "\n" + program

    compile(program, "<program>", "exec")  # check validity
    return program


def basic_signature(func):
    joined = ", ".join(inspect.signature(func).parameters)
    return f'({joined})'


def basic_function_header(func):
    return highlighted_markdown(f"    def {func.__name__}{basic_signature(func)}:")


def clean_solution_function(func, source):
    return re.sub(
        rf"def {func.__name__}\(.+?\):",
        rf"def {func.__name__}{basic_signature(func)}:",
        source,
    )


def get_special_messages(cls):
    return [v for k, v in inspect.getmembers(cls.special_messages) if not k.startswith("__")]


@cache
def clean_step_class(cls):
    assert cls.__name__ != "step_name_here"

    text = cls.text or cls.__doc__
    program = cls.program
    hints = cls.hints

    solution = cls.__dict__.get("solution", "")
    assert bool(solution) ^ bool(program)

    if issubclass(cls, ExerciseStep) and not issubclass(cls, MessageStep):
        assert cls.hints, cls

    if solution:
        assert cls.tests
        assert cls.auto_translate_program
        cls.solution = MethodType(solution, "")
        program = clean_program(cls.solution, cls)  # noqa
        cls.solution = cls.wrap_solution(cls.solution)
        if not issubclass(cls, MessageStep) or cls.after_success:
            cls.test_exercise(cls.solution)
    else:
        program = clean_program(program, cls)

    assert program

    if isinstance(hints, str):
        hints = hints.strip().splitlines()
    hints = [t.get(t.hint(cls, i), hint.strip()) for i, hint in enumerate(hints)]

    text = clean_spaces(text)
    assert text
    text = t.get(cls.text_msgid, text)
    text = clean_spaces(text)
    cls.raw_text = text

    assert "__program__indented__" not in text

    if "__program_" in text:
        text = text.replace("__program__", program)
        indented = indent(program, '    ').replace("\\", "\\\\")
        text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
        cls.program_in_text = True
    else:
        if cls.program_in_text:
            qa_error(
                "Either include __program__ or __program_indented__ in the text, "
                "or set program_in_text = False in the class. "
                f"Step: {cls}. Text: {text}",
            )

    assert "__program_" not in text, (cls, text)
    text = clean_spaces(text)

    for special_message in get_special_messages(cls):
        msgstr = clean_spaces(special_message.__doc__ or special_message.text)
        msgstr = t.get(t.special_message_text(cls, special_message), msgstr)
        special_message.text = msgstr
        try:
            special_message.program = t.translate_code(special_message.program)
        except SyntaxError:
            pass

    messages = []
    for name, inner_cls in inspect.getmembers(cls):
        if not (isinstance(inner_cls, type) and issubclass(inner_cls, Step)):
            continue
        assert issubclass(inner_cls, MessageStep)

        inner_cls.tests = inner_cls.tests or cls.tests
        inner_cls.generate_inputs = getattr(cls, "generate_inputs", None)
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

    cls.get_solution = get_solution(cls)

    if isinstance(cls.disallowed, Disallowed):
        cls.disallowed = [cls.disallowed]
    for i, disallowed in enumerate(cls.disallowed):
        disallowed.setup(cls, i)

    if cls.expected_code_source:
        cls.expected_code_source_term()


def get_predictions(cls):
    choices = getattr(cls, "predicted_output_choices", None)
    if not choices:
        return dict(choices=None, answer=None)

    answer = cls.correct_output
    choices = [t.get(t.prediction_choice(cls, i), choice.rstrip()).rstrip() for i, choice in enumerate(choices)]
    error = t.get(f"output_predictions.Error", "Error")

    if answer:
        assert answer == "Error"
        answer = error
    else:
        try:
            answer = get_stdout(cls.program).rstrip()
        except Exception as e:
            qa_error(f"Error running program in {t.step_cls(cls)}: {e}")
            answer = error

    choices += [error]
    if answer not in choices:
        qa_error(f"{t.step_cls(cls)}.output_prediction_choices: correct answer {answer} not in choices {choices}")
    return dict(choices=choices, answer=answer)


@returns_stdout
def get_stdout(program):
    if "\n" not in program:
        program = f"print(repr({program}))"
    code = compile(program, "", "exec")
    exec(code, {"assert_equal": assert_equal})


def get_solution(step):
    program = step.show_solution_program
    tokens = split_into_tokens(program)

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

        cls.final_text = clean_spaces(cls.final_text)
        cls.final_text = t.get(t.step_text(cls.slug, "final_text"), cls.final_text)
        cls.final_text = clean_spaces(cls.final_text)
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
            if "__copyable__" in str(result) or "__no_auto_translate__" in str(result):
                qa_error(f"{cls} has __copyable__ or __no_auto_translate__ in step texts")
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
                requirements=step.get_all_requirements() if getattr(step, "is_step", False) else None,
            )
            for index, (name, text, step) in
            enumerate(zip(self.step_names, self.step_texts(raw=False), self.steps))
        ]


class Page(metaclass=PageMeta):
    pass


class Disallowed:
    def __init__(self, template, *, label="", message="", max_count=0, predicate=lambda n: True, function_only=False):
        assert bool(label) ^ bool(message)
        self.label = label
        self.message = clean_spaces(message)
        self.max_count = max_count
        self.predicate = predicate
        self.function_only = function_only
        self.template = template

    def setup(self, step_cls, i):
        label = self.label and t.get(t.disallowed_label(step_cls, i), self.label)
        message = self.message and t.get(t.disallowed_message(step_cls, i), self.message)

        if not message:
            if self.max_count > 0:
                label = t.Terms.disallowed_default_label.format(
                    max_count=self.max_count, label=label
                )

            message = t.Terms.disallowed_default_message.format(label=label)

        self.text = clean_spaces(message)


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
    translated_tests = False
    page = None
    is_function_exercise = False
    requirements = ""

    class special_messages:
        pass

    @classmethod
    def pre_run(cls, runner):
        pass

    def __init__(self, *args):
        self.args = args
        self.input, self.result, self.code_source, self.console = args

    def clean_check(self) -> Union[bool, dict]:
        result = self.check()
        if hasattr(result, "text"):
            result = dict(message=result.text)

        if not isinstance(result, dict):
            result = dict(passed=bool(result))

        result.setdefault("passed", False)
        result.setdefault("messages", [])

        return result

    def check_with_messages(self):
        result = self.clean_check()
        for message_cls in self.messages:
            if result["passed"] == message_cls.after_success and message_cls.check_message(self)["passed"]:
                return result | dict(message=message_cls.text, passed=False)

        if result["passed"]:
            for d in self.disallowed:
                if search_ast(
                    self.function_tree if d.function_only else self.tree,
                    d.template,
                    d.predicate
                ) > d.max_count:
                    return result | dict(message=d.text, passed=False)

            if self.expected_code_source not in (None, self.code_source):
                return result | dict(
                    passed=False,
                    message=t.Terms.incorrect_mode + " " + self.expected_code_source_term(),
                )

            return result

        if self.code_source != "shell":
            try:
                tree = self.tree
            except SyntaxError:
                pass
            else:
                result["lint"] = lint(tree)

        return result

    @abstractmethod
    def check(self) -> Union[bool, dict]:
        raise NotImplementedError

    @classmethod
    def expected_code_source_term(cls):
        return getattr(t.Terms, f"expected_mode_{cls.expected_code_source}")

    @classmethod
    def get_all_requirements(cls):
        result = cls.get_requirements()
        if cls.program_in_text:
            result.append(dict(type="program_in_text"))
        if cls.requirements == "hints":
            assert cls.hints
        elif cls.requirements:
            translated = t.get(t.requirements(cls), cls.requirements)
            result.append(dict(type="custom", message=highlighted_markdown(translated)))

        assert result, cls

        if cls.expected_code_source:
            result.append(dict(type="custom", message=highlighted_markdown(cls.expected_code_source_term())))
        return result

    @classmethod
    def get_requirements(cls):
        return []

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
        func = self.solution
        assert self.is_function_exercise
        return function_node(func, self.tree)


def function_node(func, tree):
    function_name = t.get_code_bit(func.__name__)
    return only(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        if node.name == function_name
    )


class ExerciseStep(Step):
    def check(self):
        if self.code_source == "shell":
            return False

        if not self.is_function_exercise:
            return self.check_exercise(self.input, functionise=True)
        else:
            function_name = self.solution.__name__
            if function_name not in self.console.locals:
                return dict(
                    message=t.Terms.must_define_function.format(
                        function_name=function_name
                    )
                )

            func = self.console.locals[function_name]
            if not inspect.isfunction(func):
                return dict(
                    message=t.Terms.not_a_function.format(function_name=function_name)
                )

            actual_signature = basic_signature(func)
            needed_signature = basic_signature(self.solution)
            if actual_signature != needed_signature:
                return dict(message=t.Terms.signature_should_be.format(**locals()))

            return self.check_exercise(func)

    @classmethod
    def get_requirements(cls):
        result = [dict(type="exercise")]
        inputs = cls.example_inputs()
        stdin_input = inputs.pop("stdin_input", None)
        if not cls.is_function_exercise:
            inputs = highlighted_markdown(indented_inputs_string(inputs))
            result.append(dict(type="non_function_exercise", inputs=inputs))
        else:
            result.append(dict(type="function_exercise", header=basic_function_header(cls.solution)))
            if goal := cls.function_exercise_goal():
                result.append(dict(type="function_exercise_goal", print_or_return=goal))
        if stdin_input:
            result.append(dict(type="exercise_stdin"))
        return result

    @classmethod
    def function_exercise_goal(cls):
        assert cls.is_function_exercise
        if (
            cls.wrap_solution.__func__ == ExerciseStep.wrap_solution.__func__ and
            cls.check_result.__func__ == ExerciseStep.check_result.__func__
        ):
            if getattr(cls.solution, "returns_stdout", False):
                return "print"
            else:
                return "return"
        else:
            assert cls.requirements, cls
            return None

    @classmethod
    def _patch_streams(cls, func):
        func = match_returns_stdout(func, cls.solution)
        func = add_stdin_input_arg(func)
        return func

    @classmethod
    def check_exercise(cls, submission, functionise=False):
        solution = cls.solution
        test_values = list(cls.test_values())

        if functionise:
            try:
                initial_names, func = make_function(submission, cls.arg_names())
            except InvalidInitialCode:
                # TODO message for this
                # There should be an exception in the usual output
                return False
            except ExerciseError as e:
                return dict(message=str(e))

            func = cls._patch_streams(func)
            if cls.stdin_input:
                initial_names["stdin_input"] = cls.stdin_input

            try:
                expected_result = solution(**initial_names)
            except Exception:
                return dict(message=t.Terms.invalid_inputs)

            if not any(names == initial_names for names, _ in test_values):
                # Show a test in the assessment for the user's own initial values,
                # if there isn't a test for them already.
                test_values.insert(0, (initial_names, expected_result))
        else:
            submission = cls.wrap_solution(submission)
            func = cls._patch_streams(submission)

        passed_tests = []
        return_value = dict(passed_tests=passed_tests, passed=True)
        for inputs, result in test_values:
            test_result = cls.check_result(func, inputs, result)
            if test_result["passed"]:
                passed_tests.append(test_result["message"])
            else:
                return_value["passed"] = False
                return_value["message"] = test_result["message"]
                break

        return return_value

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
    def example_inputs(cls):
        [[inputs, _result]] = itertools.islice(cls.test_values(), 1)
        return inputs

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
            inputs = t.translate_dict_keys(inputs)
            if cls.translated_tests and t.current_language not in (None, "en"):
                # TODO also translate inputs, handling lists and dicts
                result = cls.solution(**inputs)
            yield inputs, result

        for _ in range(10):
            inputs = cls.generate_inputs()
            inputs = t.translate_dict_keys(inputs)
            result = cls.solution(**inputs)
            yield inputs, result

    @classmethod
    def test_exercise(cls, func):
        for inputs, result in cls.test_values():
            assert cls.check_result(func, inputs, result)["passed"]

    @classmethod
    def check_result(cls, func, inputs, result):
        return check_result(func, inputs, result)[0]

    @classmethod
    def generate_inputs(cls):
        return {
            name: generate_for_type(typ)
            for name, typ in get_type_hints(cls.solution).items()
        }


class VerbatimStep(Step):
    program_in_text = True

    class StringSpacesDiffer(Exception):
        pass

    @classmethod
    def get_requirements(cls):
        if not cls.program_in_text:
            assert cls.requirements, cls
        return [dict(type="verbatim")]

    def check(self):
        try:
            if result:= self.truncated_trees_match(
                self.tree,
                ast.parse(self.program),
            ):
                return result
        except SyntaxError:
            pass

        if self.truncated_trees_match(
            ast.parse(self.input.lower()),
            ast.parse(self.program.lower()),
        ):
            return dict(message=t.Terms.case_sensitive)

    def truncated_trees_match(self, input_tree, program_tree):
        body = [
            stmt
            for stmt in input_tree.body
            if not (isinstance(stmt, ast.FunctionDef) and stmt.name == "assert_equal")
        ]
        input_tree = ast.Module(
            body=body[:len(program_tree.body)],
            type_ignores=[],
        )
        return self.are_trees_equal(input_tree, program_tree)

    def are_trees_equal(self, t1, t2):
        try:
            self.assert_trees_equal(t1, t2)
            return True
        except VerbatimStep.StringSpacesDiffer:
            return dict(message=t.Terms.string_spaces_differ)
        except AssertionError:
            return False

    def assert_trees_equal(self, t1, t2):
        assert type(t1) == type(t2)
        if isinstance(t1, (list, tuple)):
            assert len(t1) == len(t2)
            for vc1, vc2 in zip(t1, t2):
                self.assert_trees_equal(vc1, vc2)
        elif isinstance(t1, ast.Str) and isinstance(t2, ast.Str):
            if t1.s == t2.s:
                return
            s1 = t1.s.replace(" ", "")
            s2 = t2.s.replace(" ", "")
            if s1 == s2:
                raise self.StringSpacesDiffer()
            raise AssertionError
        elif isinstance(t1, ast.AST):
            self.assert_trees_equal(
                list(ast.iter_fields(t1)),
                list(ast.iter_fields(t2)),
            )
        else:
            assert t1 == t2


class MessageStep(Step, ABC):
    after_success = False

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

        for substep in [*step.messages, *get_special_messages(step), step]:
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
