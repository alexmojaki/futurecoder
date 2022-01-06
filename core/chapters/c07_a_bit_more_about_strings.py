# flake8: NOQA E501
import ast
from typing import List
from core.text import ExerciseStep, VerbatimStep, Page, Step, Disallowed


class SingleAndDoubleQuotesInStrings(Page):
    title = "Single and Double Quotes in Strings"

    class single_quotes_apostrophe(Step):
        """
We have been defining strings using single quotes up until now, like:

    name = 'Alice'

What happens if we want to define a string that contains an apostrophe? Try this:

__program_indented__
        """

        program = "print('Alice's Diner')"

        def check(self):
            return self.input.count("'") == 3 and "SyntaxError" in self.result

    class double_quotes(VerbatimStep):
        """
So we can't use an apostrophe as we like in a string with single quotes.
The apostrophe counts as a single quote and therefore acts as a *closing quote* of a string definition `'Alice'`.
Then the remaining text `s Diner'` is invalid syntax and Python does not understand it.

Thankfully Python allows us to define strings in another way, using double quotes `"` instead:

__program_indented__
        """

        program = '''print("Alice's Diner")'''

    class single_double_quotes_equal(VerbatimStep):
        """
Remember that quotes are just part of the human notation for strings.
They are not stored as an actual part of the string.
Try this in the shell:

__program_indented__
        """

        expected_code_source = "shell"

        program = """'Alice' == "Alice" """
        predicted_output_choices = ["True", "False"]

    class double_quote_exercise(VerbatimStep):
        """
As you can see Python considers the same string defined by single or double quotes as the same.

Now write a program that prints the following text from the Zen of Python:

    __copyable__
    Special cases aren't special enough to break the rules.

The program should be a single line using `print()`, no variables.
        """

        hints = """
How should you define the string?
With single quotes, or with double quotes?
You only need one string.
No need to add strings together.
        """

        program_in_text = False

        def program(self):
            print("Special cases aren't special enough to break the rules.")

    class single_quote_exercise(VerbatimStep):
        """
Excellent!

Now print the following quote exactly (including the double quotes):

    __copyable__
    "Talk is cheap. Show me the code." - Linus Torvalds

The program should be a single line using `print()`, no variables.
        """

        hints = """
Think simple! How would you normally do this?
If a string contains a single quote, we must use double quotes to define it.
What if the string contains double quotes?
        """

        program_in_text = False

        def program(self):
            print('"Talk is cheap. Show me the code." - Linus Torvalds')

    final_text = """
Good job!

In most cases you can use either single or double quotes to define your strings, however you like it.
But if your string contains `'` then use `"` to define it and vice versa.
        """


class IntroducingFstrings(Page):
    title = "f-strings"

    class introduce_f_strings(VerbatimStep):
        """
So far we have been combining strings by concatenating them using `+`, like:

    __copyable__
    name = "Alice"
    friend = 'Bob'
    meal = "lunch"
    print(name + " went to " + meal + " with " + friend + '.')

However this gets a bit cumbersome. We can write the same thing more elegantly using an *f-string*.
Replace the last line of the program above with the line below and run it.
Make sure you include the `f` before the string.

    print(f"{name} went to {meal} with {friend}.")
        """

        program_in_text = False
        # TODO message: catch forgetting the f

        def program(self):
            name = "Alice"
            friend = 'Bob'
            meal = "lunch"
            print(f"{name} went to {meal} with {friend}.")

        predicted_output_choices = [
            'f"{name} went to {meal} with {friend}."',
            '"{name} went to {meal} with {friend}."',
            '{name} went to {meal} with {friend}.',
            "'name' went to 'meal' with 'friend'.",
            'name went to meal with friend.',
            '''"Alice" went to "lunch" with 'Bob'.''',
            ''''Alice' went to 'lunch' with 'Bob'.''',
            '"Alice went to lunch with Bob."',
            'Alice went to lunch with Bob.',
        ]

    class concatenate_string_number(VerbatimStep):
        """
The syntax of an f-string starts with `f` followed by a string.
The f-string can contain names of variables inside curly brackets `{}`.
They will be replaced with the values of those variables converted to strings.
The variables can be anything: strings, numbers, lists, etc.

Therefore f-strings let you easily combine strings and numbers, which can't
just be added together. For example run the following program:

    __copyable__
    __program_indented__
        """

        predicted_output_choices = [
            '"Hello " + name + ". You are " + age + " years old."',
            'Hello name. You are age years old.',
            'Hello Alice. You are 20 years old.',
            "Hello 'Alice'. You are 20 years old.",
        ]
        correct_output = "Error"

        # noinspection PyTypeChecker
        def program(self):
            name = "Alice"
            age = 20
            print("Hello " + name + ". You are " + age + " years old.")

    class basic_f_string_exercise(VerbatimStep):
        """
This fails because we cannot use `+` between the string `"Hello Alice. You are "` and the number `age`.

Fix this by replacing all the string concatenations (+) with a single f-string.
        """

        hints = """
This is just like the given f-string example.
Did you forget the `f`?
How many pairs of curly brackets do you need?
        """

        program_in_text = False

        # TODO message: catch forgetting the f

        def program(self):
            name = "Alice"
            age = 20
            print(f'Hello {name}. You are {age} years old.')

    class eval_expr_inside_f_string(VerbatimStep):
        """
In addition to variables, an f-string can actually contain any Python expression inside curly brackets.
Try this in the shell:

__program_indented__
        """

        expected_code_source = "shell"

        program = 'f"2 * 3 + 4 is equal to {2 * 3 + 4}"'

    class fix_broken_program(ExerciseStep):
        """
As you can see we can define an f-string using double quotes too, like we can a normal string.
And like quotes, f-strings are just notation. Once they are evaluated the computer forgets
that an f-string was used, it just stores the final result as a normal string.

Here is a very broken program:

    __copyable__
    people = ["Alice", "Bob", "Charlie"]
    print('There are' + people.length() + 'people waiting, the first one's name is' + people.1 + '.')

Fix it!
Your solution should work for any list of strings named `people`.
For example, in the above case it should print:

    There are 3 people waiting, the first one's name is Alice.
        """

        hints = """
There are four problems with the expression inside `print`.
There is a problem with the syntax that finds the number of people.
Then one of the strings has a problem with the quotes.
Also there is a problem with the syntax that finds the first person's name.
And you can't add strings and numbers together!
Did you properly use curly brackets in your f-string?
        """

        disallowed = Disallowed(ast.Add, label="`+`")
        # TODO message: catch forgetting the f

        def solution(self, people: List[str]):
            print(f"There are {len(people)} people waiting, the first one's name is {people[0]}.")

        translated_tests = True

        tests = [
            (["Alice", "Bob", "Charlie"],
             "There are 3 people waiting, the first one's name is Alice."),
            (["Dan", "Evelyn", "Frank", "George"],
             "There are 4 people waiting, the first one's name is Dan."),
        ]

    final_text = """
Excellent!

From now on, you are encouraged to use f-strings instead of `+` to build up your strings where possible.
"""
