# flake8: NOQA E501
from typing import List
from main.text import ExerciseStep, VerbatimStep, Page, Step


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
    title = "Introducing f-strings"

    class concatenate_string_number(VerbatimStep):
        """
So far we have been combining strings by concatenating them using `+`, like:

    name = "Alice"
    friend = 'Bob'
    meal = "lunch"
    print(name + " went to " + meal + " with " + friend + '.')

However this gets a bit cumbersome and it does not let us easily combine strings and numbers.
For example run the following program:

    __copyable__
    __program_indented__
        """

        def program(self):
            name = "Alice"
            age = 20
            print("Hello " + name + ". You are " + age + " years old.")

    class introduce_f_strings(VerbatimStep):
        """
This fails because we cannot use `+` between the string `". You are "` and the number `age`.
Thankfully Python allows us to overcome this with *f-strings*.
The syntax of an f-string starts with `f` followed by a string:

    name = "Alice"
    print(f'Hello {name}!')

The string can contain names of variables inside curly brackets `{}`.
When printed, they will be replaced with the values of those variables.
The variables can be strings, or even numbers!

As an exercise, fix the last line of the previous program in the editor by using an f-string.
        """

        hints = """
This is just like the given f-string example.
Did you forget the `f`?
How many pairs of curly brackets do you need?
        """

        program_in_text = False

        def program(self):
            name = "Alice"
            age = 20
            print(f'Hello {name}. You are {age} years old.')

    class eval_expr_inside_f_string(VerbatimStep):
        """
In addition to variables, an f-string can also contain Python expressions to be evaluated inside curly brackets.
We can evaluate an f-string in the shell like any other expression. Run this line in the shell:

__program_indented__
        """

        expected_code_source = "shell"

        program = 'f"{2 * 3 + 4}"'

    class fix_broken_program(ExerciseStep):
        """
As you can see we can define an f-string using double quotes too, like we can a normal string.
Moreover numbers that are calculated inside an f-string are then converted to strings.

Here is a broken program:

    people = ["Alice", "Bob", "Charlie"]
    print('There are' + people.length() + 'people waiting, the first one's name is' + people.1 + '.')

Fix this by using an f-string and correcting the wrong syntax.
Your solution should work for any list of strings named `people`.
It should print the correct number of people in the list, and the name of the first person in the list.
It should also have proper spacing between words. For example, in the above case it should print:

    There are 3 people waiting, the first one's name is Alice.
        """

        hints = """
There are three problems with the expression inside `print`.
There is a problem with the syntax that finds the number of people.
Then one of the strings has a problem with the quotes.
Also there is a problem with the syntax that finds the first person's name.
Did you forget to properly use curly brackets in your f-string?
        """

        # TODO: disallow bad solution using + and str(): 'There are ' + str(len(people)) + ...
        def solution(self, people: List[str]):
            print(f"There are {len(people)} people waiting, the first one's name is {people[0]}.")

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
