import ast
import random

from main.exercises import check_result, generate_short_string
from main.text import Page, step
from main.utils import returns_stdout


class IntroducingIfStatements(Page):
    @step("""
Now we're going to learn how to tell the computer to make decisions and only run code
under certain conditions. For this we will need a new type of value. You've seen
numbers and strings, now meet *booleans*. There are only two boolean values:
`True` and `False`. Try this program:

__program_indented__
    """, program="""
condition = True
print(condition)
condition = False
print(condition)
""")
    def introducing_booleans(self):
        return self.matches_program()

    @step("""
Booleans are meant to be used inside *if statements* (sometimes also called *conditionals*).

Here is a simple example for you to run:

__program_indented__
    """, program="""
if True:
    print('This gets printed')

if False:
    print('This does not')
""")
    def first_if_statements(self):
        return self.matches_program()

    @step("""
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
    """, program="""
sentence = 'Hello World'
excited = True
if excited:
    sentence += '!'
print(sentence)
    """)
    def excited_example(self):
        return self.matches_program()

    @step("""
(Remember that `sentence += '!'` means `sentence = sentence + '!'`)

Change `excited = True` to `excited = False` and run the program again to see what the difference is.
""", expected_program="""
sentence = 'Hello World'
excited = False
if excited:
    sentence += '!'
print(sentence)
    """)
    def excited_false_example(self):
        return self.matches_program()

    @step("""
Time for an exercise. Modify the program above to include an extra
boolean parameter `confused`, so the program should start like this:

    sentence = 'Hello World'
    excited = False
    confused = True

(`sentence` can be any string and the two booleans can be either `True` or `False`)

When `confused` is true, the printed sentence should have a question mark added to the end.
If both `confused` and `excited` are true, the sentence should end with `!?`.
    """, hints="""
You only need to add a few lines to the existing program. All the existing code should be left as is.
The code that you add should be very similar to the existing code.
        """)
    def excited_confused_exercise(self):
        @returns_stdout
        def solution(sentence, excited, confused):
            if excited:
                sentence += '!'
            if confused:
                sentence += '?'
            print(sentence)

        def test(func):
            check_result(
                func,
                dict(
                    sentence='Hello',
                    excited=True,
                    confused=True,
                ),
                'Hello!?',
            )

            check_result(
                func,
                dict(
                    sentence='Hello there',
                    excited=True,
                    confused=False,
                ),
                'Hello there!',
            )

            check_result(
                func,
                dict(
                    sentence="I'm bored",
                    excited=False,
                    confused=False,
                ),
                "I'm bored",
            )

            check_result(
                func,
                dict(
                    sentence="Who are you",
                    excited=False,
                    confused=True,
                ),
                "Who are you?",
            )

        def generate_inputs():
            return dict(
                sentence=generate_short_string(),
                excited=random.choice([True, False]),
                confused=random.choice([True, False]),
            )

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    final_text = """
Well done! This program can do 4 different things depending on how you combine `excited`
and `confused`. Try them out if you want.
"""


class CombiningCompoundStatements(Page):
    @step("""
Compound statements like `for` loops and `if` statements have bodies which are a list
of inner statements. Those inner statements can be anything, including other compound statements.
Try this example of a `for` loop inside an `if` statement for when you want to show
that you're *really* excited:

__program_indented__
""", program="""
sentence = 'Hello World'
excited = True

if excited:
    new_sentence = ''
    for char in sentence:
        new_sentence += char
        new_sentence += '!'
    sentence = new_sentence

print(sentence)
""")
    def for_inside_if(self):
        return self.matches_program()

    @step("""
Note how the body of the `if` statement (5 lines) is indented as usual, while the body
of the `for` loop (2 lines) is indented by an additional 4 spaces in each line to show that
those lines are within the `for` loop. You can see the overall structure of the program
just by looking at the indentation.

Alternatively, you can put an `if` inside a `for`:

    sentence = 'Hello World'
    excited = True

    new_sentence = ''
    for char in sentence:
        new_sentence += char
        if excited:
            new_sentence += '!'

    sentence = new_sentence
    print(sentence)

These two programs have the exact same result, although the first one is more efficient since it
only iterates over the string if it needs to, since when `excited = False` nothing changes.

Now run this program:

__program_indented__
""", program="""
sentence = 'Hello World'

include = False
new_sentence = ''
for char in sentence:
    if include:
        new_sentence += char
    include = True

print(new_sentence)
""")
    def print_tail(self):
        return self.matches_program()

    @step("""
As you can see, it prints everything but the first character. Take some time to understand how this works.

Now modify the program to do the opposite: only print the first character, leave out the rest.
    """, hints="""
The code should be almost exactly the same, just make a couple of small changes.
Make sure that the code inside `if include:` runs at the beginning of the loop, in the first iteration.
That means `include` should be `True` at that point.
Make sure that the code inside `if include:` *doesn't* run after the first iteration.
That means `include` should be `False` after the first iteration.
""")
    def print_first_character(self):
        @returns_stdout
        def solution(sentence):
            include = True
            new_sentence = ''
            for char in sentence:
                if include:
                    new_sentence += char
                include = False

            print(new_sentence)

        def test(func):
            check_result(func, dict(sentence='Hello there'), 'H')
            check_result(func, dict(sentence='Goodbye'), 'G')

        def generate_inputs():
            return dict(sentence=generate_short_string())

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    final_text = """
Great job! You're working with increasingly complex programs.
"""


class IfAndElse(Page):
    title = "`if` and `else`"

    @step("""
An `if` statement can optionally have an `else` part. Run this example:

__program_indented__
""", program="""
condition = True
if condition:
    print('Yes')
else:
    print('No')
    """)
    def first_if_else(self):
        return self.matches_program()

    @step("""
Now change the first line to `condition = False` and run it again.
""", expected_program="""
condition = False
if condition:
    print('Yes')
else:
    print('No')
    """)
    def first_if_else_false(self):
        return self.matches_program()

    @step("""
Think of `else` as saying 'or else' or 'otherwise'. It means that if the condition in the `if`
is false, then the body of the `else` will run instead. Whether the condition is true or false,
exactly one of the two bodies will run.

Here's a more interesting example to run:

__program_indented__
""", program="""
sentence = 'Hello World'
excited = True
if excited:
    sentence = sentence.upper()
else:
    sentence = sentence.lower()
print(sentence)
    """)
    def if_upper_else_lower(self):
        return self.matches_program()

    @step("""
`sentence.upper()` is a new kind of expression we haven't encountered yet. What's going on here is that `sentence` is a string and strings have various *methods* that let you conveniently calculate new values from them, including `upper` and `lower`. The names refer to uppercase (capital letters) and lowercase (small letters). `'Hello World'.upper()` evaluates to `'HELLO WORLD'`. It doesn't change the contents of `sentence` though, so you have to assign the new value again with `sentence = sentence.upper()`.

Now change `excited` to `False` and run it again.
""", expected_program="""
sentence = 'Hello World'
excited = False
if excited:
    sentence = sentence.upper()
else:
    sentence = sentence.lower()
print(sentence)
    """)
    def if_upper_else_lower_false(self):
        return self.matches_program()

    @step("""
Here's a broken program:

    sentence = 'Hello World'
    excited = True

    if excited:
        char = '!'
    sentence += char

    print(sentence)

Can you see the problem? If you run it, everything seems fine. What could go wrong?

Spoilers below! Have you figured it out?

What happens if you change `excited` to `False`?
""", expected_program="""
sentence = 'Hello World'
excited = False

if excited:
    char = '!'
sentence += char

print(sentence)
    """)
    def undefined_char(self):
        return self.matches_program()

    @step("""
If `excited` is true then `char` is defined and everything runs fine. But otherwise
`char` never gets assigned a value, so trying to use it in `sentence += char` fails.

Fix this by adding an `else` clause to the `if` so that if `excited` is false, a full stop (`.`)
is added to the end of the sentence instead of an exclamation mark (`!`).
""")
    def else_full_stop(self):
        @returns_stdout
        def solution(sentence, excited):
            if excited:
                char = '!'
            else:
                char = '.'
            sentence += char

            print(sentence)

        def test(func):
            check_result(
                func,
                dict(sentence='Hello there', excited=True),
                'Hello there!',
            )
            check_result(
                func,
                dict(sentence='Goodbye', excited=False),
                'Goodbye.',
            )

        def generate_inputs():
            return dict(sentence=generate_short_string(),
                        excited=random.choice([True, False]))

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    @step("""
Time for a challenge!

Write a program which, given a string `sentence`, prints a modified version with
the same letters, where the first letter is capitalised and the rest are lowercase.
For example, the output should be `Hello world` whether the input `sentence = 'hello world'`
or `'HELLO WORLD'`.
""", hints="""
You've learned all the tools you need for this. I believe in you! Look at previous programs for inspiration.
You will need a loop to build up the new sentence character by character.
You will need an `if/else` to choose whether to add an uppercase or lowercase character.
Your `if/else` needs to execute different bodies depending on which iteration of the loop it's in.
That means that your `if` condition needs to be a variable that changes inside the loop.
In the first iteration you need an uppercase letter. In the following iterations you need a lowercase letter.
""")
    def capitalise(self):
        @returns_stdout
        def solution(sentence):
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

        def test(func):
            check_result(func, dict(sentence='HELLO THERE'), 'Hello there')
            check_result(func, dict(sentence='goodbye'), 'Goodbye')

        def generate_inputs():
            return dict(sentence=generate_short_string())

        return self.check_challenge(solution, test, generate_inputs, functionise=True)

    @step("""
Excellent!!!

One more exercise, and then you can relax. 

Write a program which prints `sentence` mockingly, e.g:

    OnE MoRe eXeRcIsE, aNd tHeN YoU CaN ReLaX.

Every second character should be lowercased, the rest should be uppercase.
""", hints="""
This is similar to the previous exercise. The difference is when and where you set the condition variable.
You will need to have a boolean variable which changes with every iteration. 
First write a small program which takes a boolean variable and flips it, i.e. if the variable is `True` it becomes `False` and if it starts out `False` it's changed to `True`. No loops, just an `if/else`.
You will need to use the variable in the `if` condition and also assign to the same variable in the body.
Combine that flipping `if/else` with the one that chooses an uppercase or lowercase character.
""")
    def spongebob(self):
        @returns_stdout
        def solution(sentence):
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

        def test(func):
            check_result(
                func,
                dict(sentence='One more exercise, and then you can relax.'),
                'OnE MoRe eXeRcIsE, aNd tHeN YoU CaN ReLaX.',
            )

        def generate_inputs():
            return dict(sentence=generate_short_string())

        return self.check_challenge(solution, test, generate_inputs, functionise=True)

    def check_challenge(self, *args, **kwargs):
        result = self.check_exercise(*args, **kwargs)
        if result is True:
            ifs_and_fors = [ 
                sum(isinstance(node, typ) for node in ast.walk(self.tree))
                for typ in [ast.If, ast.For]
            ]
            if max(ifs_and_fors) > 1:
                return dict(
                    message="Well done, this solution is correct! However, it can be improved. "
                            "You only need to use one loop and one `if/else`."
                )
        return result

    final_text = """
Perfect! Take a moment to be proud of what you've achieved. Can you feel your brain growing?
"""
