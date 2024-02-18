# flake8: NOQA E501
import ast
import random
from textwrap import dedent

import pure_eval

from core.text import ExerciseStep, Page, Step, VerbatimStep, Disallowed


class IntroducingIfStatements(Page):
    class introducing_booleans(VerbatimStep):
        """
Now we're going to learn how to tell the computer to make decisions and only run code
under certain conditions. For this we will need a new type of value. You've seen
numbers and strings, now meet *booleans*. There are only two boolean values:
`True` and `False`. Try this program:

__program_indented__
        """

        def program(self):
            condition = True
            print(condition)
            condition = False
            print(condition)

    class first_if_statements(VerbatimStep):
        """
Booleans are meant to be used inside *if statements* (sometimes also called *conditionals*).

Here is a simple example for you to run:

__program_indented__
        """

        # noinspection PyUnreachableCode
        def program(self):
            if True:
                print('This gets printed')

            if False:
                print('This does not')

    class excited_example(VerbatimStep):
        """
Note how the code inside the first `if` statement ran, but not the second.

In general, an `if` statement looks like this:

    if <condition>:
        <body>

where `<condition>` is any expression which evaluates to a boolean and `<body>` is an **indented** list
of one or more statements. The structure is quite similar to a `for` loop. Note the colon (`:`) which
is essential.

When the computer sees `if <condition>:`, it checks if `<condition>` is `True`. If it is, it runs the body.
If not, it skips it and continues to the rest of the program.

Here's a more interesting example for you to run:

__program_indented__
        """

        predicted_output_choices = [
            'Hello World',
            'Hello World!',
        ]

        def program(self):
            sentence = 'Hello World'
            excited = True
            if excited:
                sentence += '!'
            print(sentence)

    class excited_false_example(VerbatimStep):
        """
(Remember that `sentence += '!'` means `sentence = sentence + '!'`)

Change `excited = True` to `excited = False` and run the program again to see what the difference is.
        """
        program_in_text = False

        requirements = "Run the program from the previous step, but replace `True` with `False`, so `excited = False`."

        predicted_output_choices = [
            'Hello World',
            'Hello World!',
        ]

        def program(self):
            sentence = 'Hello World'
            excited = False
            if excited:
                sentence += '!'
            print(sentence)

    class excited_confused_exercise(ExerciseStep):
        """
Time for an exercise. Modify the program above to include an extra
boolean parameter `confused`, so the program should start like this:

    sentence = 'Hello World'
    excited = False
    confused = True

(`sentence` can be any string and the two booleans can be either `True` or `False`)

When `confused` is true, the printed sentence should have a question mark added to the end.
If both `confused` and `excited` are true, the sentence should end with `!?`.
        """

        hints = """
You only need to add a few lines to the existing program. All the existing code should be left as is.
The code that you add should be very similar to the existing code.
        """

        def solution(self, sentence: str, excited: bool, confused: bool):
            if excited:
                sentence += '!'
            if confused:
                sentence += '?'
            print(sentence)

        tests = {
            ('Hello', True, True): 'Hello!?',
            ('Hello there', True, False): 'Hello there!',
            ("I'm bored", False, False): "I'm bored",
            ('Who are you', False, True): 'Who are you?',
        }

    final_text = """
Well done! This program can do 4 different things depending on how you combine `excited`
and `confused`. Try them out if you want.
"""


class CombiningCompoundStatements(Page):
    class for_inside_if(VerbatimStep):
        """
Compound statements like `for` loops and `if` statements have bodies which are a list
of inner statements. Those inner statements can be anything, including other compound statements.
Try this example of a `for` loop inside an `if` statement for when you want to show
that you're *really* excited:

__program_indented__
        """
        predicted_output_choices = [
            'Hello World',
            '!!!!!!!!!!!',
            'Hello World!!!!!!!!!!!',
            '!!!!!!!!!!!Hello World',
            'Hello World!',
            '!Hello World',
            '!Hello World!',
            'H!e!l!l!o! !W!o!r!l!d!',
            '!H!e!l!l!o! !W!o!r!l!d',
        ]

        def program(self):
            sentence = 'Hello World'
            excited = True

            if excited:
                new_sentence = ''
                for char in sentence:
                    new_sentence += char + '!'
                sentence = new_sentence

            print(sentence)

    final_text = """
Note how the body of the `if` statement (4 lines) is indented as usual, while the body
of the `for` loop (1 line) is indented by an additional 4 spaces in each line to show that
those lines are within the `for` loop. You can see the overall structure of the program
just by looking at the indentation.

Alternatively, you can put an `if` inside a `for`:

    __copyable__
    sentence = 'Hello World'
    excited = True

    new_sentence = ''
    for char in sentence:
        new_sentence += char
        if excited:
            new_sentence += '!'

    sentence = new_sentence
    print(sentence)

These two programs have the exact same result. However the first one is more efficient as it
only iterates over the string if it needs to, since when `excited = False` nothing changes.
        """


class print_tail_base(VerbatimStep):
    def program(self):
        sentence = 'Hello World'

        include = False
        new_sentence = ''
        for char in sentence:
            if include:
                new_sentence += char
            include = True

        print(new_sentence)


class UnderstandingProgramsWithSnoop(Page):
    title = "Understanding Programs With `snoop`"

    class print_tail(print_tail_base):
        """
Run this program:

    __copyable__
    __program_indented__
        """
        predicted_output_choices = [
            'Hello World',
            'ello World',
            'Hello Worl',
            'H',
            'd',
        ]

    class print_tail_snoop(print_tail_base):
        """
Programs are starting to get complicated!
It's time to introduce a new tool to help you understand programs. Click the `snoop` button to run the same program while also showing what's happening.
        """

        program_in_text = False
        expected_code_source = "snoop"
        requirements = "Run the same program from the previous step, but use the `snoop` button instead of the 'Run' button. " \
                       "Copy the program again if you might have changed it."

    class print_first_character(ExerciseStep):
        """
Tada! Scroll to the top of the terminal and let's walk through what `snoop` is showing you.
It starts out very straightforward:

        1 | sentence = 'Hello World'
        3 | include = False
        4 | new_sentence = ''
        5 | for char in sentence:
     ...... char = 'H'

The first lines are simply showing you the lines of the program that the computer ran.
On the left is the line number as seen in the editor.

Running `for char in sentence:` assigns a value to the variable `char`, so `snoop` shows you that value.
Lines starting with `......` indicate a new variable or a change in the value of an existing variable.
Such lines will not be shown when they're redundant, which is why the `snoop` output doesn't start like this:

        1 | sentence = 'Hello World'
     ...... sentence = 'Hello World'
        3 | include = False
     ...... include = False
        4 | new_sentence = ''
     ...... new_sentence = ''
        5 | for char in sentence:
     ...... char = 'H'

The next two lines are:

        6 |     if include:
        8 |     include = True

What's important here is what's not showing: because `include` is `False`, line 7 (`new_sentence += char`) gets skipped. But then `include` is set to `True`, so the next iteration of the loop is different:

        5 | for char in sentence:
     ...... char = 'e'
        6 |     if include:
        7 |         new_sentence += char
     .............. new_sentence = 'e'

`new_sentence += char` runs for the first time and the variable `new_sentence` gets a new value.

Now modify the program to do the opposite: only print the first character, leave out the rest.
        """

        hints = """
The code should be almost exactly the same, just make a couple of small changes.
Make sure that the code inside `if include:` runs at the beginning of the loop, in the first iteration.
That means `include` should be `True` at that point.
Make sure that the code inside `if include:` *doesn't* run after the first iteration.
That means `include` should be `False` after the first iteration.
        """

        parsons_solution = True

        def solution(self, sentence: str):
            include = True
            new_sentence = ''
            for char in sentence:
                if include:
                    new_sentence += char
                include = False

            print(new_sentence)

        tests = {
            'Hello there': 'H',
            'Goodbye': 'G',
        }

    final_text = """
Great job! You're working with increasingly complex programs.
"""


class IfAndElse(Page):
    title = "`if` and `else`"

    class first_if_else(VerbatimStep):
        """
An `if` statement can optionally have an `else` part. Run this example:

__program_indented__
        """

        def program(self):
            condition = True
            if condition:
                print('Yes')
            else:
                print('No')

    class first_if_else_false(VerbatimStep):
        """
Now change the first line to `condition = False` and run it again.
        """
        program_in_text = False
        requirements = "Run the same program from the previous step, but replace `True` with `False`, so that `condition = False`."

        def program(self):
            condition = False
            if condition:
                print('Yes')
            else:
                print('No')

    class if_upper_else_lower(VerbatimStep):
        """
Think of `else` as saying 'or else' or 'otherwise'. It means that if the condition in the `if`
is false, then the body of the `else` will run instead. Whether the condition is true or false,
exactly one of the two bodies will run.

Here's a more interesting example to run:

__program_indented__
        """

        def program(self):
            sentence = 'Hello World'
            excited = True
            if excited:
                sentence = sentence.upper()
            else:
                sentence = sentence.lower()
            print(sentence)

    class if_upper_else_lower_false(VerbatimStep):
        """
`sentence.upper()` is a new kind of expression we haven't encountered yet. What's going on here is that `sentence` is a string and strings have various *methods* that let you conveniently calculate new values from them, including `upper` and `lower`. The names refer to uppercase (capital letters) and lowercase (small letters). `'Hello World'.upper()` evaluates to `'HELLO WORLD'`. It doesn't change the contents of `sentence` though, so you have to assign the new value again with `sentence = sentence.upper()`.

Now change `excited` to `False` and run it again.
        """
        program_in_text = False
        requirements = "Run the same program from the previous step, but replace `True` with `False`, so that `excited = False`."

        def program(self):
            sentence = 'Hello World'
            excited = False
            if excited:
                sentence = sentence.upper()
            else:
                sentence = sentence.lower()
            print(sentence)

    class undefined_char(VerbatimStep):
        """
Here's a broken program:

    __copyable__
    sentence = 'Hello World'
    excited = True

    if excited:
        char = '!'
    sentence += char

    print(sentence)

Can you see the problem? If you run it, everything seems fine. What could go wrong?

Spoilers below! Have you figured it out?

What happens if you change `excited` to `False`?
        """
        program_in_text = False
        requirements = "Copy the program above. Run it as is if you want. Then change `excited = True` to `excited = False` and run it again."

        predicted_output_choices = [
            'Hello World',
            'Hello World!',
        ]
        correct_output = "Error"

        # noinspection PyUnboundLocalVariable
        def program(self):
            sentence = 'Hello World'
            excited = False

            if excited:
                char = '!'
            sentence += char

            print(sentence)

    class else_full_stop(ExerciseStep):
        """
If `excited` is true then `char` is defined and everything runs fine. But otherwise
`char` never gets assigned a value, so trying to use it in `sentence += char` fails.

Fix this by adding an `else` clause to the `if` so that if `excited` is false, a full stop (`.`)
is added to the end of the sentence instead of an exclamation mark (`!`).
        """

        hints = """
Don't change anything that's already there, just add a bit more code.
`else` needs to come immediately after the `if` body, with nothing in between.
`sentence += char` needs to run whether `excited` is `True` or `False`.
You *could* have a copy of `sentence += char` in both the `if` and `else` blocks, but there's a better way.
Use `else` to assign a different value to `char`.
If `excited` is `False`, then `char` should be `'.'` instead of `'!'`.
"""

        parsons_solution = True

        def solution(self, sentence: str, excited: bool):
            if excited:
                char = '!'
            else:
                char = '.'
            sentence += char

            print(sentence)

        tests = {
            ('Hello there', True): 'Hello there!',
            ('Goodbye', False): 'Goodbye.',
        }

    class capitalise(ExerciseStep):
        """
Time for a challenge!

Write a program which, given a string `sentence`, prints a modified version with
the same letters, where the first letter is capitalised and the rest are lowercase.
For example, the output should be `Hello world` whether the input `sentence = 'hello world'`
or `'HELLO WORLD'`.
        """

        hints = """
You've learned all the tools you need for this. I believe in you! Look at previous programs for inspiration.
You will need a loop to build up the new sentence character by character.
You will need an `if/else` to choose whether to add an uppercase or lowercase character.
Your `if/else` needs to execute different bodies depending on which iteration of the loop it's in.
That means that your `if` condition needs to be a variable that changes inside the loop.
In the first iteration you need an uppercase letter. In the following iterations you need a lowercase letter.
        """

        parsons_solution = True

        def solution(self, sentence: str):
            upper = True
            new_sentence = ''
            for char in sentence:
                if upper:
                    char = char.upper()
                else:
                    char = char.lower()
                new_sentence += char
                upper = False

            print(new_sentence)

        tests = {
            'HELLO THERE': 'Hello there',
            'goodbye': 'Goodbye',
        }

        disallowed = [
            Disallowed(ast.For, max_count=1, label="`for`"),
            Disallowed(ast.If, max_count=1, label="`if/else`"),
        ]

    class spongebob(ExerciseStep):
        """
Excellent!!!

One more exercise, and then you can relax.

Write a program which prints `sentence` mockingly, e.g:

    OnE MoRe eXeRcIsE, aNd tHeN YoU CaN ReLaX.

Every second character should be lowercased, the rest should be uppercase.
        """

        hints = """
This is similar to the previous exercise. The difference is when and where you set the condition variable.
You will need to have a boolean variable which changes with every iteration.
First write a small program which takes a boolean variable and flips it, i.e. if the variable is `True` it becomes `False` and if it starts out `False` it's changed to `True`. No loops, just an `if/else`.
You will need to use the variable in the `if` condition and also assign to the same variable in the body.
Combine that flipping `if/else` with the one that chooses an uppercase or lowercase character.
        """

        parsons_solution = True

        def solution(self, sentence: str):
            upper = True
            new_sentence = ''
            for char in sentence:
                if upper:
                    char = char.upper()
                    upper = False
                else:
                    char = char.lower()
                    upper = True
                new_sentence += char

            print(new_sentence)

        tests = {
            'One more exercise, and then you can relax.': 'OnE MoRe eXeRcIsE, aNd tHeN YoU CaN ReLaX.',
        }

        disallowed = [
            Disallowed(ast.For, max_count=1, label="`for`"),
            Disallowed(ast.If, max_count=1, label="`if/else`"),
        ]

    final_text = """
Perfect! Take a moment to be proud of what you've achieved. Can you feel your brain growing?
"""


class TheEqualityOperator(Page):
    class introducing_equality(VerbatimStep):
        """
There are several ways to obtain booleans without assigning them directly,
which allows you to construct very useful `if` statements. In particular there
are many *comparison operators* which compare the values of two expressions.
The most common is the equality operator which checks if two values are equal.
It's denoted by two equals signs: `==`. Try running this:

__program_indented__
        """

        def program(self):
            print(1 + 2 == 3)
            print(4 + 5 == 6)
            print('ab' + 'c' == 'a' + 'bc')

    class equality_vs_assignment(Step):
        """
As you can see, if the values are equal, the equality expression evaluates to `True`,
otherwise it's `False`.

Note the difference between the equality operator `==` and a single `=` which has different meanings,
particularly in assignment statements as you've seen them so far. What happens if you try
removing a single `=` from the previous program?
        """

        program = "print(1 + 2 = 3)"

        requirements = "Run the program from the previous step, but replace any of the `==` with just `=`."

        def check(self):
            return "SyntaxError" in self.result

    class if_equals_replacing_characters(VerbatimStep):
        """
Let's use `==` in an `if` statement. In this program, the `if` body runs only when `c` is the character `'s'`. See for yourself.

    __copyable__
    __program_indented__
        """

        def program(self):
            name = 'kesha'
            new_name = ''
            for c in name:
                if c == 's':
                    c = '$'
                new_name += c

            print(new_name)

    class if_equals_replacing_characters_exercise(ExerciseStep):
        """
Now extend the program to also replace `e` with `3` and `a` with `@`.
        """

        hints = """
You just need to add a few lines of code that are very similar to existing ones.
"""

        parsons_solution = True

        def solution(self, name: str):
            new_name = ''
            for c in name:
                if c == 'e':
                    c = '3'
                if c == 's':
                    c = '$'
                if c == 'a':
                    c = '@'
                new_name += c

            print(new_name)

        tests = {
            "kesha": "k3$h@",
            "alex": "@l3x",
        }

    final_text = "Well done!"


class IntroducingElif(Page):
    title = "Introducing `elif`"

    class dna_example(VerbatimStep):
        """
Quick biology lesson! Most of the cells in your body contain your full genetic code in DNA.
This consists of strands of molecular units called nucleobases which come in four varieties:
Adenine, Cytosine, Guanine, and Thymine, or ACGT for short.
So part of a single strand might be something like:

    AGTAGCGTCCTTAGTTACAGGATGGCTTAT...

This will be paired with another strand where A is replaced by T and vice versa,
and C is replaced by G and vice versa, e.g:

    TCATCGCAGGAATCAATGTCCTACCGAATA...

The two strands are 'zipped' together into the famous double helix structure,
joined by the matching A-T and C-G pairs. These pairings are essential in copying DNA when
cells divide and reproduce. The double helix is unzipped and the code is transcribed
into its opposite version to make the copy.

We're going to repeat that process. Let's try the same kind of program we just wrote:

    __copyable__
    __program_indented__
        """

        def program(self):
            dna = 'AGTAGCGTC'
            opposite_dna = ''
            for char in dna:
                if char == 'A':
                    char = 'T'
                if char == 'T':
                    char = 'A'
                if char == 'G':
                    char = 'C'
                if char == 'C':
                    char = 'G'
                opposite_dna += char

            print(opposite_dna)

    class dna_example_with_else(ExerciseStep):
        """
Oh dear, that doesn't quite work. `T` is changed to `A` but `A` isn't changed to anything.
Can you see why?

When `char == 'A'`, then the body `char = 'T'` does indeed run. But that means that the following
condition `char == 'T'` also passes and so `char = 'A'` and we're back where we started.
We need to only change `char` from `T` to `A` if `char` wasn't already `A` to begin with,
meaning `char == 'A'` was `False`. We can do that with an `else`, like so:

    if char == 'A':
        char = 'T'
    else:
        if char == 'T':
            char = 'A'

Now fix the program to replace all characters correctly.
        """

        hints = [
            dedent("""
            Change:

                if char == 'A':
                    char = 'T'
                if char == 'T':
                    char = 'A'

            to look like the revised snippet. It's just a small change, do it without copy-pasting.
            """),
            "Now make the same kind of change to the code swapping G and C."
        ]

        parsons_solution = True

        def solution(self, dna: str):
            opposite_dna = ''
            for char in dna:
                if char == 'A':
                    char = 'T'
                else:
                    if char == 'T':
                        char = 'A'
                if char == 'G':
                    char = 'C'
                else:
                    if char == 'C':
                        char = 'G'
                opposite_dna += char

            print(opposite_dna)

        tests = {
            "AGTAGCGTCCTTAGTTACAGGATGGCTTAT": "TCATCGCAGGAATCAATGTCCTACCGAATA",
            "GTGGTGAACATAAGTGGTACGTTAACGGCA": "CACCACTTGTATTCACCATGCAATTGCCGT",
        }

        @classmethod
        def generate_inputs(cls):
            return {
                "dna": "".join(
                    random.choice("ATGC")
                    for _ in range(random.randrange(20, 30))
                )
            }

    class dna_example_with_elif(VerbatimStep):
        """
Brilliant! You have mimicked what your own cells are constantly doing.

An `if` inside an `else` can be replaced by a single keyword `elif`. For example,
the previous code can be changed to this:

    if char == 'A':
        char = 'T'
    elif char == 'T':
        char = 'A'
    elif char == 'G':
        char = 'C'
    elif char == 'C':
        char = 'G'
        """

        requirements = """
Copy the program from the first step on this page, but replace the 4 `if` blocks there with the
combination of `if` and `elif` blocks here. In other words, replace each of the last three `if`s with
`elif`, but leave the first `if` alone.
        """

        program_in_text = False

        def program(self):
            dna = 'AGTAGCGTC'
            opposite_dna = ''
            for char in dna:
                if char == 'A':
                    char = 'T'
                elif char == 'T':
                    char = 'A'
                elif char == 'G':
                    char = 'C'
                elif char == 'C':
                    char = 'G'
                opposite_dna += char

            print(opposite_dna)

    final_text = """
It's common to have a chain of `elif` clauses when you want exactly one of many
bodies to run, like in this case. In general, code like this:

    if X:
        ...
    else:
        if Y:
            ...
        else:
            if Z:
                ...
            else:
                ...

can be rewritten as:

    if X:
        ...
    elif Y:
        ...
    elif Z:
        ...
    else:
        ...

which is both shorter and saves you from unpleasant nested indentation.
The difference is only cosmetic: once the computer runs this code, it can't
tell the difference between the two versions.

Note that `elif`(s) can optionally be followed by one final `else`. We didn't include one
in our DNA example, but we could add one to alert us to any unexpected characters
in the input, or change `elif char == 'C':` to `else:` if we were confident
about the input being valid.
    """


class try_less_than_in_shell(Step):
    comparators_type = None
    expected_code_source = "shell"

    def check(self):
        evaluator = pure_eval.Evaluator(self.console.locals)
        for node in ast.walk(self.tree):
            try:
                if (
                        isinstance(node, ast.Compare) and
                        isinstance(node.ops[0], (ast.Lt, ast.Gt)) and
                        isinstance(evaluator[node.left], self.comparators_type) and
                        isinstance(evaluator[node.comparators[0]], self.comparators_type)
                ):
                    return True
            except pure_eval.CannotEval:
                pass


class OtherComparisonOperators(Page):
    class try_not_equals(VerbatimStep):
        """
The opposite of the equals operator `==` is the *not equals* operator `!=`. If you squint it sort of looks like ≠. It evaluates to `True` when two values are...not equal. Try `__program__` for yourself in the shell.
        """

        program = "1 != 2"

        expected_code_source = "shell"

        predicted_output_choices = ["True", "False"]

    class brokn_kyboard(VerbatimStep):
        """
Here's a cute little program using `!=`:

    __copyable__
    __program_indented__
        """

        def program(self):
            sentence = 'The e key on my keyboard is broken'
            new_sentence = ''
            for c in sentence:
                if c != 'e':
                    new_sentence += c
            print(new_sentence)

    class introducing_less_than(try_less_than_in_shell):
        """
Other handy operators are `<` (less than) and `>` (greater than). For example, `a < b` means "`a` is less than `b`". Try using one of these in the shell to compare two numbers.
        """

        requirements = "Run any code in the shell using either `<` or `>` on two numbers."
        program = "1 < 2"
        comparators_type = int

        hints = """
You only need to run one very small, simple line in the shell.
How would you add two numbers in the shell?
For example, try `123 + 456`
For this exercise you have to do basically that, but compare them instead.
"""

    class comparing_strings(try_less_than_in_shell):
        """
You can also use these operators to compare strings. If you arrange two strings in alphabetical order, the first one is 'less than' the second. See for yourself.
        """

        requirements = "Run any code in the shell using either `<` or `>` on two strings."
        program = "'1' < '2'"
        comparators_type = str

        hints = """
This is almost exactly the same as the previous step, just use strings instead of numbers.
You only need to run one very small, simple line in the shell.
You can also do this by running multiple lines in the shell, first defining variables and then comparing them, but you don't need to, this can be done without variables.
Remember adding two strings in the shell at the beginning of the course?
For example, we did `'hello' + 'world'`
For this exercise you have to do basically that, but compare them instead.
"""

    class grades_example(VerbatimStep):
        """
Here's a practical example of `<` in action for you to try:

__program_indented__

Recall that `elif percentage < 60` after `if percentage < 40` means "if the percentage wasn't less than 40 and also is less than 60", so it will pass for all numbers from 40 to 59 inclusive. Similarly a 'B' is for percentages from 60 to 79, and an 'A' is for any number 80 and up.
        """

        translate_output_choices = False
        predicted_output_choices = ["F", "C", "B", "A"]

        def program(self):
            percentage = 73

            if percentage < 40:
                grade = 'F'
            elif percentage < 60:
                grade = 'C'
            elif percentage < 80:
                grade = 'B'
            else:
                grade = 'A'

            print(grade)

    class min_three_exercise(ExerciseStep):
        """
Now for an exercise: write a program that takes three variables `x1`, `x2`, and `x3`, and prints the value of the smallest one. So for:

    x1 = 30
    x2 = 10
    x3 = 20

it should print `10`.
        """

        hints = """
Try writing a program which prints the smallest of just `x1` and `x2`.
All you need is a few uses of `<`, `if`, and maybe `else`.
"""

        parsons_solution = True

        def solution(self, x1: str, x2: str, x3: str):
            if x1 < x2:
                if x1 < x3:
                    first = x1
                else:
                    first = x3
            else:
                if x2 < x3:
                    first = x2
                else:
                    first = x3
            print(first)

        tests = {
            (1, 2, 3): 1,
            (10, 20, 30): 10,
            (40, 20, 30): 20,
            (40, 50, 30): 30,
            ('Charlie', 'Alice', 'Bob'): 'Alice',
            ('Charlie', 'Bob', 'Alice'): 'Alice',
            ('Alice', 'Charlie', 'Bob'): 'Alice',
        }

    final_text = """
Marvelous!

There are many ways this could be solved. Here's one solution:

    if x1 < x2:
        if x1 < x3:
            first = x1
        else:
            first = x3
    else:
        if x2 < x3:
            first = x2
        else:
            first = x3

    print(first)

Here's another:

    first = x1

    if x2 < first:
        first = x2

    if x3 < first:
        first = x3

    print(first)

These programs (and yours too) all work equally well with numbers and strings. So for:

    x1 = 'Charlie'
    x2 = 'Alice'
    x3 = 'Bob'

they will print `Alice` because that's the first string alphabetically.

`<` and `>` evaluate to False if the compared values are equal. For example,
3 is not less than 3, so `3 < 3` and `3 > 3` are both False.
To allow equal values, use `<=` and `>=`.
Again, if you squint, they look a bit like ≤ and ≥.
Note that the `=` comes second - there are no such operators as `=<` or `=>`.
To remember this, read them out loud as "less than or equal to"
and "greater than or equal to".

In summary, the main comparison operators are `==`, `!=`, `<`, `>`, `<=`, and `>=`.
If you ever have doubts about what they do, play with them in the shell!
"""
