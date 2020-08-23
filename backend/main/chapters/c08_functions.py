# flake8: NOQA E501
from typing import List

from main.exercises import generate_string
from main.text import ExerciseStep, MessageStep, Page, VerbatimStep
from main.utils import returns_stdout


class DefiningFunctions(Page):
    class define_greet(VerbatimStep):
        """
You've seen how to call functions such as `print()` and `len()`. Now you're going to learn how to write your own
functions that you or other people can use. This is very important as programs get bigger and more complicated.

Here's a simple example:

__program_indented__

This defines a function called `greet` which accepts one parameter. Below the definition, we call the function twice.
Run the code to see what happens.
        """

        def program(self):
            def greet(name):
                print("Hello " + name + "!")

            greet("Alice")
            greet("Bob")

    class how_are_you(VerbatimStep):
        """
A function definition is a compound statement. Like `if` and `for`, it has a header line followed by an indented body
which can contain one or more statements.

Add another statement to the function so that it looks like this:

    def greet(name):
        print("Hello " + name + "!")
        print("How are you?")

Then run the program again.
        """

        program_in_text = False

        def program(self):
            def greet(name):
                print("Hello " + name + "!")
                print("How are you?")

            greet("Alice")
            greet("Bob")

    class print_twice_exercise(ExerciseStep):
        """
Note how the output of the program changed. `How are you?` is printed twice. You can think of the whole program as being
equivalent to this:

    name = "Alice"
    print("Hello " + name + "!")
    print("How are you?")

    name = "Bob"
    print("Hello " + name + "!")
    print("How are you?")

This shows one of the most useful things about functions. They let you reuse the same code multiple times without
having to repeat yourself. It's like writing a program within a program.

The header line of a function definition always has these parts:

1. The special keyword `def`, followed by a space.
2. The name of the function. This is like a variable name - you can choose the name you want, but there are some constraints,
e.g. it can't contain a space.
3. A pair of parentheses `(` and `)`
4. Zero or more parameter names between the parentheses, separated by commas if there's more than one. Here we have
one parameter called `name`.
5. A colon `:`

Here's an exercise: write a function called `print_twice` which accepts one argument `x` and prints that argument twice.

For example, `print_twice("Hello")` should output:

    Hello
    Hello
"""
        # TODO hints

        function_name = "print_twice"

        @returns_stdout
        def solution(self, x: str):
            print(x)
            print(x)

        tests = {
            "Hello": "Hello\nHello\n",
            123: "123\n123\n",
        }

    final_text = """
Well done! You've reached the end for now. More coming soon!
"""
