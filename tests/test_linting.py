import ast
from core.linting import lint


def lint_tree(code):
    tree = ast.parse(code)
    return list(lint(tree))


def test_import_shadowed_by_loop_var():
    code_import_shadowed_by_loop_var = """
import pandas as pd
x=[1,2,3]
for pd in x:
    print(pd)
    """
    assert lint_tree(code_import_shadowed_by_loop_var) == [
        """
**Import `pd` shadowed by loop variable**

The name of the loop variable `pd` should be changed as it redefines the `pd` module imported earlier.
Choose a different loop variable to avoid this error.
"""
    ]


def test_unused_import():
    code_unused_import = """
import random
def write_to_file(text, filename):
    with open("log.txt", "w") as file:
        file.write(text)
"""
    assert lint_tree(code_unused_import) == [
        """
**Unused import `random`**

You imported `random` but never used it. Did you forget to use it?
Maybe you used the wrong variable in its place? If you don't need the import, just remove it entirely.
    """
    ]


def test_unused_var():
    code_unused_var = """
import random

def write_random_to_file():
    no = random.randint(1, 10)
    with open("random.txt", "w") as file:
        file.write(str(no))
    return no

random_no = write_random_to_file()
print ("A random number was written to random.txt")
"""
    assert lint_tree(code_unused_var) == [
        """
**Unused variable `random_no`**

You defined a variable `random_no` but never used it. Did you forget to use it?
Maybe you used the wrong variable in its place? If you don't need it, just remove it entirely.
    """
    ]


def test_is_literal():
    code_is_literal = """
x='a'
'aa' is x*2

"""
    assert lint_tree(code_is_literal) == [
        """
**`is` comparison with literal**

You used the `is`/`is not` operator to compare with a literal (e.g. a string or number).
You should have rather used the `==` / `!=` operator.

The `is` operator checks if two expressions refer to the exact same object.
You rarely want to use them, certainly not for basic data types like strings and numbers.
In those cases they will seem to work sometimes (e.g. for small numbers) and mysteriously
fail on other occasions.
    """
    ]


def test_redefined_while_unused():
    code_redefined_while_unused = """
def is_positive(number: int) -> bool:
    return number > 0


def is_positive(number: int) -> bool: 
    return number >= 0

    """
    assert lint_tree(code_redefined_while_unused) == [
        """
**Redefined `is_positive` without using it**

You defined `is_positive` on line `2`, but before ever using it you redefined it,
overwriting the original definition.

In general your functions and classes should have different names.
Check that you use everything you define, e.g. that you called your functions.
    """
    ]


def test_import_star():
    code_import_star = """
from base import *
print(BaseThing('hi'))
"""
    assert lint_tree(code_import_star) == [
        """
**Import made using `*` **

`from base import *` imports everything from the module `base` into the current namespace.
This creates a bunch of invisible unknown variables.
It makes it hard to read and understand code and see where things come from.

Avoid this kind of import and instead explicitly import exactly the names you need.
"""
    ]


def test_import_star_not_permitted():
    code_import_star_not_permitted = """
def f():
    from module import *
"""
    assert lint_tree(code_import_star_not_permitted) == [
        """
**Import made using `*` **

`from module import *` imports everything from the module `module` into the current namespace.
This creates a bunch of invisible unknown variables.
It makes it hard to read and understand code and see where things come from.

Avoid this kind of import and instead explicitly import exactly the names you need.
"""
    ]


def test_multi_value_repeated_key_literal():
    code_multi_value_repeated_key = """
print({'a':1,'b':2,'a':3})
"""
    assert lint_tree(code_multi_value_repeated_key) == [
        """
**Dictionary key `a` repeated with different values**

A dictionary cannot have multiple entries for the same key.
Check your code again and change the repeated key to something unique.
""",

        """
**Dictionary key `a` repeated with different values**

A dictionary cannot have multiple entries for the same key.
Check your code again and change the repeated key to something unique.
"""
    ]
