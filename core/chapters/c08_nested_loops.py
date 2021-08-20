# flake8: NOQA E501
import ast
from string import ascii_lowercase
from random import randint, choice
from typing import List

from core.exercises import generate_string
from core.text import (
    ExerciseStep,
    MessageStep,
    Page,
    VerbatimStep,
    Disallowed,
    search_ast,
    Step,
)


class IntroducingNestedLoops(Page):
    class first_nested_loop(VerbatimStep):
        """
You've seen that the indented body of an `if` or a loop can contain any kind of statement, including more `if` statements and loops. In particular a loop can contain another loop. Here's an example:

__program_indented__

This is called a *nested loop*. Nothing about it is really new, it's just worth understanding properly because it can be very useful for writing interesting programs.
        """

        def program(self):
            for letter in "ABC":
                print(letter)
                for number in range(4):
                    print(f'{letter} {number}')
                print('---')

        predicted_output_choices = [
            """\
A 0
A 1
A 2
A 3
---
B 0
B 1
B 2
B 3
---
C 0
C 1
C 2
C 3
---
""", """\
A
A 0
A 1
A 2
A 3
---
B
B 0
B 1
B 2
B 3
---
C
C 0
C 1
C 2
C 3
---
""", """\
A 1
A 2
A 3
A 4
---
B 1
B 2
B 3
B 4
---
C 1
C 2
C 3
C 4
---
""", """\
A
B
C
---
A 0
B 0
C 0
---
A 1
B 1
C 1
---
A 2
B 2
C 2
---
A 3
B 3
C 3
"""
        ]

    class times_table_exercise(ExerciseStep):
        """
Make sure you fully grasp what's going on. `print(letter)` and `print('---')` each run 3 times, because their indentation puts them in the *outer loop*. `print(f'{letter} {number}')` is called 3 × 4 = 12 times, because it's in the *inner loop* `for number in range(4):` which has 4 iterations but is itself in the outer loop so it runs 3 times.

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
Use an f-string with several variables.
Remember to print a line with the correct number of dashes after each section.
Make sure each line is in the correct loop and has the right amount of indentation.
        """

        parsons_solution = True

        def check(self):
            try:
                return super().check()
            except SyntaxError:
                lines = self.result.splitlines()
                if (
                    len(lines) >= 3
                    and lines[2].strip() == "SyntaxError: invalid syntax"
                    and lines[1].strip() == "^"
                    and lines[0][lines[1].index("^")] == "x"
                ):
                    return dict(message="To multiply numbers, use `*`")

        def solution(self):
            for left in range(12):
                left += 1
                for right in range(12):
                    right += 1
                    print(f'{left} x {right} = {left * right}')
                print('----------')

        class adding_one_in_wrong_loop(ExerciseStep, MessageStep):
            """
You added 1 to your outer loop variable at the wrong place!
Where should you do that instead to fix it?
            """

            def solution(self):
                for left in range(12):
                    for right in range(12):
                        left += 1
                        right += 1
                        print(f'{left} x {right} = {left * right}')
                    print('----------')

            tests = {
                (): """\
1 x 1 = 1
2 x 2 = 4
3 x 3 = 9
4 x 4 = 16
5 x 5 = 25
6 x 6 = 36
7 x 7 = 49
8 x 8 = 64
9 x 9 = 81
10 x 10 = 100
11 x 11 = 121
12 x 12 = 144
----------
2 x 1 = 2
3 x 2 = 6
4 x 3 = 12
5 x 4 = 20
6 x 5 = 30
7 x 6 = 42
8 x 7 = 56
9 x 8 = 72
10 x 9 = 90
11 x 10 = 110
12 x 11 = 132
13 x 12 = 156
----------
3 x 1 = 3
4 x 2 = 8
5 x 3 = 15
6 x 4 = 24
7 x 5 = 35
8 x 6 = 48
9 x 7 = 63
10 x 8 = 80
11 x 9 = 99
12 x 10 = 120
13 x 11 = 143
14 x 12 = 168
----------
4 x 1 = 4
5 x 2 = 10
6 x 3 = 18
7 x 4 = 28
8 x 5 = 40
9 x 6 = 54
10 x 7 = 70
11 x 8 = 88
12 x 9 = 108
13 x 10 = 130
14 x 11 = 154
15 x 12 = 180
----------
5 x 1 = 5
6 x 2 = 12
7 x 3 = 21
8 x 4 = 32
9 x 5 = 45
10 x 6 = 60
11 x 7 = 77
12 x 8 = 96
13 x 9 = 117
14 x 10 = 140
15 x 11 = 165
16 x 12 = 192
----------
6 x 1 = 6
7 x 2 = 14
8 x 3 = 24
9 x 4 = 36
10 x 5 = 50
11 x 6 = 66
12 x 7 = 84
13 x 8 = 104
14 x 9 = 126
15 x 10 = 150
16 x 11 = 176
17 x 12 = 204
----------
7 x 1 = 7
8 x 2 = 16
9 x 3 = 27
10 x 4 = 40
11 x 5 = 55
12 x 6 = 72
13 x 7 = 91
14 x 8 = 112
15 x 9 = 135
16 x 10 = 160
17 x 11 = 187
18 x 12 = 216
----------
8 x 1 = 8
9 x 2 = 18
10 x 3 = 30
11 x 4 = 44
12 x 5 = 60
13 x 6 = 78
14 x 7 = 98
15 x 8 = 120
16 x 9 = 144
17 x 10 = 170
18 x 11 = 198
19 x 12 = 228
----------
9 x 1 = 9
10 x 2 = 20
11 x 3 = 33
12 x 4 = 48
13 x 5 = 65
14 x 6 = 84
15 x 7 = 105
16 x 8 = 128
17 x 9 = 153
18 x 10 = 180
19 x 11 = 209
20 x 12 = 240
----------
10 x 1 = 10
11 x 2 = 22
12 x 3 = 36
13 x 4 = 52
14 x 5 = 70
15 x 6 = 90
16 x 7 = 112
17 x 8 = 136
18 x 9 = 162
19 x 10 = 190
20 x 11 = 220
21 x 12 = 252
----------
11 x 1 = 11
12 x 2 = 24
13 x 3 = 39
14 x 4 = 56
15 x 5 = 75
16 x 6 = 96
17 x 7 = 119
18 x 8 = 144
19 x 9 = 171
20 x 10 = 200
21 x 11 = 231
22 x 12 = 264
----------
12 x 1 = 12
13 x 2 = 26
14 x 3 = 42
15 x 4 = 60
16 x 5 = 80
17 x 6 = 102
18 x 7 = 126
19 x 8 = 152
20 x 9 = 180
21 x 10 = 210
22 x 11 = 242
23 x 12 = 276
----------
"""
            }

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
You can't add together strings and numbers. Use an f-string.
            """

            def program(self):
                # noinspection PyTypeChecker
                print(1 + "x")

            def check(self):
                return "TypeError: unsupported operand type(s) for +: " in self.result

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
                        print(f'{player1} vs {player2}')

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
             ),
            (['Charlie', 'Alice', 'Dylan', 'Bob'], """\
Charlie vs Alice
Charlie vs Dylan
Charlie vs Bob
Alice vs Charlie
Alice vs Dylan
Alice vs Bob
Dylan vs Charlie
Dylan vs Alice
Dylan vs Bob
Bob vs Charlie
Bob vs Alice
Bob vs Dylan
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

        def solution(self, letters: str):
            for c1 in letters:
                for c2 in letters:
                    for c3 in letters:
                        for c4 in letters:
                            print(c1 + c2 + c3 + c4)

        @classmethod
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

        disallowed = Disallowed(ast.Mult, label="`*`")

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

If you'd like, you can just continue to the [next page](#IntroducingBirdseye) now. Or you can do a bonus challenge!

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
                        print(f'{players[i]} vs {players[j]}')

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
                print(f'{players[i]} vs {players[j]}')
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


class IntroducingNestedLists(Page):
    class string_list_exercise(ExerciseStep):
        """
Exercise: given a list of strings, print the first letter of the second string in the list. For example, given:

    __copyable__
    strings = ["abc", "def", "ghi"]

you should print `d`.
        """

        def solution(self, strings: List[str]):
            string = strings[1]
            print(string[0])

        hints = """
How can you access the second string in the list?
Then how do you access a particular letter in a string?
Remember that the indexing of lists and strings are very similar.
"""
        tests = [
            (["abc", "def", "ghi"], 'd'),
            (["Alice", "went", "to", "school"], 'w')
        ]

    class double_subscripting(Step):
        """
You may have solved it like this:

    string = strings[1]
    print(string[0])

There's a shorter way. `strings[1]` is an expression like any other, and subscripting like `[0]`
can be used on any expression, not just variables.
So you can skip the intermediate variable and just do it in one line:

    print(strings[1][0])

Take a good look at this syntax. If it looks new and fancy, it's not.
It's just the usual syntax for subscripting, applied twice.
Try it in birdseye to see how Python breaks it down into smaller pieces.
        """

        expected_code_source = "birdseye"
        program_in_text = False

        def program(self):
            strings = ["abc", "def", "ghi"]
            print(strings[1][0])

        def check(self):
            return search_ast(
                self.tree,
                ast.Subscript(value=ast.Subscript()),
            )

    class double_subscripting_exercise(ExerciseStep):
        """
Using this syntax, modify the program to print the last letter of the second-to-last string in the list `strings`.
You must use a single expression like above, and you are not allowed to use `len`.
Your solution should work for any non-empty list of strings.
For the previous example input it should print `f`.
        """

        def solution(self, strings: List[str]):
            print(strings[-2][-1])

        def check(self):
            # Basically the above solution is the only option
            # The only reason this isn't a VerbatimStep is to allow strings to be a loose parameter
            return super().check() and \
                search_ast(
                    self.tree,
                    ast.parse("print(strings[-2][-1])").body[0],
                )

        hints = """
This is very similar to the previous exercise.
Do you remember how to access the last position of a list (without using `len`)?
Similarly how do you access the second-to-last position in a list?
If you can't remember, you can Google it!
Indexing works similarly on lists and strings.
Do you get an `index out of range` error? Is it for a string, or a list? Why?
Make sure you are not confusing the order of the list index and the string index.
Use birdseye if you're having trouble.
"""
        tests = [
            (["abc", "de", "fghi", "jklmn", "o"], 'n'),
            (["Alice", "went", "to", "school"], 'o')
        ]

    class first_nested_list_example(VerbatimStep):
        """
Well done!

Applying subscripting twice can be even more powerful.
We can use it on not only a list of strings, but on *a list of lists* too.
For example, what does the following program print?

__program_indented__
        """

        def program(self):
            strings = [['hello', 'there'], ['how', 'are', 'you']]
            print(strings[1][0])

        predicted_output_choices = [
            "hello", "there", "how", "are", "you",
            "['hello', 'there']", "['how', 'are', 'you']",
            'h', 't', 'e', 'a',
        ]

    class triple_subscripting(ExerciseStep):
        """
As you can see Python allows us to have *nested lists*: a list where each element is another list (we refer to them as *sublists*).

We can use subscripting even more than twice.
Write a program that takes a nested list `strings` like above,
and prints the **first letter of the third string in the second sublist**.
Use only a single expression like in the previous exercise.
For example, for the list above, it should print `y`.
        """

        def solution(self, strings: List[List[str]]):
            print(strings[1][2][0])

        hints = """
This is very similar to the previous exercises.
How many times do you need to use subscripting?
First you need to access a sublist.
Then a string in that sublist.
Then a letter in that string.
Use birdseye if you're having trouble.
        """

        tests = [
            ([['hello', 'there'], ['how', 'are', 'you']], 'y'),
            ([
                [
                    "The cat stretched.",
                    "Jacob stood on his tiptoes."
                ],
                [
                    "The car turned the corner.",
                    "Kelly twirled in circles,",
                    "she opened the door."
                ],
                [
                    "Aaron made a picture."
                ]
            ], "s")
        ]

    final_text = """
Excellent! You now understand nested subscripting very well.

We can still use all the list methods and functions we learned before.
For example we can add a new word to the last sublist of `strings` with `append`,
to come after `'you'`:

    strings[1].append("today?")
    
After all, the sublist `strings[1]` is still a list like any other!

On the next page we will learn about looping over nested lists.
        """


class LoopingOverNestedLists(Page):
    class nested_list_nested_loop_example(VerbatimStep):
        """
You can use a nested loop to iterate over each element and sub-element of a nested list.
For example, consider this nested list.

    __copyable__
    numbers = [[1, 2, 3], [4, 5], [6], []]

Click the button to copy the list into the editor, then type in the following nested loop.

    for sublist in numbers:
        for num in sublist:
            print(num)
        print('---')

Look carefully at the code. Note that the outer loop creates a variable `sublist`
and the inner loop iterates over the same variable. This is a common pattern.
Now run the code.
        """

        program_in_text = False

        def program(self):
            numbers = [[1, 2, 3], [4, 5], [6], []]
            for sublist in numbers:
                for num in sublist:
                    print(num)
                print('---')

        predicted_output_choices = ["""\
1
---
2
---
3
---
4
---
5
---
6
---
""", """\
1
2
3
---
4
5
---
6
---
---
""", """\
1
2
3
---
4
5
---
6
---
""", """\
1 2 3
---
4 5
---
6
---
---
""", """\
1 2 3
---
4 5
---
6
---
"""]

    class nested_list_loop_python_tutor(nested_list_nested_loop_example):
        text = """
Now run the same program again in Python Tutor.

Examine what `numbers` looks like, and what `numbers[0]` up to `numbers[3]` are.
Look at how `sublist` and `num` variables advance.
        """

        expected_code_source = "pythontutor"
        predicted_output_choices = None

    class string_contains_word_exercise(ExerciseStep):
        """
Now let's solve some problems using this kind of loop.

Suppose we have a nested list of strings like the one below,
and we want to search for a particular `word` deep within the list.

    __copyable__
    strings = [
        [
            "hello there",
            "how are you",
        ],
        [
            "goodbye world",
            "hello world",
        ]
    ]
    word = "hello"

You can imagine that `strings` represents a book, where each sublist is a page and each string within
is a line in that page.
It could also represent a library, where each list is a book, and each string is a page.

Write a program to print every string that contains `word`.
It should work for any `word` and `strings`. For the example above, it should print

    hello there
    hello world

Remember that there is a specific way to check if a string contains another string. If you can't remember how, Google it!
        """

        def solution(self, strings: List[List[str]], word: str):
            for sublist in strings:
                for string in sublist:
                    if word in string:
                        print(string)

        hints = """
How do you check if a string contains a word?
Make sure to check whether **the string** contains the word, not the sublist.
How can you access each string in each sublist of a nested list?
You need to use a nested loop.
The loops should follow the same pattern as the example at the beginning of the page. 
        """

        tests = [
            (
                (
                    [
                        [
                            "hello there",
                            "how are you",
                        ],
                        [
                            "goodbye world",
                            "hello world",
                        ]
                    ], "hello"
                ), """\
hello there
hello world
"""),
            (
                (
                    [
                        [
                            "The cat stretched.",
                            "Jacob stood on his tiptoes."
                        ],
                        [
                            "The car turned the corner.",
                            "Kelly twirled in circles,",
                            "she opened the door."
                        ],
                        [
                            "Aaron made a picture."
                        ]
                    ], "The"
                ), """\
The cat stretched.
The car turned the corner.
""")
        ]

    class sublist_contains_word_exercise(ExerciseStep):
        """
Nice!

Now let's change the exercise slightly. This time the output should tell us which *sublists* contain `word`,
rather than which inner strings. In particular, we want to print a boolean for each sublist:
`True` if the sublist contains the word in any of its strings, `False` if it's not there at all.

Given these example inputs:

    __copyable__
    strings = [
        [
            "hello there",
            "how are you",
        ],
        [
            "goodbye world",
            "hello world",
        ]
    ]
    word = "goodbye"

then your program should print

    False
    True

Note that `word in sublist` won't work. For example, `"hello" in ["hello there", "how are you"]` is `False`
because `"hello"` is not *equal* to either of the two elements of that list, even though it is in one of them.
        """

        parsons_solution = True

        def solution(self, strings: List[List[str]], word: str):
            for sublist in strings:
                present = False
                for string in sublist:
                    if word in string:
                        present = True
                print(present)

        hints = """
For each sublist, define a boolean.
Go through a sublist, update the boolean accordingly.
Only print the boolean once for each sublist.
What should be the initial value for the boolean?
What if one of the sublists is empty? What should you print for that sublist?
If you find the word in a string, the boolean should be set to `True`.
What if a string doesn't contain the word?
Doesn't matter! It doesn't change whether any other string might contain the word.
In other words, don't set the boolean to `False` except at the beginning.
        """

        tests = [
            (
                (
                    [
                        [
                            "hello there",
                            "how are you",
                        ],
                        [
                            "goodbye world",
                            "hello world",
                        ]
                    ], "goodbye"
                ), """\
False
True
"""),
            (
                (
                    [
                        [
                            "hello there",
                            "how are you",
                        ],
                        [
                            "goodbye world",
                            "hello world",
                        ]
                    ], "hello"
                ), """\
True
True
"""),
            (
                (
                    [
                        [
                            "hello there",
                            "how are you",
                        ],
                        [
                            "goodbye world",
                            "hello world",
                        ]
                    ], "Python"
                ), """\
False
False
""")
        ]

    class list_contains_word_exercise(ExerciseStep):
        """
Well done!

Next, print only one boolean to indicate if `word` is present in any string in the entire nested list at all. For example, if

    __copyable__
    strings = [
        [
            "hello there",
            "how are you",
        ],
        [
            "goodbye world",
            "hello world",
        ]
    ]
    word = "Python"

your program should print `False`.
        """

        parsons_solution = True

        def solution(self, strings: List[List[str]], word: str):
            present = False
            for sublist in strings:
                for string in sublist:
                    if word in string:
                        present = True
            print(present)

        hints = """
This is very similar to the previous exercise.
When should you print the boolean?
Remember you want to print it only once.
Instead of defining a boolean for each sublist, define only one boolean for the entire list.
When and how should you modify the boolean?
        """

        tests = [
            (
                (
                    [
                        [
                            "hello there",
                            "how are you",
                        ],
                        [
                            "goodbye world",
                            "hello world",
                        ]
                    ], "are"
                ), "True"),
            (
                (
                    [
                        [
                            "hello there",
                            "how are you",
                        ],
                        [
                            "goodbye world",
                            "hello world",
                        ]
                    ], "Python"
                ), "False")
        ]

    class zip_strings_list_exercise(ExerciseStep):
        """
Excellent!

[Earlier in the course](#GettingElementsAtPosition) there was an exercise
to print two strings vertically side by side, like this:

    H W
    e o
    l r
    l l
    o d

Now we're going to generalize this to a list of strings, rather than just two.

For this exercise you are given a list of strings of **equal length**.
Write a program that prints the first letter of each string on one line,
then the second letter of each string on the next line, and so on. For example, if

    strings = ["abc", "def", "ghi"]

then your program should print

    adg
    beh
    cfi

Your program should work for any such list. In particular, if you use the following list,
you'll discover a hidden message from the Zen of Python!

    __copyable__
    strings = ["  b n", "f ete", "liths", "astat", "t ene", "  r d"]

Note that this time you shouldn't add spaces between letters in the output.
        """

        def solution(self, strings: List[str]):
            for i in range(len(strings[0])):
                line = ""
                for string in strings:
                    line += string[i]
                print(line)

        @classmethod
        def generate_inputs(cls):
            strlen, listlen = randint(1, 10), randint(1, 10)
            strings = [generate_string(strlen) for _ in range(listlen)]
            return dict(
                strings=strings,
            )

        hints = """
This is NOT similar to the previous exercises on this page.
Think about the solution when there's just two strings. How can you generalize it to a list of strings?
You'll need to go through the first letters, then the second letters, and so on.
You'll have to use a loop, but how long should the loop take?
Remember that strings in the list have equal lengths.
For each position (first, second etc.) define a new string.
What should that string be initially?
For each position (first, second etc.) you'll have to go through each string in the list.
You'll need another loop inside the one you have.
        """

        tests = [
            (["abc", "def", "ghi"], """\
adg
beh
cfi
"""),
            (["  b n", "f ete", "liths", "astat", "t ene", "  r d"], """\
 flat 
  is  
better
 than 
nested
""")
        ]

    class zip_longest_strings_exercise(ExerciseStep):
        text = """
Excellent! If you'd like, you can just continue to the [next page](#DefiningFunctions) now.
Or you can do a bonus challenge!

Now let's generalize the previous exercise to strings of unequal length. Once again you are given a list of strings.
Like before, write a program that prints the first letter of each string together on one line,
then the second letters together on the next line, and so on.
But this time, if a string does not have enough letters, it should print a space.

For example, if

    strings = ["abcqwe", "def", "ghiq"]

your program should print

    adg
    beh
    cfi
    q q
    w  
    e  
        """

        def solution(self, strings: List[str]):
            lengths = []
            for string in strings:
                lengths.append(len(string))
            length = max(lengths)

            for i in range(length):
                line = ""
                for string in strings:
                    if i >= len(string):
                        line += " "
                    else:
                        line += string[i]
                print(line)

        hints = """
Since the strings can have different lengths, this is a bit tricky.
For how long should your outer loop go this time?
Before you start handling the strings, it might be a good idea to find the longest string length first.
The rest is very similar to the previous exercise.
The only difference is that now you have to determine whether to add a letter from a string, or a space.
        """

        tests = [
            (["abcqwe", "def", "ghiq"], """\
adg
beh
cfi
q q
w  
e  
""")
        ]

    final_text = """
You have mastered nested lists and how to combine them with nested loops.
Brilliant! You now have extremely powerful programming tools in your tool belt.
    """
