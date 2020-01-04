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
