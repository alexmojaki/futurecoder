import ast
from .linting import lint


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
**Import `pd` from line '2` shadowed by loop variable**

The name of the loop variable `pd` should be changed in line`2` as it redefines the `pd` module.
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

You imported a module `random` but never used it. Did you forget to use it?
Maybe you used the wrong import in its place? If you don't need it, just remove it entirely.
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

def write_random():
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
**Is literal**

You used the is/is not statement for comparison. You should have rather used the `==` / `!=` statements,
which can be used to compare anything. The is/is not statement checks if objects refer to the same instance 
(address in memory) and should not be used for literals.
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
**Redefined `is_positive` while unused on line `2`**

This error occurs when a function, class or method is redefined.
The function `is_positive` has not been called however it has been redefined on line `2`
Make sure that all functions have different names if they are different. Also remember to call the function.
    """
    ]


def test_import_star():
    code_import_star = """
from base import *
print(BaseThing('hi'))
"""
    assert lint_tree(code_import_star) == [
        """
**Import made using * **

This * import is used to import everything from a designated module under the current 
module, allowing the use of various objects from the imported module- without having to prefix them with the module's 
name. Refrain from using this type of import statement and rather explicitly import a few statements that you may 
require instead.  
"""
    ]


def test_import_star_not_permitted():
    code_import_star_not_permitted = """
def f():
    from module import *
"""
    assert lint_tree(code_import_star_not_permitted) == [
        """
**Import made using * **

This * import is used to import everything from a designated module under the current 
module, allowing the use of various objects from the imported module- without having to prefix them with the module's 
name. Refrain from using this type of import statement and rather explicitly import a few statements that you may 
require instead.
"""
    ]


def test_duplicate_argument():
    code_duplicate_argument = """
def format_name(first_name, last_name, first_name='Grant'):
    pass
"""
    assert lint_tree(code_duplicate_argument) == [
        """
**Duplicate argument `first_name` in function definition**

Two or more parameters in a function definition have the same name.
All names in the function definition should be distinct. Change one of the names so that all parameters are unique.
"""
    ]


def test_multi_value_repeated_key_literal():
    code_multi_value_repeated_key = """
dict={'a':1,'b':2,'a':3}
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
