from linting import lint

if __name__ == '__main__':
    code_unused_import = """
import random

def write_to_file(text, filename):
    with open("log.txt", "w") as file:
        file.write(text)

"""
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
    code_is_literal = """
x='a'
'aa' is x*2

"""
    code_redefined_while_unused = """
def is_positive(number: int) -> bool:
    return number > 0


def is_positive(number: int) -> bool: 
    return number >= 0

"""
    code_import_shadowed_by_loop_var = """
import pandas as pd

x=[1,2,3]
for pd in x:
    print(pd)

"""
    code_import_star = """
from base import *
print(BaseThing('hi'))
"""

    code_import_star_not_permitted = """
def f():
    from module import *
"""

    code_duplicate_argument = """
def format_name(first_name, last_name, first_name='Grant'):
    pass
"""

    code_multi_value_repeated_key = """
my_dict={'a':1,'b':4,'b':2}

"""

    for x in lint(code_unused_var):
        print(x)