import ast
import inspect
import random
import string
import traceback
import typing
from textwrap import indent

from littleutils import only

from main.utils import format_exception_string, returns_stdout


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
        raise ExerciseError(f"""\
Your code should start like this:

{indented_inputs_string(dict.fromkeys(arg_names, "..."))}
""")

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


def check_exercise(func, solution, test, generate_inputs, functionise=False):
    test(solution)
    inputs = [generate_inputs() for _ in range(10)]
    expected_generated_results = [solution(**inp) for inp in inputs]

    if functionise:
        try:
            initial_names, func = make_function(func, solution)
        except InvalidInitialCode:
            # There should be an exception in the usual output
            return False
        except ExerciseError as e:
            return dict(message=str(e))

        func = match_returns_stdout(func, solution)

        try:
            expected_result = solution(**initial_names)
        except Exception:
            traceback.print_exc()
            return dict(message="The values of your input variables are invalid, "
                                "try using values like the example.")

        try:
            check_result(func, initial_names, expected_result)
        except:
            # Assume that the user can tell that the output is wrong
            return False
    else:
        func = match_returns_stdout(func, solution)

    try:
        test(func)
        for inp, result in zip(inputs, expected_generated_results):
            check_result(func, inp, result)
    except ExerciseError as e:
        return dict(message=str(e))

    return True


def clean_result(result):
    if not isinstance(result, str):
        result = repr(result)
    result = result.rstrip()
    result = result or '<nothing>'
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

    result = clean_result(result)
    expected_result = clean_result(expected_result)

    if result != expected_result:
        raise ExerciseError(f"""\
For these inputs:

{indented_inputs_string(inputs)}

your code outputs:

{result}

when it should output:

{expected_result}
""")


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


def main():
    program = """
name = 'World'
print('Hello ' + name)
    """

    @returns_stdout
    def solution(name):
        print('Hello ' + name)

    def test(func):
        check_result(func, {"name": "World"}, "Hello World\n")
        check_result(func, {"name": "Bob"}, "Hello Bob\n")

    def generate_inputs():
        return {"name": generate_string()}

    print(check_exercise(program, solution, test, generate_inputs, functionise=True))


if __name__ == '__main__':
    main()
