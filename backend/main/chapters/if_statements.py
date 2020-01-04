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

    final_text = """TODO"""
