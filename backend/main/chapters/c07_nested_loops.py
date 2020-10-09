# flake8: NOQA E501
from typing import List

from main.exercises import generate_string
from main.text import ExerciseStep, MessageStep, Page, VerbatimStep


class IntroducingNestedLoops(Page):
    class first_nested_loop(VerbatimStep):
        """
You've seen that the indented body of an `if` or a loop can contain any kind of statement, including more `if` statements and loops. In particular a loop can contain another loop. Here's an example:

__program_indented__
        """

        # TODO after adding quotes chapter:
        #   collapse first three steps into one, add predicted output

        def program(self):
            for letter in "ABC":
                print(letter)
                for number in range(4):
                    print(number)

    class first_nested_loop_with_line(VerbatimStep):
        """
This is called a *nested loop*. Nothing about it is really new, it's just worth understanding properly because it can be very useful for writing interesting programs.

Let's add a line to separate sections of the output:

__program_indented__
        """

        def program(self):
            for letter in "ABC":
                print(letter)
                for number in range(4):
                    print(number)
                print('---')

    class first_nested_loop_with_two_arg_print(VerbatimStep):
        """
Make sure you fully grasp what's going on. `print(letter)` and `print('---')` each run 3 times, because their indentation puts them in the *outer loop*. `print(number)` is called 3 × 4 = 12 times, because it's in the *inner loop* `for number in range(4):` which has 4 iterations but is itself in the outer loop so it runs 3 times.

One more tweak:

__program_indented__
        """

        def program(self):
            for letter in "ABC":
                print(letter)
                for number in range(4):
                    print(letter, number)
                print('---')

    class times_table_exercise(ExerciseStep):
        """
`print(letter, number)` gives `print` two arguments. `print` can take any number of arguments, and it will output them all on the same line, with spaces in between. If you try using `print(letter + ' ' + number)` instead you'll get an error, because you can't add strings and numbers. We'll come back to that later.

Let's put this to use! Suppose you're a teacher and you need to print out all the multiplication tables from 1 to 12 for your students. You don't want to write them manually, but you can write a program to do it for you! Your program output should look like this including the lines of dashes:

    1 x 1 = 1
    1 x 2 = 2
    1 x 3 = 3
    1 x 4 = 4
    1 x 5 = 5
    1 x 6 = 6
    1 x 7 = 7
    1 x 8 = 8
    1 x 9 = 9
    1 x 10 = 10
    1 x 11 = 11
    1 x 12 = 12
    ----------
    2 x 1 = 2
    2 x 2 = 4
    2 x 3 = 6
    2 x 4 = 8
    2 x 5 = 10
    2 x 6 = 12
    2 x 7 = 14
    2 x 8 = 16
    2 x 9 = 18
    2 x 10 = 20
    2 x 11 = 22
    2 x 12 = 24
    ----------
    3 x 1 = 3
    3 x 2 = 6
    3 x 3 = 9
    (you get the idea...)
    11 x 10 = 110
    11 x 11 = 121
    11 x 12 = 132
    ----------
    12 x 1 = 12
    12 x 2 = 24
    12 x 3 = 36
    12 x 4 = 48
    12 x 5 = 60
    12 x 6 = 72
    12 x 7 = 84
    12 x 8 = 96
    12 x 9 = 108
    12 x 10 = 120
    12 x 11 = 132
    12 x 12 = 144
    ----------
        """

        hints = """
You need to use a for loop inside a for loop.
You need the numbers from 1 to 12.
Whenever you need a sequence of consecutive numbers, use `range`.
You want something like `for x in range(n):`.
This will start with `x = 0`, but there's an easy workaround for that.
You can just add 1 to `x`.
Use `*` to multiply numbers.
Use `print()` with several arguments separated by commas to print several things on one line.
Remember to print a line with the correct number of dashes after each section.
Make sure each line is in the correct loop and has the right amount of indentation.
        """

        parsons_solution = True

        def solution(self):
            for left in range(12):
                left += 1
                for right in range(12):
                    right += 1
                    print(left, 'x', right, '=', left * right)
                print('----------')

        # TODO handle left += 1 in inner loop

        class too_long(MessageStep):
            """
Your solution is too long. You only need a few lines of code for this problem.
Use a nested loop so that you don't need to repeat yourself.
The computer will do the repetition for you!
            """
            after_success = True

            def program(self):
                for left in range(12):
                    left += 1
                    print(left, 'x 1 =', left * 1)
                    print(left, 'x 2 =', left * 2)
                    print(left, 'x 3 =', left * 3)
                    print(left, 'x 4 =', left * 4)
                    print(left, 'x 5 =', left * 5)
                    print(left, 'x 6 =', left * 6)
                    print(left, 'x 7 =', left * 7)
                    print(left, 'x 8 =', left * 8)
                    print(left, 'x 9 =', left * 9)
                    print(left, 'x 10 =', left * 10)
                    print(left, 'x 11 =', left * 11)
                    print(left, 'x 12 =', left * 12)
                    print('----------')

            def check(self):
                lines = [line.strip() for line in self.input.splitlines()]
                lines = [line for line in lines if line and not line.startswith("#")]
                return len(lines) > 10

        class added_str_and_int(MessageStep):
            """
You can't add together strings and numbers. Use `print()` with several arguments
as shown above, e.g. `print(x, y, z)`. It'll even add spaces for you!
            """

            def program(self):
                # noinspection PyTypeChecker
                print(1 + "x")

            def check(self):
                return "TypeError: unsupported operand type(s) for +: " in self.result

        class used_x_to_multiply(MessageStep):
            """To multiply numbers, use `*`"""

            program = "2 x 3"

            def check(self):
                """
                Check for a traceback like:
                    2 x 3
                      ^
                SyntaxError: invalid syntax

                It might be better to try replacing x with * and see if
                it becomes valid syntax
                """
                lines = self.result.strip().splitlines()
                return (
                        len(lines) >= 3 and
                        lines[-1] == "SyntaxError: invalid syntax" and
                        lines[-2].strip() == "^" and
                        lines[-3][lines[-2].index("^")] == "x"
                )

        tests = {
            (): """\
1 x 1 = 1
1 x 2 = 2
1 x 3 = 3
1 x 4 = 4
1 x 5 = 5
1 x 6 = 6
1 x 7 = 7
1 x 8 = 8
1 x 9 = 9
1 x 10 = 10
1 x 11 = 11
1 x 12 = 12
----------
2 x 1 = 2
2 x 2 = 4
2 x 3 = 6
2 x 4 = 8
2 x 5 = 10
2 x 6 = 12
2 x 7 = 14
2 x 8 = 16
2 x 9 = 18
2 x 10 = 20
2 x 11 = 22
2 x 12 = 24
----------
3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
3 x 6 = 18
3 x 7 = 21
3 x 8 = 24
3 x 9 = 27
3 x 10 = 30
3 x 11 = 33
3 x 12 = 36
----------
4 x 1 = 4
4 x 2 = 8
4 x 3 = 12
4 x 4 = 16
4 x 5 = 20
4 x 6 = 24
4 x 7 = 28
4 x 8 = 32
4 x 9 = 36
4 x 10 = 40
4 x 11 = 44
4 x 12 = 48
----------
5 x 1 = 5
5 x 2 = 10
5 x 3 = 15
5 x 4 = 20
5 x 5 = 25
5 x 6 = 30
5 x 7 = 35
5 x 8 = 40
5 x 9 = 45
5 x 10 = 50
5 x 11 = 55
5 x 12 = 60
----------
6 x 1 = 6
6 x 2 = 12
6 x 3 = 18
6 x 4 = 24
6 x 5 = 30
6 x 6 = 36
6 x 7 = 42
6 x 8 = 48
6 x 9 = 54
6 x 10 = 60
6 x 11 = 66
6 x 12 = 72
----------
7 x 1 = 7
7 x 2 = 14
7 x 3 = 21
7 x 4 = 28
7 x 5 = 35
7 x 6 = 42
7 x 7 = 49
7 x 8 = 56
7 x 9 = 63
7 x 10 = 70
7 x 11 = 77
7 x 12 = 84
----------
8 x 1 = 8
8 x 2 = 16
8 x 3 = 24
8 x 4 = 32
8 x 5 = 40
8 x 6 = 48
8 x 7 = 56
8 x 8 = 64
8 x 9 = 72
8 x 10 = 80
8 x 11 = 88
8 x 12 = 96
----------
9 x 1 = 9
9 x 2 = 18
9 x 3 = 27
9 x 4 = 36
9 x 5 = 45
9 x 6 = 54
9 x 7 = 63
9 x 8 = 72
9 x 9 = 81
9 x 10 = 90
9 x 11 = 99
9 x 12 = 108
----------
10 x 1 = 10
10 x 2 = 20
10 x 3 = 30
10 x 4 = 40
10 x 5 = 50
10 x 6 = 60
10 x 7 = 70
10 x 8 = 80
10 x 9 = 90
10 x 10 = 100
10 x 11 = 110
10 x 12 = 120
----------
11 x 1 = 11
11 x 2 = 22
11 x 3 = 33
11 x 4 = 44
11 x 5 = 55
11 x 6 = 66
11 x 7 = 77
11 x 8 = 88
11 x 9 = 99
11 x 10 = 110
11 x 11 = 121
11 x 12 = 132
----------
12 x 1 = 12
12 x 2 = 24
12 x 3 = 36
12 x 4 = 48
12 x 5 = 60
12 x 6 = 72
12 x 7 = 84
12 x 8 = 96
12 x 9 = 108
12 x 10 = 120
12 x 11 = 132
12 x 12 = 144
----------
"""
        }

    class player_vs_player_exercise(ExerciseStep):
        """
Perfect!

Next exercise: you're organising a tournament for a game, such as chess or tennis. You have a list of player names:

    players = ["Alice", "Bob", "Charlie"]

Every player is going to play against every other player twice: once where they get the advantage (e.g. by moving or serving first) and once not. Print out all the match combinations like this:

    Alice vs Bob
    Alice vs Charlie
    Bob vs Alice
    Bob vs Charlie
    Charlie vs Alice
    Charlie vs Bob

Note that "Alice vs Bob" and "Bob vs Alice" are both in the list, but there's no "Alice vs Alice" - we don't want anyone playing with themselves.
        """

        def solution(self, players: List[str]):
            for player1 in players:
                for player2 in players:
                    if player1 != player2:
                        print(player1, 'vs', player2)

        hints = """
Think about how you would do this manually and systematically, with a pencil and paper.
You need to use a for loop inside a for loop.
You need an `if` statement to check that the two players aren't the same person.
        """

        tests = [
            (["Alice", "Bob", "Charlie"], """\
Alice vs Bob
Alice vs Charlie
Bob vs Alice
Bob vs Charlie
Charlie vs Alice
Charlie vs Bob
            """
             )]

    class crack_password_exercise(ExerciseStep):
        """
For your next exercise, you need to crack a password. You know that it's exactly four letters long and that only a few letters are possible, which you've written down:

    letters = "ABCD"

You need to print out all possible passwords:

    AAAA
    AAAB
    AAAC
    AAAD
    AABA
    AABB
    ...skipping a few...
    DDDA
    DDDB
    DDDC
    DDDD
            """

        hints = """
Think about how you would do this manually and systematically, with a pencil and paper.
The fact that the password must be four letters long is very important. This would be a lot harder to solve if the password could be any given length.
But the string `letters` might have any number of characters.
If there are `n` different letters, then the number of possible passwords is `n^4 == n*n*n*n` because there are `n` possible letters for each position and they're all independent.
Suppose again that `letters = "ABCD"`. Imagine you have all possible three-letter passwords. Now for each one, add an A at the end, or add a B, or a C, or a D. That's how you would get all possible four-letter passwords.
Remember, a for loop can contain any statement, including another for loop.
That applies to all for loops.
One for loop inside another for loop is no longer enough.
You have to go deeper. 
        """

        # TODO check for spaces between letters in output

        def solution(self, letters: str):
            for c1 in letters:
                for c2 in letters:
                    for c3 in letters:
                        for c4 in letters:
                            print(c1 + c2 + c3 + c4)

        def generate_inputs(cls):
            return {"letters": generate_string(2)}

        tests = {
            "AB": """\
AAAA
AAAB
AABA
AABB
ABAA
ABAB
ABBA
ABBB
BAAA
BAAB
BABA
BABB
BBAA
BBAB
BBBA
BBBB
""",
            "ABC": """\
AAAA
AAAB
AAAC
AABA
AABB
AABC
AACA
AACB
AACC
ABAA
ABAB
ABAC
ABBA
ABBB
ABBC
ABCA
ABCB
ABCC
ACAA
ACAB
ACAC
ACBA
ACBB
ACBC
ACCA
ACCB
ACCC
BAAA
BAAB
BAAC
BABA
BABB
BABC
BACA
BACB
BACC
BBAA
BBAB
BBAC
BBBA
BBBB
BBBC
BBCA
BBCB
BBCC
BCAA
BCAB
BCAC
BCBA
BCBB
BCBC
BCCA
BCCB
BCCC
CAAA
CAAB
CAAC
CABA
CABB
CABC
CACA
CACB
CACC
CBAA
CBAB
CBAC
CBBA
CBBB
CBBC
CBCA
CBCB
CBCC
CCAA
CCAB
CCAC
CCBA
CCBB
CCBC
CCCA
CCCB
CCCC
"""
        }

    class upside_down_triangle_exercise(ExerciseStep):
        """
Wow, you're basically a hacker now!

One more exercise. Given a size:

    size = 5

Print out an 'upside down' triangle made of the letter `O` whose sides are as long as the given size, e.g:

    OOOOO
    OOOO
    OOO
    OO
    O
        """

        hints = """
How would you describe instructions to type in this triangle manually?
Print a line of `size` Os, then `size - 1` Os, etc. down to 1 O. For example print 5 Os, then 4 Os, then 3, 2, and 1.
Break this down into subproblems.
How do you print one line of Os of a given length, and how do you go through all the lengths?
Building up a line of characters should be very familiar from previous exercises, the only difference is that you have to make it a given length instead of just the same length as another string.
An easy way to do something `n` times is to loop over `range(n)`. 
You need to use a for loop inside a for loop.
You need numbers that count down, like 5, 4, 3, 2, 1. There is a way to do this with `range`, and you can easily look it up, but it's also easy to use a normal range and do some very simple maths to convert numbers counting up into numbers counting down.
What formula converts 0 into 5, 1 into 4, 2, into 3, etc?
"""

        parsons_solution = True

        def solution(self, size: int):
            for i in range(size):
                length = size - i
                line = ''
                for _ in range(length):
                    line += 'O'
                print(line)

        # TODO disallow *

        tests = {
            3: """\
OOO
OO
O
""",
            5: """\
OOOOO
OOOO
OOO
OO
O
    """
        }

    class player_vs_player_bonus(ExerciseStep):
        """
Wow, you're an artist too!

If you'd like, you can just continue to the [next page](/course/?page=IntroducingBirdseye) now. Or you can do a bonus challenge!

Like the earlier exercise, you're organising a tournament for a game. You have a list of player names:

    players = ['Charlie', 'Alice', 'Dylan', 'Bob']

This time, each pair of players should only appear once. Specifically, print only those pairs that are in
the same left-to-right order as they are in `players`, starting with pairs containing the leftmost person
in `players` and moving right. For example, for the above, your program should print

    Charlie vs Alice
    Charlie vs Dylan
    Charlie vs Bob
    Alice vs Dylan
    Alice vs Bob
    Dylan vs Bob

        """

        def solution(self, players: List[str]):
            for i in range(len(players)):
                for j in range(len(players)):
                    if i < j:
                        print(players[i], 'vs', players[j])

        hints = """
You'll need a for loop inside a for loop like before.
This time something like `for player1 in players:` won't be enough.
Your program needs to use the *positions* of the players in the list.
That means you need to loop over the positions and use indexing (subscripting) to access the list entries.
To loop over the positions, use `range`...
...and `len`.
Look at the desired output: `Charlie vs Alice`: `Charlie` comes before `Alice` in the `players` list.
We don't want to print `Alice vs Charlie` because `Alice` comes AFTER `Charlie` in `players`.
The only pairs we want to print are those where the left player comes before the right player in the list.
How can we express this relation in terms of the list indices of the two for-loops?
You need to use a comparison operator.
Once you figure out the relation, you can express it with an `if` statement.
"""

        tests = [
            (["Alice", "Bob", "Charlie"], """\
Alice vs Bob
Alice vs Charlie
Bob vs Charlie
            """
            ),
            (["Frank", "Dave", "Emily"], """\
Frank vs Dave
Frank vs Emily
Dave vs Emily
            """
            ),
            (["Charlie", "Alice", "Dylan", "Bob"], """\
Charlie vs Alice
Charlie vs Dylan
Charlie vs Bob
Alice vs Dylan
Alice vs Bob
Dylan vs Bob
            """
            )]

    final_text = """
Excellent! The solution goes like this:

    players = ['Charlie', 'Alice', 'Dylan', 'Bob']
    for i in range(len(players)):
        for j in range(len(players)):
            if i < j:
                print(players[i], 'vs', players[j])
"""


class IntroducingBirdseye(Page):
    title = "Understanding Programs with Bird's Eye"

    class first_birdseye_example(VerbatimStep):
        """
You've seen Snoop and Python Tutor. futurecoder comes with one last tool to analyse programs as they run, called *Bird's Eye*.

Here's an example program to run. Copy it into the editor and click the Bird's Eye button. This will open a new browser tab with the visualisation.

    __copyable__
    __program_indented__
        """

        expected_code_source = "birdseye"

        def program(self):
            a = 2
            b = 3
            c = 4
            d = 5
            print(a * b + c * d)

    class birdseye_loop_example(VerbatimStep):
        """
While the other tools show how code runs line by line and the values of variables, Bird's Eye shows you the value of every expression in a program. This lets you see how a complex expression is broken down into smaller sub-expressions
and what the value of each one is.

Hover your mouse over the various boxed expressions in the last line of the program.
As each box is highlighted, its value is shown at the bottom of the screen. Clicking on the box will stick it on a panel so you can see several expression values at once and move your mouse around freely.

In this case Bird's Eye shows that the expression:

    a * b + c * d

is broken into

    (a * b) + (c * d)

rather than

    ((a * b) + c) * d

In other words, Python follows the usual order of operations in maths, rather than just evaluating from left to right.

Note that there are some expressions that Bird's Eye doesn't put in a box. In this case `2`, `3`, `4`, `5`, and `print` are all expressions as well, but their values are obvious and boxing them would just be clutter.

Here's a more complicated example to try out:

    __copyable__
    __program_indented__
        """

        expected_code_source = "birdseye"

        def program(self):
            word = 'Amazing'
            vowels = []
            consonants = []
            for letter in word:
                if letter.lower() in 'aeiou':
                    vowels.append(letter)
                else:
                    consonants.append(letter)
            print(vowels)
            print(consonants)

    final_text = """
Note that:

1. There's a pair of arrows next to the for loop. Click on them to navigate through the loop in time and see what happened in different iterations.
2. Code that doesn't run in an iteration because of the `if` is greyed out. The expressions within have no values because they weren't evaluated.
3. The values recorded for the expressions `vowels` and `consonants` depend on which box you look at. In the lines after the loop, they contain all the letters, but inside the loop they only contain some, and exactly how many depends on which iteration you're on.
4. In `vowels.append(letter)`, you see what the values of those variables were *at that moment*. That means that `letter` is about to be appended to `vowels` but this hasn't happened yet, so `vowels` doesn't contain `letter`.
        """
