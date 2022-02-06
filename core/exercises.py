import ast
import inspect
import random
import string
import typing
from textwrap import indent

from littleutils import only

from core import translation as t
from core.utils import format_exception_string, returns_stdout


class ExerciseError(Exception):
    pass


class InvalidInitialCode(Exception):
    pass


def make_function(program, function_template):
    arg_names = inspect.signature(function_template).parameters
    tree = ast.parse(program)
    try:
        for node, arg_name in zip(tree.body, arg_names):
            assert isinstance(node, ast.Assign)
            target = only(node.targets)
            assert isinstance(target, ast.Name)
            assert target.id == arg_name
    except AssertionError:
        expected_start = indented_inputs_string(dict.fromkeys(arg_names, "..."))
        raise ExerciseError(
            t.Terms.code_should_start_like.format(expected_start=expected_start)
        )

    assignments = tree.body[:len(arg_names)]
    exercise = tree.body[len(arg_names):]
    tree.body = assignments
    code = compile(tree, "<string>", "exec", dont_inherit=True)
    initial_names = {}
    try:
        exec(code, initial_names)
    except Exception as e:
        raise InvalidInitialCode from e
    del initial_names["__builtins__"]

    tree.body = exercise
    code = compile(tree, "<string>", "exec", dont_inherit=True)

    def func(**kwargs):
        exec(code, kwargs)

    return initial_names, func


def match_returns_stdout(func, solution):
    if getattr(solution, "returns_stdout", False):
        func = returns_stdout(func)
    return func


def clean_result(result):
    if not isinstance(result, str):
        result = repr(result)
    result = '\n'.join(line.rstrip() for line in result.rstrip().splitlines())
    result = result or t.Terms.blank_result
    result = indent(result, '    ')
    return result


def indented_inputs_string(inputs):
    return indent(inputs_string(inputs), '    ')


def inputs_string(inputs):
    return '\n'.join(f'{name} = {value!r}'
                     for name, value in inputs.items())


def check_result(func, inputs, expected_result):
    try:
        result = func(**inputs)
    except Exception as e:
        result = format_exception_string()

    cleaned_result = clean_result(result)
    expected_result = clean_result(expected_result)

    if cleaned_result != expected_result:
        inputs.pop("stdin_input", None)
        if inputs:
            message = t.Terms.your_code_outputs_given_values.format(
                given_values=indented_inputs_string(inputs)
            )
        else:
            message = t.Terms.your_code_outputs

        message += f"""

{cleaned_result}

{t.Terms.when_it_should_output}

{expected_result}
"""
        raise ExerciseError(message)
    return result


def generate_string(length=None):
    if length is None:
        length = random.randrange(5, 11)
    return "".join(random.sample(string.ascii_letters, length))


def generate_list(typ):
    return [
        generate_for_type(typ)
        for _ in range(random.randrange(5, 11))
    ]


def generate_for_type(typ):
    if isinstance(typ, typing._GenericAlias):
        if typ.__origin__ is list:
            return generate_list(only(typ.__args__))
    return {
        str: generate_string(),
        bool: random.choice([True, False]),
        int: random.randrange(100),
    }[typ]


# This function is shown to the user, keep it simple
# Its definition is duplicated in App.js to copy it into PythonTutor code
def assert_equal(actual, expected):
    if actual == expected:
        print("OK")
    else:
        print(f"Error! {repr(actual)} != {repr(expected)}")
