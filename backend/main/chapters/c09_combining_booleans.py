# flake8: NOQA E501

from typing import List
import random

from main.exercises import assert_equal
from main.text import ExerciseStep, Page, VerbatimStep
from main.utils import returns_stdout


class IntroducingOr(Page):
    class InputAliceBob(VerbatimStep):
        """
We learned about *booleans* (`True` and `False`) when we introduced If statements.
We also learned about comparison operators `==`, `<`, `>`, `<=`, `>=` which return booleans.
Now we want to combine booleans to check for more complex conditions.

Here's a simple example: imagine you have two friends, Alice and Bob.
The function below accepts one parameter, `name`, and checks if the person with the given name is among your friends.
Below its definition, we test the function on three different inputs with `assert_equal` from the previous chapter.
After that, we have an example program that uses this function interactively.
Copy and run the code in the editor:

__program_indented__
        """
        def program(self):
            def is_friend(name):
                if name == "Alice":
                    return True
                elif name == "Bob":
                    return True
                else:
                    return False

            assert_equal(is_friend("Alice"), True)
            assert_equal(is_friend("Bob"), True)
            assert_equal(is_friend("Charlie"), False)

            print("What is your name?")
            your_name = input()
            print("Hello " + your_name + "!")
            if is_friend(your_name):
                print("I have a friend called " + your_name + "!")

    class TrueOrTrue(VerbatimStep):
        """
Let's see if we can do better.
We can combine the `if` and `elif` statements using **`or`**. `or` is a *boolean operator*,
meaning it's an operator (like `+` or `-`) which combines two booleans (`True` or `False`).

The expression `A or B` is `True` if either `A` or `B` is `True`, i.e. if `A` is `True` or `B` is `True`, or both.
It's only `False` if neither `A` nor `B` is `True`, i.e. both are `False`.

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
        return True
    elif name == "Bob":
        return True

with:

    if name == "Alice" or name == "Bob":
        return True

As you can see, `is_friend` will return `True` only when `name` is Alice or Bob.
The `or` is used in between the two booleans `name == "Alice"` and `name == "Bob"`.

Now let's focus completely on the function `is_friend`.
Delete the interactive program that comes after the three tests, and run the code again.
        """
        program_in_text = False

        def program(self):
            def is_friend(name):
                if name == "Alice" or name == "Bob":
                    return True
                else:
                    return False

            assert_equal(is_friend("Alice"), True)
            assert_equal(is_friend("Bob"), True)
            assert_equal(is_friend("Charlie"), False)

    class FurtherImprovement(VerbatimStep):
        """
We can do even better. Notice that

    name == "Alice" or name == "Bob"

is a boolean, and both `return` statements are returning booleans `True` or `False`.
The function returns `True` when `name == "Alice" or name == "Bob"` is `True`,
and it returns `False` when `name == "Alice" or name == "Bob"` is `False`.
So we could simply return the boolean `name == "Alice" or name == "Bob"` itself in both cases!

This is a common pattern for simplifying your code. If you ever find yourself writing code like:

    if x:
        return True
    else:
        return False

where `x` itself is a boolean, you can always simplify this block of code to:

    return x

Now in the editor, make the appropriate simplification as explained above, and run your code again.
        """

        program_in_text = False

        def program(self):
            def is_friend(name):
                return name == "Alice" or name == "Bob"

            assert_equal(is_friend("Alice"), True)
            assert_equal(is_friend("Bob"), True)
            assert_equal(is_friend("Charlie"), False)

    class ACommonMistake(VerbatimStep):
        """
Take careful note of how we wrote the condition:

    return name == "Alice" or name == "Bob"

A common mistake is to write this instead:

    return name == "Alice" or "Bob"

It makes sense if you read it like English: "If `name` is equal to either `"Alice"` or `"Bob"`, then return `True`...".
But Python is not English, and that's not how `or` works.

Replace the `return` line in the code with the above line, and try running it again.
        """
        program_in_text = False

        def program(self):
            def is_friend(name):
                return name == "Alice" or "Bob"

            assert_equal(is_friend("Alice"), True)
            assert_equal(is_friend("Bob"), True)
            assert_equal(is_friend("Charlie"), False)

    class InspectWithBirdseye(ACommonMistake):
        text = """
The second and third tests fail! Our function seems to be doing the wrong thing:
it returns `"Bob"` (a string, not a boolean!) when `name` is `"Bob"` or `"Charlie"`. What is going on?
Try inspecting the code with Bird's Eye. Inspect the `return` statements of each `is_friend` call carefully.
(Use the blue arrow buttons)
        """

        expected_code_source = "birdseye"

    class AnExercise(ExerciseStep):
        """
When we inspect it with Bird's Eye, we can see that:

    name == "Alice" or "Bob"

is not translated into

    name == ("Alice" or "Bob")

the way we think in English, but rather:

    (name == "Alice") or ("Bob")

What then happens is:

- `name == "Alice"` evaluates to `False`,
- `name == "Alice" or "Bob"` evaluates to `"Bob"`, and
-  `return "Bob"` returns the string "Bob", instead of a boolean value, which is what we originally intended.

Perhaps you feel like this:

[![I now have additional questions](https://i.imgur.com/jN57tGt.png)](https://imgur.com/a/icKzI)

The only thing you really need to know is this: Until you know what you're doing, always
make sure you put booleans on both sides of `or`, because it's a boolean operator.
`name == "Alice" or "Bob"` breaks that rule.

If you're curious, the answers are below, but you can skip them if you want.
Make sure to read the Exercise that comes afterwards!

----

> Why does `(name == "Alice") or ("Bob")` equal `"Bob"`? Why does it equal anything? `"Bob"` isn't even a boolean!

The definition "`A or B` is `True` if either `A` or `B` is `True`" was a simplification. It's the easiest
way to think about `or` most of the time, especially for writing `if` statements.
The real definition is that if `A` is true then `A or B` is just `A` (in fact `B` is not even evaluated),
otherwise it's `B`.
You can see for yourself that if `A` and `B` are booleans then the two definitions are equivalent.
In this example `A` is `name == "Alice"` which is `False`, so `A or B` is `B` which is `"Bob"`.

> Why does `if "Bob"` run the body? Again, `"Bob"` isn't a boolean!

Python actually lets you treat anything like a boolean. Most things are equivalent to `True` in this context,
including all strings (such as `"Bob"`) except the empty string which is 'falsy'.

> Is there a better way to write the condition without repeating `name ==` each time?

Yes! In [Functions and Methods for Lists](/course/?page=FunctionsAndMethodsForLists) we mentioned the `in`
operator, which you can use with a list like this:

    return name in ["Alice", "Bob", "Charlie"]

But you can't always get rid of `or` like that.

----

Exercise: A percentage number is valid if it is between 0 and 100 (including 0 and 100).
Using `or`, write a function named `is_valid_percentage`, accepting one number argument `x`,
that checks the validity of a given percentage number:
it should return `True` if the argument `x` is between 0 and 100 (inclusive), return `False` otherwise.

Your function should use `or`, and pass these tests:

    assert_equal(is_valid_percentage(-1), False)
    assert_equal(is_valid_percentage(0), True)
    assert_equal(is_valid_percentage(50), True)
    assert_equal(is_valid_percentage(100), True)
    assert_equal(is_valid_percentage(101), False)

        """
        hints = """
Remember, you can use comparison operators `<, >, <=, >=, ==` to produce booleans.
What are the two conditions on `x` where you should return `False`?
Use an if-else block, and connect the two conditions with `or`.
        """

        def solution():
            def is_valid_percentage(_, x: int):
                if x < 0 or x > 100:
                    return False
                else:
                    return True
            return is_valid_percentage

        tests = {
            -1: False,
            0: True,
            50: True,
            100: True,
            101: False,
        }

    final_text = """
Good job! The typical solution looks like:

    def is_valid_percentage(x):
        if x < 0 or x > 100:
            return False
        else:
            return True
            
"""


class AnExerciseUsingOr(Page):
    title = "Introducing And"

    class TrueAndTrue(VerbatimStep):
        """
Another boolean operator in Python is `and`.
The statement `A and B` is true only if BOTH `A` and `B` are true. Otherwise it's false.
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
Exercise: rewrite the `is_valid_percentage` function from before, using `and` instead of `or`.
It should still work exactly as before, accepting a number parameter `x`, and passing the same tests.
        """
        hints = """
Our solution with `or` first determines if `x` is an invalid percentage, else concludes validity. Using `and` will do this in reverse.
You will have to reverse the `return` statements accordingly.
You will have to change the comparison operators too.
        """

        def solution():
            def is_valid_percentage(_, x: int):
                if 0 <= x and x <= 100:
                    return True
                else:
                    return False
            return is_valid_percentage

        tests = {
            -1: False,
            0: True,
            50: True,
            100: True,
            101: False,
        }

    final_text = """
Awesome! A typical solution looks like:

    def is_valid_percentage(x):
        if 0 <= x and x <= 100:
            return True
        else:
            return False
            
As before, we can simplify this solution to:

    def is_valid_percentage(x):
        return 0 <= x and x <= 100

In Python,

    0 <= x and x <= 100

can also be written as a short hand:

    0 <= x <= 100
    
So the solution can be simplified to its final form:

    def is_valid_percentage(x):
        return 0 <= x <= 100
        
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

Write a function `is_winning_row` taking one argument `row` like above (a list of 3 strings),
which prints `We have a winner!` if `row` is a winning row. Otherwise print `Not a winning row.`
        """
        hints = """
There are only two winning rows: ["X", "X", "X"] and ["O", "O", "O"].
You will need to use `and`, `if`, `==` and list indexing.
Check if the three row entries are equal to each other.
You need to make two separate checks using `==`, then connect them using `and`.
                """

        def solution(self):
            def is_winning_row(row: List[str]):
                if row[0] == row[1] and row[0] == row[2]:
                    print("We have a winner!")
                else:
                    print("Not a winning row.")
            return is_winning_row

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

    def is_winning_row(row):
        if row[0] == row[1] and row[0] == row[2]:
            print("We have a winner!")
        else:
            print("Not a winning row.")

Another one is by using a list of the winning lists to do the check:

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

which evaluates to `True` (what's in parentheses will be evaluated first).

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
Our code for checking a tic-tac-toe board for a winning row will get quite long.
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
For each row, we can reuse our row-checking code from before
(with parentheses around it):

    (row[0] == row[1] and row[0] == row[2])

To fit all 3 row checks on multiple lines,
we need one extra set of parentheses around the whole thing, after `if`.
We break lines after the boolean operators `or` which are connecting the bigger blocks.
Type and run this code, make sure you understand the complex boolean expression:

__program_indented__
        """
        def program(self):
            def is_winning_board(row1, row2, row3):
                if (
                    (row1[0] == row1[1] and row1[0] == row1[2]) or
                    (row2[0] == row2[1] and row2[0] == row2[2]) or
                    (row3[0] == row3[1] and row3[0] == row3[2])
                ):
                    print("We have a winner!")

            row1 = ["X", "O", "X"]
            row2 = ["X", "X", "X"]
            row3 = ["O", "O", "X"]

            is_winning_board(row1, row2, row3)

    class DiagonalWinnerExercise(ExerciseStep):
        """
Exercise: write a function `diagonal_winner` to check if there's a diagonal winner on a tic-tac-toe board.
As before, the board is given as 3 rows: `row1, row2, row3`, which the function takes as arguments.
Print out `X wins!` or `O wins!` depending on which player has a winning diagonal.
Otherwise print `No winners.`
For example, if

    row1 = ["X", "O", "X"]
    row2 = ["X", "X", "O"]
    row3 = ["O", "O", "X"]

then `diagonal_winner(row1, row2, row3)` should print `X wins!`
        """
        hints = """
How many diagonals are there on the board? What do they have in common?
Which entries of `row1, row2, row3` make up each diagonal?
Similar to how we checked a row, check that the 3 entries on a diagonal are equal to each other, using `and`.
Similar to how we checked three rows together, check the two diagonals together, using `or`.
As before, use a multi-line boolean expression where `if` contains lines that are connected with `or`. Only 2 lines 
needed.
Don't forget the `else` part!
        """

        def solution():
            @returns_stdout
            def diagonal_winner(_, row1: List[str], row2: List[str], row3: List[str]):
                middle = row2[1]
                if (
                    (middle == row1[0] and middle == row3[2]) or
                    (middle == row1[2] and middle == row3[0])
                ):
                    print(middle + " wins!")
                else:
                    print("No winners.")
            return diagonal_winner

        @classmethod
        def generate_inputs(cls):
            return {
                "row1": [random.choice(["X", "O"]) for _ in range(3)],
                "row2": [random.choice(["X", "O"]) for _ in range(3)],
                "row3": [random.choice(["X", "O"]) for _ in range(3)]
            }

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


    final_text = """
Well done! This was a hard one. One possible solution looks like this:

    def diagonal_winner(row1, row2, row3):
        middle = row2[1]
        if (
            (middle == row1[0] and middle == row3[2]) or
            (middle == row1[2] and middle == row3[0])
        ):
            print(middle + " wins!")
        else:
            print("No winners.")
"""


class IntroducingNotPage(Page):
    title = "Introducing Not"

    class IntroducingNot(VerbatimStep):
        """
Unlike the other two boolean operators `and` and `or`,
which are used in between two booleans (called *binary* operators),
`not` is used before only one boolean (called a *unary* operator).
It negates the expression to which it is applied, a bit like a minus sign. Try in the shell:

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
