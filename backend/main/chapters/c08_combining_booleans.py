# flake8: NOQA E501

from typing import List

from main.text import ExerciseStep, Page, VerbatimStep
from main.utils import returns_stdout


class IntroducingOr(Page):
    class InputAliceBob(VerbatimStep):
        """
We learned about *booleans* (`True` and `False`) when we introduced If statements.
We also learned about comparison operators `==`, `<`, `>`, `<=`, `>=` which return booleans.
Now we want to combine booleans to check for more complex conditions.
Type and run this code in the editor:

__program_indented__
        """
        def program(self):
            print("What is your name?")
            name = input()
            print("Hello " + name + "!")
            if name == "Alice":
                print("I have a friend called Alice!")
            if name == "Bob":
                print("I have a friend called Bob!")

    class TrueOrTrue(VerbatimStep):
        """
Let's see if we can do better. We could replace both `print` statements with:

    print("I have a friend called " + name + "!")

We could also combine the two `if` statements into one using **`or`**. `or` is a *boolean operator*,
meaning it's an operator (like `+` or `-`) which combines two booleans (`True` or `False`).

The expression `A or B` is `True` if either `A` or `B` is `True`, i.e. if `A` is `True` or `B` is `True`, or both.
It's only `False` if neither `A` nor `B` is `True`, i.e. both are `False`.

Let's try some examples in the shell.
Try the following in the shell. Think about what you expect it to return:

__program_indented__
        """
        program = "True or True"

    class TrueOrFalse(VerbatimStep):
        """
Good, now try:

__program_indented__

What do you expect?
        """
        program = "True or False"

    class FalseOrFalse(VerbatimStep):
        """
Finally, try:

__program_indented__
        """
        program = "False or False"

    class ImprovingWithOr(VerbatimStep):
        """
In the editor, replace:

    if name == "Alice":
        print("I have a friend called Alice!")
    if name == "Bob":
        print("I have a friend called Bob!")

with:

    if name == "Alice" or name == "Bob":
        print("I have a friend called " + name + "!")

As you can see, our `print` statement will be executed only when the input provided is Alice or Bob.
The `or` is used in between the two booleans `name == "Alice"` and `name == "Bob"`.
Now run the code again. Try different inputs. Try Alice, Bob, or something else.
        """
        program_in_text = False

        def program(self):
            print("What is your name?")
            name = input()
            print("Hello " + name + "!")
            if name == "Alice" or name == "Bob":
                print("I have a friend called " + name + "!")

    class ACommonMistake(VerbatimStep):
        """
A common mistake, although it appears to make sense in English, is to write it like this:

    if name == "Alice" or "Bob":

Replace the `if` line in the code with the above line, and try running it again
with `Charlie` when asked for a name.
        """
        program_in_text = False

        def program(self):
            print("What is your name?")
            name = input()
            print("Hello " + name + "!")
            if name == "Alice" or "Bob":
                print("I have a friend called " + name + "!")

    class InspectWithBirdseye(ACommonMistake):
        """
Our code is not giving errors, but it seems to be doing the wrong thing:
it still prints "I have a friend called..." even when `name` is `Charlie`.
Try inspecting the code with Birdseye. When you click Birdseye, it will first
run the program. When asked for a name, type `Charlie` again and hit Enter.
Then the Birdseye page will pop up. Inspect the `if` statement carefully.
        """

        def check(self):
            return super().check() and self.code_source == "birdseye"

    final_text = """
When we inspect it with Birdseye, we can see that

- `name == "Alice"` evaluates to `False`,
- `name == "Alice" or "Bob"` evaluates to `"Bob"`, and
-  `if "Bob"` triggers the `print` statement

(`if` followed by any non-empty string will be satisfied).

This is because Python evaluates `x or y` to `y` only when `x` is `False`,
which is what happened in this case.
(If `x` is `True`, `y` will not be evaluated.)

Once again, the correct way is:

    if name == "Alice" or name == "Bob":

Alternatively to `or`, we can also accomplish the same result by using a List instead:

    if name in ["Alice", "Bob"]:
"""


class AnExerciseUsingOr(Page):
    title = "Introducing And"

    class AnExercise(ExerciseStep):
        """
Exercise: using `or`, write code that checks the validity of a given percentage number.
A percentage number is valid if it is between 0 and 100 (including 0 and 100).

Given a number `percentage`, your code should print `This percentage is valid.`
if it's valid, `This percentage is not valid.` otherwise.
        """
        hints = """
Remember, you can use comparison operators `<, >, <=, >=, ==` to produce booleans.
        """

        @returns_stdout
        def solution(self, percentage: int):
            if percentage < 0 or percentage > 100:
                print("This percentage is not valid.")
            else:
                print("This percentage is valid.")

        tests = {
            -1: """\
This percentage is not valid.
""",
            0: """\
This percentage is valid.
""",
            50: """\
This percentage is valid.
""",
            100: """\
This percentage is valid.
""",
            101: """\
This percentage is not valid.
""",
        }

    class TrueAndTrue(VerbatimStep):
        """
Good job! The typical solution looks like:

    percentage = 50
    if percentage < 0 or percentage > 100:
        print("This percentage is not valid.")
    else:
        print("This percentage is valid.")

Another boolean operator in Python is `and`.
The statement `A and B` is true only if both `A` and `B` are true.
Try it in the shell:

__program_indented__
        """
        program = "True and True"

    class TrueAndFalse(VerbatimStep):
        """
Good, now try:

__program_indented__

What do you expect?
        """
        program = "True and False"

    class FalseAndFalse(VerbatimStep):
        """
Finally, try:

__program_indented__
        """
        program = "False and False"

    class AndExercise(ExerciseStep):
        """
Exercise: rewrite our percentage checking code, using `and` instead of `or`.
It should still work exactly as before.
        """
        hints = """
Our code with `or` first determines if `percentage` is invalid, else concludes validity. 
Using `and` will do this in reverse.
Change the line with the `if` statement in the code, using `and` to achieve the same logic. 
Then change the `print` statements accordingly.
You will have to change the comparison operators too.
        """

        @returns_stdout
        def solution(self, percentage: int):
            if 0 <= percentage and percentage <= 100:
                print("This percentage is valid.")
            else:
                print("This percentage is not valid.")

        tests = {
            -1: """\
This percentage is not valid.
""",
            0: """\
This percentage is valid.
""",
            50: """\
This percentage is valid.
""",
            100: """\
This percentage is valid.
""",
            101: """\
This percentage is not valid.
""",
        }

    final_text = """
Awesome! A typical solution looks like:

    percentage = 50 
    if 0 <= percentage and percentage <= 100:
        print("This percentage is valid.") 
    else:         
        print("This percentage is not valid.")
        
In Python,

    if 0 <= percentage and percentage <= 100:

can also be written as a short hand: 

    if 0 <= percentage <= 100:

    """


class TicTacToeExercise(Page):
    class TicTacToeWinningRow(ExerciseStep):
        """
Exercise: check if a row of tic-tac-toe represents a winner, using `and`.
If you've never heard of tic-tac-toe, you can read about it
[here](https://en.wikipedia.org/wiki/Tic-tac-toe) and play a few games against a
computer opponent [here](https://playtictactoe.org/).

We will use a list of strings "X" and "O" to represent a row of tic-tac-toe:

    row = ["X", "O", "O"]

Given such a `row`, write code that prints `We have a winner!` if `row` is a winning row.
Otherwise print `Not a winning row.`
        """
        hints = """
There are only two winning rows: ["X", "X", "X"] and ["O", "O", "O"].
You will need to use `and`, `if`, `==` and list indexing.
Check if the three row entries are equal to each other.
                """

        @returns_stdout
        def solution(self, row: List[str]):
            if row[0] == row[1] and row[0] == row[2]:
                print("We have a winner!")
            else:
                print("Not a winning row.")

        tests = [
            (["O", "O", "O"], """\
We have a winner!
"""),
            (["X", "X", "X"], """\
We have a winner!
"""),
            (["O", "X", "O"], """\
Not a winning row.
"""),
            (["O", "O", "X"], """\
Not a winning row.
"""),
            (["X", "O", "O"], """\
Not a winning row.
""")
        ]

    class CombiningAndOr(VerbatimStep):
        """
Good job. There are many possible correct solutions here. One solution:

    row = ["X", "O", "X"]
    if row[0] == row[1] and row[0] == row[2]:
        print("We have a winner!")
    else:
        print("Not a winning row.")

Another one is by using a list of lists:

    if row in [["X", "X", "X"], ["O", "O", "O"]]:

Before we expand this idea to the whole tic-tac-toe board,
let's explore how `and` and `or` interact when combined, using 3 booleans.
Which one has higher priority? Try the following code in the shell.
What do you expect?

__program_indented__
        """
        program = "True or False and False"

    class AndHasHigherPriority(VerbatimStep):
        """
If you read it casually from left to right, you may think:

- `True or False` would evaluate to `True`,
- then it would reduce to `True and False`, which evaluates to `False`.

However, this is not the case! Because `and` has a higher priority in evaluation than `or`, so

    True or False and False

is equivalent to

    True or (False and False)

which evaluates to `True` (what's in parentheses get evaluated first).

So we should always use parentheses to be safe.

Now evaluate in the shell the command:

__program_indented__
        """
        program = "(True or False) and False"

    final_text = """
Therefore we should play it safe and always use parentheses to indicate
which priority we intend with our code when there is ambiguity.
    """


class MultiLineExpressions(Page):
    class TrueOrFalseAndFalse(VerbatimStep):
        """
our code for checking a tic-tac-toe board for a winning row will get quite long.
Thankfully Python allows us to write a single, long expression on multiple lines,
as long as it is within parentheses.
We can go to the next line right after a boolean operator.
Type and run this code in the editor:

    print(True or
    False and
    False)
        """
        program_in_text = False
        program = "print(True or False and False)"

    final_text = """
Remember to always wrap your multi-line expressions inside parentheses to be safe.
    """


class CombiningAndWithOr(Page):
    class CheckTheWholeBoard(VerbatimStep):
        """
The tic-tac-toe board can be represented by 3 rows.
If we have a winning row, it's either row 1, OR row 2, OR row 3.
For each row, we can reuse our row-checking code from above
(with parentheses around it):

    (row[0] == row[1] and row[0] == row[2])

To fit all 3 row checks on multiple lines,
we need one extra set of parentheses around the whole thing, after `if`.
We break lines after the boolean operators `or` which are connecting the bigger blocks.
Type and run this code, also observe the big `if` block with Birdseye to make
sure you understand the complex boolean expression:

__program_indented__
        """
        def program(self):
            row1 = ["X", "O", "X"]
            row2 = ["X", "X", "X"]
            row3 = ["O", "O", "X"]

            if (
                (row1[0] == row1[1] and row1[0] == row1[2]) or
                (row2[0] == row2[1] and row2[0] == row2[2]) or
                (row3[0] == row3[1] and row3[0] == row3[2])
            ):
                print("We have a winner!")

    class DiagonalWinnerExercise(ExerciseStep):
        """
Exercise: write code to check if there's a diagonal winner on a tic-tac-toe board.
As before, the board is given as 3 rows: `row1, row2, row3`.
Print out `X wins!` or `O wins!` depending on which player has a winning diagonal.
Otherwise print `No winners.`
For example, if

    row1 = ["X", "O", "X"]
    row2 = ["X", "X", "O"]
    row3 = ["O", "O", "X"]

then your code should print `X wins!`
        """
        hints = """
How many diagonals are there on the board? What do they have in common?
Which entries of `row1, row2, row3` make up each diagonal?
Similar to how we checked a row, check that the 3 entries on a diagonal are equal to each other.
Similar to how we checked three rows together, check the two diagonals together. 
As before, use a multi-line boolean expression where `if` contains lines that are connected with `or`.
Don't forget the `else` part! 
        """

        @returns_stdout
        def solution(self, row1: List[str], row2: List[str], row3: List[str]):
            middle = row2[1]
            if (
                (middle == row1[0] and middle == row3[2]) or
                (middle == row1[2] and middle == row3[0])
            ):
                print(middle + " wins!")
            else:
                print("No winners.")

        tests = [
            ((["X", "O", "X"], ["X", "X", "O"], ["O", "O", "X"]), """\
X wins!
"""),
            ((["X", "O", "O"], ["X", "O", "X"], ["O", "X", "X"]), """\
O wins!
"""),
            ((["X", "O", "X"], ["X", "O", "X"], ["O", "O", "X"]), """\
No winners.
"""),
        ]

    class IntroducingNot(VerbatimStep):
        """
Well done! This was a hard one. One possible solution looks like this:

    middle = row2[1]
    if (
        (middle == row1[0] and middle == row3[2]) or
        (middle == row1[2] and middle == row3[0])
    ):
        print(middle + " wins!")
    else:
        print("No winners.")

Unlike the other two boolean operators `and` and `or`,
which are used in between two booleans (called *binary* operators),
`not` is used before only one boolean (called a *unary* operator).
It negates the statement to which it is applied. Try in the shell:

__program_indented__
        """
        program = "not True"

    class NotFalse(VerbatimStep):
        """
Now try the following:

__program_indented__
        """
        program = "not False"

    class NotTrueOrTrue(VerbatimStep):
        """
What is the priority of `not` compared to `and` and `or`? Let us turn to the shell again. Evaluate:

    __program_indented__
        """
        program = "not True or True"

    class NotPriority(VerbatimStep):
        """
We see that `not True or True` is interpreted by Python as:

    (not True) or True

which evaluates to `False or True` , which is `True`.
So, `not` has higher priority than `or` if there are no parentheses.
Now run this in the shell:

__program_indented__
        """
        program = "not (True or True)"

    final_text = """
We see that `not (True or True)` evaluates to `not (True)` which is `False`. 
Because of the parentheses, `or` gets evaluated first.
    """
