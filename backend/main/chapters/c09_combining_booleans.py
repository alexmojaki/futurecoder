# flake8: NOQA E501

from typing import List
import random

from main.exercises import assert_equal, generate_string
from main.text import ExerciseStep, Page, VerbatimStep


class IntroducingOr(Page):
    title = "Introducing `or`"

    class InputAliceBob(VerbatimStep):
        """
We learned about *booleans* (`True` and `False`) when we introduced If statements.
We also learned about comparison operators `==`, `<`, `>`, `<=`, `>=` which return booleans.
Now we want to combine booleans to check for more complex conditions.

Here's a simple example: imagine you have two friends, Alice and Bob.
The function below accepts one parameter, `name`, and checks if the person with the given name is among your friends.
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
The function:

 - returns `True` when `name == "Alice" or name == "Bob"` is `True`, and
 - returns `False` when `name == "Alice" or name == "Bob"` is `False`.

So we could simply return the boolean `name == "Alice" or name == "Bob"` itself in both cases!

This is a common pattern for simplifying your code. If you ever find yourself writing code like:

    if x:
        return True
    else:
        return False

where `x` itself is a boolean, you can always simplify this block of code to:

    return x

Apply this simplification to the code yourself, and run it again.
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

It makes sense if you read it like English:

> `return` whether `name` is equal to either `"Alice"` or `"Bob"`

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

which evaluates to `"Bob"` when `name == "Alice"` is `False`.

Perhaps you feel like this:

[![I now have additional questions](https://i.imgur.com/jN57tGt.png)](https://imgur.com/a/icKzI)

The only thing you really need to know is this: Until you know what you're doing, always
make sure you put booleans on both sides of `or`, because it's a boolean operator.
`name == "Alice" or "Bob"` breaks that rule.

If you're curious, the answers are below, but you can skip them if you want and move onto the exercise below.

----

> Why does `(name == "Alice") or ("Bob")` equal `"Bob"`? Why does it equal anything? `"Bob"` isn't even a boolean!

The definition "`A or B` is `True` if either `A` or `B` is `True`" was a simplification. It's the easiest
way to think about `or` most of the time, especially for writing `if` statements.
The real definition is that if `A` is true then `A or B` is just `A` (in fact `B` is not even evaluated),
otherwise it's `B`.
You can see for yourself that if `A` and `B` are booleans then the two definitions are equivalent.
In this example `A` is `name == "Alice"` which is `False`, so `A or B` is `B` which is `"Bob"`.

> Is there a better way to write the condition without repeating `name ==` each time?

Yes! In [Functions and Methods for Lists](/course/?page=FunctionsAndMethodsForLists) we mentioned the `in`
operator, which you can use with a list like this:

    return name in ["Alice", "Bob", "Charlie"]

But you can't always get rid of `or` like that.

----

Exercise: Write a function named `is_valid_percentage`, accepting one numerical argument `x`.
It should return `True` if `x` is between 0 and 100 (inclusive), and return `False` otherwise.
Your function should use `or`, and pass these tests:

    assert_equal(is_valid_percentage(-1), False)
    assert_equal(is_valid_percentage(0), True)
    assert_equal(is_valid_percentage(50), True)
    assert_equal(is_valid_percentage(100), True)
    assert_equal(is_valid_percentage(101), False)

        """
        hints = """
Remember, you can use comparison operators `<, >, <=, >=, ==` to produce booleans.
You need to check how `x` compares to 0 and how it compares to 100.
You need to combine the two comparisons into one boolean using `or`.
Above we used a trick so that the whole function body was just `return <comparison> or <comparison>`. But that won't work here!
You need to use an `if` statement.
You need to have a `return False` and a `return True`.
If you have something like `x >= 0 or x <= 100`, you're on the wrong track. That's going to be true for *any* value of `x`. After all, 101 is greater than 0!
        """

        # TODO disallow and, in, chaining, and multiple ifs
        # TODO catch wrong comparisons

        def solution(self):
            def is_valid_percentage(x: int):
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
Good job!
"""


class IntroducingAnd(Page):
    title = "Introducing `and`"

    class TrueAndTrue(VerbatimStep):
        """
Another boolean operator in Python is `and`.
The expression `A and B` is `True` only if BOTH `A` and `B` are `True`. Otherwise it's `False`.
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

    # noinspection PyChainedComparisons
    class AndExercise(ExerciseStep):
        """
Let's practice now. Previously we wrote a function `is_valid_percentage` using `or`. Here's an example
solution:

    def is_valid_percentage(x):
        if x < 0 or x > 100:
            return False
        else:
            return True

    assert_equal(is_valid_percentage(-1), False)
    assert_equal(is_valid_percentage(0), True)
    assert_equal(is_valid_percentage(50), True)
    assert_equal(is_valid_percentage(100), True)
    assert_equal(is_valid_percentage(101), False)

Rewrite this function using `and` instead.
        """

        hints = """
If you have something like `x < 0 and x > 100`, you're on the wrong track. That's going to be `False` for *any* value of `x`!
The solution with `and` is different in several ways from the solution with `or`.
Our solution with `or` first determines if `x` is an invalid percentage, else concludes validity. Using `and` will do this in reverse.
You will have to reverse the `return` statements accordingly.
You will have to change the comparison operators too.
        """

        # TODO disallow or, in, multiple ifs

        def solution(self):
            def is_valid_percentage(x: int):
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

    class TicTacToeWinningRow(ExerciseStep):
        """
Awesome! Here's one possible solution:

    def is_valid_percentage(x):
        if 0 <= x and x <= 100:
            return True
        else:
            return False

As before, we can simplify this solution to:

    def is_valid_percentage(x):
        return 0 <= x and x <= 100

There's another trick to improve this further called comparison chaining. Any condition like this:

    a < b and b < c

can be shortened by removing the extra `and b` into:

    a < b < c

This works for any comparison operators, including `==`, and the two operators can even be different.
So the solution can be simplified to:

    def is_valid_percentage(x):
        return 0 <= x <= 100

Next exercise: given a list of three elements, check if all three elements are equal.

    def all_equal(row):
        ...

    assert_equal(all_equal(["X", "X", "X"]), True)
    assert_equal(all_equal(["O", "O", "O"]), True)
    assert_equal(all_equal(["X", "O", "X"]), False)
        """

        hints = """
The list will always have 3 elements.
That means you don't need to use a loop.
Remember that you can get the first element using `row[0]`.
The first element, second element, and third element all need to be equal.
That means the first element should be equal to the second element and also the third element.
                """

        def solution(self):
            def all_equal(row: List[str]):
                return row[0] == row[1] and row[0] == row[2]

            return all_equal

        tests = [
            (["O", "O", "O"], True),
            (["X", "X", "X"], True),
            (["O", "X", "O"], False),
            (["O", "O", "X"], False),
            (["X", "O", "O"], False)
        ]

        @classmethod
        def generate_inputs(cls):
            if random.random() < 0.5:
                row = [generate_string()] * 3
            else:
                row = [generate_string() for _ in range(3)]
            return {"row": row}

    final_text = """
Good job. There are many possible correct solutions here:

    def all_equal(row):
        return row[0] == row[1] and row[0] == row[2]

or using comparison chaining again:

        return row[0] == row[1] == row[2]

or check that it's equal to a list containing the first element three times:

        return row == [row[0], row[0], row[0]]
"""


class MultiLineExpressions(Page):
    title = "Multi-line statements"

    class invalid_multiline(VerbatimStep):
        """
Our code lines are starting to get quite long.
Thankfully Python offers a few ways to spread out one statement across many lines,
but it's not automatic. You have to make sure Python understands that's what you're doing.
For example, this code is invalid syntax and will give you an error:

__program_indented__
        """
        program = """\
is_friend = name == "Alice" or
            name == "Bob"
"""

        def check(self):
            return "SyntaxError: invalid syntax" in self.result

    class valid_multiline(VerbatimStep):
        """
Python tries to intepret this as two separate lines of code and gets confused. You need to tell it that
the first line is continuing onto the second line.

One way to do this is by adding `\\` at the end of the line to 'escape' the line break.

Another way is to ensure that the line break is contained within some kind of brackets. Then the line
continuation is implied because Python will wait till all brackets have been closed before
considering a line to be complete. If you already have brackets because for example you're calling a function
or making a list, you may not need to do anything! Otherwise you can add brackets to any expression
to imply the line continuation.

Here are some examples. Pay close attention to the details.

__program_indented__
        """

        def program(self):
            name = "Bob"

            is_friend = name == "Alice" or \
                        name == "Bob"
            print(is_friend)

            is_friend = (name == "Alice" or
                         name == "Bob")
            print(is_friend)

            is_friend = [name == "Alice",
                         name == "Bob"]
            print(is_friend)

            print(name == "Alice" or
                  name == "Bob")

    final_text = """
So if you get a mysterious `SyntaxError`, make sure that you haven't improperly broken up any lines!
    """


class CombiningAndAndOr(Page):
    title = "Combining `and` and `or`"

    class CombiningAndOr(VerbatimStep):
        """
If you use both `and` and `or` in a single expression, it's a lot like combining `*` and `+`.
The operators are evaluated in a specific order.

For example, try the following code in the shell.
What do you expect?

__program_indented__
        """

        expected_code_source = "shell"
        program = "True or False and False"

    class AndHasHigherPriority(ExerciseStep):
        """
If you read it casually from left to right, you may think that:

    True or False and False

is equivalent to

    (True or False) and False

but it's actually equivalent to

    True or (False and False)

This is because `and` has a higher priority than `or`.
This is important because the first interpretation reduces to `True and False` which is `False`, while the second
interpretation reduces to `True or False` which is `True`!
You can try both options with parentheses in the shell to confirm.

**The lesson here is to be extra careful when combining operators.** Either add parentheses to be safe or
break up your expression into smaller parts and assign each part to a variable.
This will make your code clear, readable, and unambiguous, and will save you from painful mistakes.

Time for an exercise. Suppose you're writing a program to play tic-tac-toe,
also known as noughts and crosses or Xs and Os. If you've never heard of tic-tac-toe, you can read the rules
and play a few games [here](https://gametable.org/games/tic-tac-toe/).

We need to check if someone has won a game. Our function `all_equal` is already helpful for checking rows.

Write a function to check if someone has won a game by placing 3 of the same pieces on one of the diagonal lines.
The board is given as 3 lists of 3 strings each, and the function should return a boolean.

    def diagonal_winner(row1, row2, row3):
        ...

    assert_equal(
        diagonal_winner(
            ['X', 'O', 'X'],
            ['X', 'X', 'O'],
            ['O', 'O', 'X']
        ),
        True
    )

    assert_equal(
        diagonal_winner(
            ['X', 'X', 'O'],
            ['X', 'O', 'O'],
            ['O', 'X', 'X']
        ),
        True
    )

    assert_equal(
        diagonal_winner(
            ['O', 'X', 'O'],
            ['X', 'X', 'X'],
            ['O', 'O', 'X']
        ),
        False
    )
        """
        hints = """
How many diagonals are there on the board?
Which entries of `row1, row2, row3` make up each diagonal?
Every list always has 3 entries, so no need for a loop.
There are two problems to solve here: checking for a win in a specific diagonal, and combining the checks for each diagonal.
One problem can be solved using `and`, the other using `or`.
There's a lot of similarity with the `all_equal` function. You can even call that function to help! But then you have to include its definition.
Similar to `all_equal`, check that the 3 entries on a diagonal are equal to each other, e.g. by using `and`.
Check the two diagonals together, using `or`.
        """

        # TODO disallow multiple ifs

        def solution(self):
            def diagonal_winner(row1: List[str], row2: List[str], row3: List[str]):
                middle = row2[1]
                return (
                        (middle == row1[0] and middle == row3[2]) or
                        (middle == row1[2] and middle == row3[0])
                )

            return diagonal_winner

        @classmethod
        def generate_inputs(cls):
            return {
                "row1": [random.choice(["X", "O"]) for _ in range(3)],
                "row2": [random.choice(["X", "O"]) for _ in range(3)],
                "row3": [random.choice(["X", "O"]) for _ in range(3)]
            }

        tests = [
            ((["X", "O", "X"],
              ["X", "X", "O"],
              ["O", "O", "X"]), True),
            ((["X", "O", "O"],
              ["X", "O", "X"],
              ["O", "X", "X"]), True),
            ((["X", "O", "X"],
              ["X", "O", "X"],
              ["O", "O", "X"]), False),
        ]

    final_text = """
Well done! This was a hard one. Here are some possible solutions:

    def diagonal_winner(row1, row2, row3):
        middle = row2[1]
        return (
            (middle == row1[0] and middle == row3[2]) or
            (middle == row1[2] and middle == row3[0])
        )

or:

        diagonal1 = all_equal([row1[0], row2[1], row3[2]])
        diagonal2 = all_equal([row3[0], row2[1], row1[2]])
        return diagonal1 or diagonal2
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

    class NotExercise(ExerciseStep):
        """
We see that `not (True or True)` evaluates to `not (True)` which is `False`.
Because of the parentheses, `or` gets evaluated first.

Exercise: Suppose you're writing a program which processes images. Only certain types of file can be processed.
If the user gives you a file that can't be processed, you want to show an error:

    if invalid_image(filename):
        print("I can't process " + filename)

Suppose that .png and .jpg files cannot be processed, but other file types can.
Here's an example function to do that:

    def invalid_image(filename):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            return False
        else:
            return True

    assert_equal(invalid_image("dog.png"), False)
    assert_equal(invalid_image("cat.jpg"), False)
    assert_equal(invalid_image("invoice.pdf"), True)

This is longer than it needs to be. Rewrite `invalid_image` so that the body is a single line `return <expression>`,
i.e. no `if` statement. It should pass the same tests.
        """

        def solution(self):
            def invalid_image(filename: str):
                return not (filename.endswith(".png") or filename.endswith(".jpg"))
            return invalid_image

        tests = {
            "dog.png": False,
            "invoice.pdf": True,
            "cat.jpg": False,
        }

    final_text = """
Well done! Here are two valid solutions:

    def invalid_image(filename):
        return not (filename.endswith(".png") or filename.endswith(".jpg"))

    def invalid_image(filename):
        return not filename.endswith(".png") and not filename.endswith(".jpg")

(if you're curious, these are equivalent because of something called De Morgan's law)

Also notice that this is another general pattern that can be simplified: if your code has the form:

    if x:
        return False
    else:
        return True

where `x` itself is a boolean, then it can be simplified to:

    return not x

    """
