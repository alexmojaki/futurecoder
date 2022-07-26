# flake8: NOQA E501
import ast
import itertools
from copy import deepcopy
from random import choice, randint
from string import ascii_uppercase
from textwrap import dedent
from typing import List

from core import translation as t
from core.exercises import assert_equal, ExerciseError
from core.text import ExerciseStep, Page, MessageStep, Disallowed, VerbatimStep
from core.utils import returns_stdout, shuffled, wrap_solution


def generate_board(board_type):
    winning = choice([True, False])
    size = randint(3, 9)
    char1 = choice(ascii_uppercase)
    char2 = choice(ascii_uppercase)
    chars = [char1, char2, ' ']
    board = [[choice(chars) for _ in range(size)] for _ in range(size)]

    if winning:
        winning_piece = choice([char1, char2])
        if board_type == 'row':
            row = randint(0, size - 1)
            board[row] = [winning_piece for _ in range(size)]
        if board_type == 'col':
            col = randint(0, size - 1)
            for i in range(size):
                board[i][col] = winning_piece
        if board_type == 'diag':
            diag = choice([True, False])
            for i in range(size):
                if diag:
                    board[i][i] = winning_piece
                else:
                    board[i][-i - 1] = winning_piece
    else:
        diag = choice([True, False])
        for i in range(size):
            if diag:
                board[i][i] = ' '
            else:
                board[i][-i - 1] = ' '
        if (size % 2) == 0:
            if diag:
                board[0][-1] = ' '
            else:
                board[0][0] = ' '
    return board


class IntroducingTicTacToe(Page):
    title = "Checking the board for winners"

    class intro_row_winner(ExerciseStep):
        """
You've done many short exercises solving one little problem. Now we're going to tackle a larger, more complex
project which will really test your knowledge and require combining many smaller parts together.
It's going to be so fun!

You will develop a text-based interactive tic-tac-toe game to be played by 2 human players.
Here is a small preview of what the finished game will look like in play:

      1 2 3
    1  | |
      -+-+-
    2  | |
      -+-+-
    3  | |

    X to play:
    1
    1

      1 2 3
    1 X| |
      -+-+-
    2  | |
      -+-+-
    3  | |

    O to play:
    2
    2

      1 2 3
    1 X| |
      -+-+-
    2  |O|
      -+-+-
    3  | |

    X to play:
    1
    3

      1 2 3
    1 X| |X
      -+-+-
    2  |O|
      -+-+-
    3  | |

We will break up the project into several small functions, which will be exercises.

You will use many of the concepts you have learned so far: strings,
nested lists, nested loops, `range`, calling functions within functions, comparisons, and booleans.

Along the way you will also learn some new concepts, including newline characters, types, and `input()`.

Here is a rough outline of the project:

- three functions `row_winner`, `column_winner`,  `diagonal_winner`  that check the whole board for winning rows, columns, and diagonals
- a function `winner` that checks the whole board for a winner, combining the above functions
- a function `format_board` that displays the current state of the game
- a function `play_move` that takes user input to play a move,
- finally a `play_game` function that puts it all together and runs the game interactively.
- Later on we will add further improvements.

Let's get started!

As in the last chapter, we will represent the tic-tac-toe board as a nested list of strings.
For a typical game this will be a 3x3 list, i.e. 3 lists each containing 3 strings, with players represented by `'X'` or `'O'`.
Empty squares will be represented by a space, i.e. `' '`. For example:

    board = [
        ['X', 'O', 'X'],
        ['O', ' ', ' '],
        [' ', 'X', 'O']
    ]

However to make things more interesting your code will need to work for square boards of any size
(4x4, 5x5, etc) where players can be represented by any strings, e.g.

    board = [
        ['A', 'B', 'A', 'A'],
        ['B', ' ', ' ', 'A'],
        [' ', 'A', 'B', 'B'],
        [' ', 'A', 'B', ' ']
    ]

Write a function `row_winner` which returns `True` if `board` contains
a winning row, i.e. a horizontal line which has the same character in all its entries (except `' '`):

    __copyable__
    def row_winner(board):
        ...

    assert_equal(
        row_winner(
            [
                ['A', 'A', 'B', 'A'],
                [' ', ' ', ' ', ' '],
                ['A', ' ', ' ', 'A'],
                ['B', ' ', 'B', 'A']
            ]
        ),
        False
    )
    assert_equal(
        row_winner(
            [
                ['X', ' ', 'X'],
                ['O', 'X', 'X'],
                ['O', 'O', 'O']
            ]
        ),
        True
    )

In the second example, `O` wins in the bottom row.
        """

        hints = """
You need to check every row in the board, so you'll need a loop for that.
How can you check if all entries in a row are equal to each other?
That's a self contained problem on its own. You can start by forgetting about the whole board and just checking a single row.
You could even write a function which just does this, although you don't have to.
Since the row could have any size, you'll have to loop all the way through it.
For each row, define a boolean. Then loop through that row, updating the boolean accordingly.
You can use the first entry `row[0]` in a row to compare all the row entries to it.
Think carefully about what the initial value of the boolean should be, and under what conditions you should change its value.
After looping through a row, if you determined that all its entries are equal, then return `True` (ending the outer loop early).
Make sure you don't return `True` for a row filled with spaces.
Make sure you return `False` if there are no winning rows
"""

        parsons_solution = True

        def solution(self):
            def row_winner(board: List[List[str]]):
                for row in board:
                    all_equal = True
                    piece = row[0]
                    for entry in row:
                        if entry == ' ' or piece != entry:
                            all_equal = False
                            break
                    if all_equal:
                        return True
                return False

            return row_winner

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board('row')
            }

        tests = [
            ([[" ", " ", " "],
              ["A", "A", "B"],
              ["B", "B", "A"]], False),
            ([["S", "S", "S", "S"],
              ["M", "M", "S", " "],
              [" ", "S", "M", "S"],
              [" ", "M", " ", "S"]], True),
            ([["X", "O", " ", "X", "X"],
              ["X", "O", " ", "X", "X"],
              [" ", "O", "X", "X", " "],
              ["X", "X", "X", "X", " "],
              ["X", "O", "O", "X", "O"]], False),
        ]

        class catch_empty_row(ExerciseStep, MessageStep):
            """
Keep in mind that some entries might be `' '`. An empty row is not a winning row.
            """

            def solution(self):
                def row_winner(board: List[List[str]]):
                    for row in board:
                        all_equal = True
                        piece = row[0]
                        for entry in row:
                            if piece != entry:
                                all_equal = False
                                break
                        if all_equal:
                            return True
                    return False

                return row_winner

            tests = [
                ([[" ", " ", " "],
                  ["A", "A", "B"],
                  ["B", "B", "A"]], True),
                ([[" ", "A", " "],
                  ["A", "A", "B"],
                  ["B", "B", "A"]], False),
                ([["S", "S", "S", "S"],
                  [" ", " ", " ", " "],
                  ["S", "S", "M", "S"],
                  ["M", "M", " ", "S"]], True),
                ([["S", "S", "M", "S"],
                  [" ", " ", "M", " "],
                  ["S", "S", "M", "S"],
                  ["M", "M", " ", "S"]], False),
                ([["S", "S", "M", "S"],
                  [" ", " ", " ", " "],
                  ["S", "S", "M", "S"],
                  ["M", "M", " ", "S"]], True),
                ([["X", "O", " ", "X", "X"],
                  ["X", "O", " ", "X", "X"],
                  [" ", "O", "O", "O", " "],
                  ["X", "X", "X", "X", " "],
                  [" ", " ", " ", " ", " "]], True),
            ]

    class column_winner(ExerciseStep):
        """
Great job!

Now write a similar function `column_winner` which checks for a winning *column* (a vertical line) of either piece:

    __copyable__
    def column_winner(board):
        ...

    assert_equal(
        column_winner(
            [
                ['X', 'O', ' '],
                ['X', 'O', ' '],
                ['O', 'X', ' ']
            ]
        ),
        False
    )
    assert_equal(
        column_winner(
            [
                ['X', 'O', ' ', 'X'],
                [' ', 'O', 'X', 'O'],
                ['O', 'O', 'X', 'X'],
                ['O', 'O', 'X', ' ']
            ]
        ),
        True
    )

Here `O` won in the second column of the second board.
        """

        hints = """
You can start by imitating `row_winner` above, then change it to make it work with columns.
You can't loop through the columns of `board` as simply as its rows.
What *is* a column of a nested list? The first column consists of the first element of the first row, the first element of the second row, etc.
Looping through all columns means looking at the first element of every row, then the second element of every row, etc.
So you need to loop through numbers representing the positions first, second, etc.
How do you find the number of columns in `board`?
That covers the outer loop, which goes through each column. Then you need an inner loop to go through each element in the column.
The different entries of a column are NOT on the same row. So how can you access them?
You can loop through rows of the board and find the element corresponding to that row and the current column.
To access all the entries of, say, the 5th column, you can loop through all the rows, and access the 5th element in each row.
Define a boolean for each column, then update it accordingly inside the inner loop.
The rest of the logic is very similar to `row_winner`.
Watch out for `' '`.
Remember to return `False` at the end if needed.
"""

        parsons_solution = True

        def solution(self):
            def column_winner(board: List[List[str]]):
                for col in range(len(board[0])):
                    all_equal = True
                    piece = board[0][col]
                    for row in board:
                        if row[col] == ' ' or row[col] != piece:
                            all_equal = False
                            break
                    if all_equal:
                        return True
                return False

            return column_winner

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board('col')
            }

        tests = [
            ([[" ", "A", "B"],
              [" ", "A", "B"],
              [" ", "B", "A"]], False),
            ([["S", "M", " ", "M"],
              ["S", "M", "S", " "],
              ["S", "S", "M", "S"],
              ["S", "M", " ", "S"]], True),
            ([["X", "O", " ", "X", "O"],
              ["O", "O", "O", "O", "O"],
              ["X", "O", "O", "O", " "],
              ["X", "O", "O", "X", " "],
              ["O", "X", " ", "O", "O"]], False),
        ]

    class diagonal_winner(ExerciseStep):
        """
Excellent! That was challenging.

Finally we need to check for winning diagonals. You already wrote a function to do just that in the previous chapter, for 3-by-3 boards:

    def diagonal_winner(board):
        middle = board[1][1]
        return (
                (middle == board[0][0] and middle == board[2][2]) or
                (middle == board[0][2] and middle == board[2][0])
        )

Now write a `diagonal_winner` that works for square boards of any size: 4-by-4, 5-by-5, and so on...

    __copyable__
    def diagonal_winner(board):
        ...

    assert_equal(
        diagonal_winner(
            [
                ['O', 'X', 'O', 'X'],
                [' ', 'O', 'X', ' '],
                ['X', 'X', ' ', 'X'],
                ['X', ' ', 'O', 'O']
            ]
        ),
        True
    )
    assert_equal(
        diagonal_winner(
            [
                ['X', 'X', ' '],
                ['X', ' ', 'O'],
                [' ', 'O', 'O']
            ]
        ),
        False
    )

In the first example, `X` won in the diagonal going from the bottom left to the top right.
        """

        hints = """
How many diagonals are there on a square board of arbitrary size?
Even if the size of the board changes, the number of diagonals remains the same!
You can't do something like `middle == board[0][0] and middle == board[2][2]` this time, because you don't know how long a diagonal is.
Moreover the two diagonals might not have anything in common like `middle`.
First, focus on the diagonal that goes from top left to bottom right.
How can you access those entries with double subscripting?
Do you see a pattern in those double subscripts? Get some paper and pen, work it out on some examples.
Now focus on the other diagonal (from top right to bottom left). There is a pattern in the subscripts again, but it's a little bit more difficult.
Do you remember negative indexing? It might be helpful here.
Once you get the hang of the patterns, use the same ideas from before to check if all entries are equal.
You can use one loop and check both diagonals at the same time. Or you can use one loop for each diagonal.
"""

        parsons_solution = True

        def solution(self):
            def diagonal_winner(board: List[List[str]]):
                all_equal1 = True
                all_equal2 = True
                topleft = board[0][0]
                topright = board[0][-1]
                for i in range(len(board)):
                    if board[i][i] == ' ' or board[i][i] != topleft:
                        all_equal1 = False
                    if board[i][-i - 1] == ' ' or board[i][-i - 1] != topright:
                        all_equal2 = False
                return all_equal1 or all_equal2

            return diagonal_winner

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board('diag')
            }

        tests = [
            ([[" ", "A", " "],
              ["B", " ", "B"],
              [" ", "B", " "]], False),
            ([["S", "M", " ", "M"],
              ["S", "S", "S", " "],
              ["S", "S", "S", "S"],
              [" ", "M", " ", "S"]], True),
            ([["S", "M", " ", "M"],
              [" ", "S", "M", " "],
              ["S", "M", " ", "S"],
              ["M", " ", " ", "M"]], True),
            ([["X", " ", " ", " ", "X"],
              [" ", "O", " ", "X", " "],
              [" ", " ", "X", " ", " "],
              [" ", "X", " ", "O", " "],
              ["O", " ", " ", " ", "O"]], False),
        ]

    class winner(ExerciseStep):
        """
Bravo! That was quite tough.

Now we can put the three functions together! Write a function `winner` that takes an argument `board` as before,
and returns `True` if `board` contains either a winning row, column or diagonal, `False` otherwise.

Your solution should work by calling the three functions. `winner` itself should not do any
looping, subscripting, etc.

Here is some code for `row_winner`, `column_winner` and `diagonal_winner`, along with some tests for `winner`.
Click the Copy button, and fill in the blanks for your `winner` function.

    __copyable__
    def winner(board):
        ...

    def winning_line(strings):
        piece = strings[0]
        if piece == ' ':
            return False
        for entry in strings:
            if piece != entry:
                return False
        return True

    def row_winner(board):
        for row in board:
            if winning_line(row):
                return True
        return False

    def column_winner(board):
        for col in range(len(board[0])):
            column = []
            for row in board:
                column.append(row[col])
            if winning_line(column):
                return True
        return False

    def diagonal_winner(board):
        diagonal1 = []
        diagonal2 = []
        for i in range(len(board)):
            diagonal1.append(board[i][i])
            diagonal2.append(board[i][-i-1])
        return winning_line(diagonal1) or winning_line(diagonal2)

    assert_equal(
        winner(
            [
                ['X', 'X', 'X', ' '],
                ['X', 'X', ' ', ' '],
                ['X', ' ', 'O', 'X'],
                [' ', ' ', 'O', 'X']
            ]
        ),
        False
    )
    assert_equal(
        winner(
            [
                ['X', ' ', 'X'],
                ['O', 'X', 'O'],
                ['O', 'O', 'O']
            ]
        ),
        True
    )
    assert_equal(
        winner(
            [
                ['X', ' '],
                ['X', 'O']
            ]
        ),
        True
    )

        """

        hints = """
The solution is quite short! Simply use the three functions correctly.
Think about possible cases. When does `winner(board)` return `False`? When does it return `True`?
How can you use the three functions and a boolean operator together to get the result you need?
"""

        disallowed = Disallowed((ast.For, ast.Subscript), function_only=True, message="""
Your solution should work by calling the three functions. `winner` itself should not do any
looping, subscripting, etc. It should be very short.

Copy the `row_winner` and other functions and leave them as they are. Don't copy code from them
into the `winner` function, just call those functions.
""")

        def solution(self):
            def winning_line(strings):
                piece = strings[0]
                if piece == ' ':
                    return False
                for entry in strings:
                    if piece != entry:
                        return False
                return True

            def row_winner(board):
                for row in board:
                    if winning_line(row):
                        return True
                return False

            def column_winner(board):
                for col in range(len(board[0])):
                    column = []
                    for row in board:
                        column.append(row[col])
                    if winning_line(column):
                        return True
                return False

            def diagonal_winner(board):
                diagonal1 = []
                diagonal2 = []
                for i in range(len(board)):
                    diagonal1.append(board[i][i])
                    diagonal2.append(board[i][-i - 1])
                return winning_line(diagonal1) or winning_line(diagonal2)

            def winner(board: List[List[str]]):
                return row_winner(board) or column_winner(board) or diagonal_winner(board)

            return winner

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board(choice(['row', 'col', 'diag']))
            }

        tests = [
            ([[" ", "A", "B"],
              [" ", "A", "B"],
              [" ", "B", "A"]], False),
            ([[" ", "A", "A"],
              [" ", "A", "B"],
              ["B", "B", "B"]], True),
            ([["S", "M", " ", "M"],
              ["S", "M", "S", " "],
              ["S", "S", "M", "S"],
              ["S", "M", " ", "S"]], True),
            ([["O", "O", " ", "X", "X"],
              ["X", "O", "O", "X", "X"],
              ["X", "O", "O", "O", " "],
              ["X", "O", "O", "O", " "],
              ["O", "X", " ", "O", "O"]], True),
        ]

    final_text = """
Great work!

Now we have the code to determine a winning state on the board.
"""


class NewlinesAndFormatBoard(Page):
    title = "The newline character, `format_board`"

    class one_way_to_print_board(VerbatimStep):
        """
Next we want to tackle the problem of displaying the tic-tac-toe board. Here's one way to do this:

    __copyable__
    __program_indented__

(What's `"".join`? Google it!)
        """

        def program(self):
            def print_board(board):
                for row in board:
                    print("".join(row))

            print_board([
                ['X', 'O', 'X'],
                [' ', 'O', 'O'],
                [' ', 'X', ' ']
            ])

    class invalid_multi_line_string(VerbatimStep):
        """
This is a good start but ideally we'd like a function which *returns* a string rather than printing it.
This way other code can make easy use of the string in different ways. We might want to manipulate the string
(e.g. draw a box around it or extract only the first few lines), we might want to send it somewhere other than the screen
(e.g. a file) and in this particular case we want to be able to test it with `assert_equal`. This doesn't work:

    assert_equal(print_board([...]), "...")

because `print_board` doesn't use `return` so it just returns `None` by default.
So instead we want code like this:

    def format_board(board):
        ...
        return ...

    assert_equal(format_board([...]), "...")

Then `print(format_board(board))` should print something like what we saw at the beginning.
But how do we return a string with multiple lines? And how do we test it? We'd like to do something like this:

    __copyable__
    __program_indented__

See for yourself how this doesn't work.
        """

        program = """\
assert_equal(
    format_board([
        ['X', 'O', 'X'],
        [' ', 'O', 'O'],
        [' ', 'X', ' ']
    ]),
    "XOX
      OO
      X "
)"""

        def check(self):
            return 'SyntaxError: EOL while scanning string literal' in self.result

    class multi_line_strings_triple_quotes(VerbatimStep):
        """
Normally a string literal has to be on one line, so this is invalid:

    string = "First line
    Second line"
    print(string)

But Python provides a way! The solution is to use *triple quotes*, i.e. three quote characters in a row
(either `'''` or `\"""`) around the contents of the string. Run the following:

__program_indented__
        """

        # Auto-translation of the body of `def program` is broken by the multiline string
        auto_translate_program = False

        def program(self):
            string = """First line
            Second line"""
            print(string)

    class discovering_newline(VerbatimStep):
        """
Hooray! A *triple quoted string* is allowed to span many lines and they will be shown in the output.

Like single and double quotes, triple quotes are just another kind of notation, not a new kind of string.
`\"""abc\"""` is the same thing as `"abc"`.

However `string` does contain something new. Run `__program__` in the shell to see.
        """

        expected_code_source = "shell"

        program = "string"

        class special_messages:
            class bad_string:
                """
                Oops, `string` doesn't have the right value. Run the program from the previous step again.
                """

                program = "string = 'a'"

        @classmethod
        def pre_run(cls, runner):
            runner.console.locals[cls.program] = "First line\nSecond line"

        def check(self):
            string = self.console.locals.get(self.program, "")
            if not (isinstance(string, str) and '\n' in string):
                return self.special_messages.bad_string
            return super().check()

    class introducing_newline(VerbatimStep):
        """
There's the secret!

`\\n` represents a ***newline*** character. This is just another character, like a letter or a space (`' '`).
It's the character between two separate lines that you type in by pressing Enter on your keyboard.

Again, `\\n` *represents* the newline character within a Python string literal.
The string doesn't actually contain `\\` and `n`, it just contains one character. Check this in the shell:

    __program_indented__
        """

        expected_code_source = "shell"

        program = "len('\\n')"

        predicted_output_choices = ["1", "2"]

    class format_board_simple(ExerciseStep):
        """
Now use the newline character to write the function `format_board` (your solution should work for a square `board` of any size):

    __copyable__
    def format_board(board):
        ...

    assert_equal(
        format_board([
            ['X', 'O', 'X'],
            ['O', ' ', ' '],
            [' ', 'X', 'O']
        ]),
        'XOX\\nO  \\n XO'
    )

        """

        hints = """
Look carefully at the test case we provided. It shows you all you need!
You need to build up a string for the whole board. Start with an empty string.
For each row, add the characters from that row to the string.
You'll need a nested loop.
When you reach the end of a row, you need to add a newline before the next row.
`'\\n'` is just like any other character! You can add it as usual with `+`.
Notice that the end of the last row is different than the others.
Before you add a newline, you'll need to check if it's the last row or not.
Your outer loop should loop over the length of the board.
Then check if you are at the last index or not.
"""

        # TODO message step for trailing newline?

        parsons_solution = True

        def solution(self):
            def format_board(board: List[List[str]]):
                result = ''
                for i in range(len(board)):
                    for char in board[i]:
                        result += char
                    if i != len(board) - 1:
                        result += '\n'
                return result

            return format_board

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board('row')
            }

        tests = [
            ([[" ", " ", " "],
              ["X", "X", "O"],
              ["O", "O", "X"]], "   \nXXO\nOOX"),
            ([["X", "X", "X", "X"],
              ["O", "O", "X", " "],
              [" ", "X", "O", "O"],
              [" ", "O", " ", "O"]], "XXXX\nOOX \n XOO\n O O"),
            ([["X", "O", " ", "X", "X"],
              ["X", "O", " ", "X", "X"],
              [" ", "O", "X", "X", " "],
              ["X", "X", "X", "X", " "],
              ["X", "O", "O", "X", "O"]], "XO XX\nXO XX\n OXX \nXXXX \nXOOXO"),
        ]

    class format_board_bonus_challenge(ExerciseStep):
        """
Excellent! A typical solution looks like:

    def format_board(board):
        result = ''
        for i in range(len(board)):
            for char in board[i]:
                result += char
            if i != len(board) - 1:
                result += '\\n'
        return result

If you looked up how `join` works and used it in your solution, that's great!
You might have solved it with something like this:

    def format_board(board):
        joined_rows = []
        for row in board:
            joined_rows.append("".join(row))
        return "\\n".join(joined_rows)

If you'd like, you can just continue to the [next page](#Types) now. Or you can do a bonus challenge!

Write an improved version of `format_board` that displays row and column separators. For example, if

    board = [
        ['X', 'O', 'X'],
        [' ', 'O', 'O'],
        [' ', 'X', ' ']
    ]

then `print(format_board(board))` should print

    X|O|X
    -+-+-
     |O|O
    -+-+-
     |X|

Once again it should work for a square `board` of *any size*.

You are strongly encouraged to use `join` on this exercise. We provide one test as before, you can write additional tests:

    __copyable__
    def format_board(board):
        ...

    assert_equal(
        format_board([
            ['X', 'O', 'X'],
            ['O', ' ', ' '],
            [' ', 'X', 'O']
        ]),
        'X|O|X\\n-+-+-\\nO| | \\n-+-+-\\n |X|O'
    )

        """

        hints = """
There are two types of lines to be displayed: one type has the pieces joined by `|`s in between them, the other type has `-`s joined by `+`s in between them.
Both of these types of lines can be built up by using `join` appropriately.
For example, how can you convert a row `['X', 'O', 'X']` into `'X|O|X'` using `join`?
Similarly, how can you obtain `'-+-+-'` using `join`? To what list should you apply `join`?
Once you figured out how to build up both types of lines, how can you combine them to obtain the final result?
Notice that the lines with the `+-`  signs are always the same.
And there is one line with `+-` separating every consecutive pair of lines with pieces.
You can use `join` on the lines themselves!
The lines with the pieces can be joined together with the `+-` line in between them (with newlines added in appropriate places).
To do that, first you need to keep the lines with the pieces stored in a list as you are building them.
Then apply `join` to that list, with the `+-` line as separator.
To add the newlines to the `+-` line correctly, take a look at the test case we provided.
"""

        parsons_solution = True

        def solution(self):
            def format_board(board: List[List[str]]):
                joined_rows = []
                for row in board:
                    joined_rows.append("|".join(row))
                lines = []
                for _ in board[0]:
                    lines.append("-")
                line = f'\n{"+".join(lines)}\n'
                return line.join(joined_rows)

            return format_board

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board('row')
            }

        tests = [
            ([[" ", " ", " "],
              ["X", "X", "O"],
              ["O", "O", "X"]], " | | \n-+-+-\nX|X|O\n-+-+-\nO|O|X"),
            ([["X", "X", "X", "X"],
              ["O", "O", "X", " "],
              [" ", "X", "O", "X"],
              [" ", "O", " ", "X"]], "X|X|X|X\n-+-+-+-\nO|O|X| \n-+-+-+-\n |X|O|X\n-+-+-+-\n |O| |X"),
            ([["X", "O", " ", "X", "X"],
              ["X", "O", " ", "X", "X"],
              [" ", "O", "X", "X", " "],
              ["X", "X", "X", "X", " "],
              ["X", "O", "O", "X", "O"]],
             "X|O| |X|X\n-+-+-+-+-\nX|O| |X|X\n-+-+-+-+-\n |O|X|X| \n-+-+-+-+-\nX|X|X|X| \n-+-+-+-+-\nX|O|O|X|O"),
        ]

    final_text = """
Great work! That was quite challenging.

Now you have mastered how to build up a string of multiple lines of text, and solved the problem of displaying the board to the players.

Next you will learn more about types in Python and how to convert them, and how to get input from the players.
You are already about halfway done with the project. Keep going!
    """


class Types(Page):
    class five_different_types(VerbatimStep):
        """
So far we've seen various kinds of data: strings, lists, numbers and booleans.
These are called *types*. Every value has a type which affects how it behaves
and can be revealed with the `type` function:

    __copyable__
    __program_indented__
        """

        def program(self):
            print(type('Hello World'))
            print(type(23))
            print(type(True))
            print(type([1, 2, 3]))
            print(type(4.56))

    class check_type_manually(VerbatimStep):
        """
Python reports first that `type('Hello World')` is `<class 'str'>`. Don't worry about `class` for now.
`str` is short for *string*.

Then `True` is a `bool` (short for *boolean*) and `[1, 2, 3]` has type `list`.

Note that there are two types for numbers:

- `int`, short for 'integer', is for whole numbers, meaning no fractions or decimal points.
- `float`, short for 'floating point number', is for numbers with a decimal point and maybe a fractional part

In most cases you don't have to worry about the different types of number, as you can mix the two when doing maths.

Types are values which can be used in various ways, just like other values.
For example, try this in the shell:

__program_indented__
        """

        expected_code_source = 'shell'

        program = 'type(3) == int'

    class different_types_look_same(VerbatimStep):
        """
Values with different types are usually quite different from each other, but they can look the same when printed,
which can be confusing. Try this:

    __copyable__
    __program_indented__

(You can use `print(repr(123))` and `print(repr('123'))` to tell the difference. What's `repr`? Google it!)
        """

        def program(self):
            print('123')
            print(123)
            print(123 == '123')

    class plus_has_two_meanings(VerbatimStep):
        """
Different types have different methods and support different operators.
The same method or operator can also mean different things.
For example, see how `+` has different meanings for `str` and `int`:

    __copyable__
    __program_indented__
        """

        predicted_output_choices = [
            "579\n579",
            "579\n'579'",
            "123456\n123456",
            "123456\n'123456'",
            "579\n123456",
            "579\n'123456'",
        ]

        def program(self):
            print(123 + 456)
            print('123' + '456')

    class less_than_has_two_meanings(VerbatimStep):
        """
For two integers `+` acts as addition, whereas for two strings it acts as string concatenation.
Python automatically figures out the meaning of `+` from the types of the inputs.
Similarly `<` acts differently on two strings and two integers:

    __copyable__
    __program_indented__
        """

        translate_output_choices = False
        predicted_output_choices = [
            "True\nTrue",
            "True\nFalse",
            "False\nTrue",
            "False\nFalse",
        ]

        def program(self):
            print(13 < 120)
            print('13' < '120')

    class less_than_sorting_strings(VerbatimStep):
        """
So `<` acts as the usual 'less than' between two integers, because `13` is less than `120`,
but it acts as the dictionary ordering between two strings: `13` is 'alphabetically' after `120`
because `3` comes after `2`.

See what difference this makes when sorting a list:

    __copyable__
    __program_indented__
        """

        predicted_output_choices = [
            "[0, 13, 120]\n['0', '120', '13']",
            "[0, 13, 120]\n['13', '120', '0']",
            "[0, 13, 120]\n['120', '13', '0']",
            "[120, 13, 0]\n['0', '120', '13']",
            "[120, 13, 0]\n['13', '120', '0']",
            "[120, 13, 0]\n['120', '13', '0']",
        ]

        def program(self):
            print(sorted([120, 13, 0]))
            print(sorted(['120', '13', '0']))

    class common_type_errors(VerbatimStep):
        """
What happens if you use an operator between a `str` and an `int`? Try in the shell:

__program_indented__
        """

        correct_output = "Error"

        predicted_output_choices = ["46", "'46'", "1234", "'1234'"]

        expected_code_source = "shell"

        program = "12 + '34'"

        def check(self):
            return "TypeError: unsupported operand type(s) for +: 'int' and 'str'" in self.result

    class fixing_type_errors_with_conversion(ExerciseStep):
        """
Using a string instead of an integer in `range` like `range('5')`,
or in list subscripting like `list['3']` will also lead to an error.

Most of these problems can be solved by converting the string to an integer by using `int` as a function:
`int('5')` will return the integer `5`.
Similarly an integer can be converted to a string by using `str` as a function:
`str(5)` will return the string `'5'`.

Using this new knowledge, fix this broken program:

    __copyable__
    number = '3'
    for i in range(number):
        print('Starting... ' + i + 1)
    print('Go!')

The correct program should print:

    Starting... 1
    Starting... 2
    Starting... 3
    Go!

Your solution should work for any value of the variable `number`.

        """

        hints = """
At what points is this code broken?
There are values that need to be converted to a different type.
Specifically there's a `str` that needs to be converted to an `int`.
And an `int` that needs to be converted to a `str`.
        """

        tests = [
            ('1', """\
Starting... 1
Go!
            """),
            ('2', """\
Starting... 1
Starting... 2
Go!
            """),
            ('3', """\
Starting... 1
Starting... 2
Starting... 3
Go!
            """),
        ]

        disallowed = Disallowed(ast.JoinedStr, label="f-strings")

        translated_tests = True

        def solution(self, number: str):
            for i in range(int(number)):
                print('Starting... ' + str(i + 1))
            print('Go!')

        @classmethod
        def generate_inputs(cls):
            return {
                "number": str(randint(1, 10))
            }

    class format_board_with_numbers(ExerciseStep):
        """
Write an improved version of `format_board` that has row and column numbers like this:

     123
    1XOX
    2 OO
    3 X

It should work for boards of any single-digit size. Here's a test case:

    __copyable__
    def format_board(board):
        ...

    assert_equal(
        format_board([
            ['X', 'O', 'X'],
            ['O', ' ', ' '],
            [' ', 'X', 'O']
        ]),
        ' 123\\n1XOX\\n2O  \\n3 XO'
    )

        """

        hints = """
You can start by using the ideas from your previous solution to `format_board`. Using `join` is highly recommended!
The first line has to be treated separately from the rest.
Remember that `range` yields numbers in the way: 0, 1, 2, ...
We want numbers on the first line like this: 1, 2, 3...
Each number has to be converted to a string before being added to the first row!
For the rows of the board itself, do something similar.
Start with a list consisting only of the first line that you built above.
Add each row's string to the list, then join the list with a newline character.
        """

        parsons_solution = True

        def solution(self):
            def format_board(board: List[List[str]]):
                first_row = ' '
                for i in range(len(board)):
                    first_row += str(i + 1)
                joined_rows = [first_row]
                for i in range(len(board)):
                    joined_row = str(i + 1) + ''.join(board[i])
                    joined_rows.append(joined_row)
                return "\n".join(joined_rows)

            return format_board

        @classmethod
        def generate_inputs(cls):
            return {
                "board": generate_board('row')
            }

        tests = [
            ([[" ", " ", " "],
              ["X", "X", "O"],
              ["O", "O", "X"]], " 123\n1   \n2XXO\n3OOX"),
            ([["X", "X", "X", "X"],
              ["O", "O", "X", " "],
              [" ", "X", "O", "X"],
              [" ", "O", " ", "X"]], " 1234\n1XXXX\n2OOX \n3 XOX\n4 O X"),
            ([["X", "O", " ", "X", "X"],
              ["X", "O", " ", "X", "X"],
              [" ", "O", "X", "X", " "],
              ["X", "X", "X", "X", " "],
              ["X", "O", "O", "X", "O"]],
             " 12345\n1XO XX\n2XO XX\n3 OXX \n4XXXX \n5XOOXO"),
        ]

    final_text = """
Excellent!

By the way, when you need to concatenate strings and numbers, remember that you can also
use f-strings. They often look nicer.

You've learned about types in Python and how to avoid common errors by converting types.
Keep going with the rest of the project!
    """


class InteractiveProgramsWithInput(Page):
    title = "Interactive Programs with `input()`"

    class first_input(VerbatimStep):
        """
The programs we have written so far are not interactive.
To make our interactive Tic-tac-toe game, we will need a method of receiving input from the players.
Python allows us to do that with the built-in `input` function. Run this program:

    __copyable__
    __program_indented__

When `name = input()` runs, the program actually stops and waits for you to type in the shell and press Enter,
so you will need to do that for it to complete.
        """

        stdin_input = "there"

        def program(self):
            print('Type your name, then press Enter:')
            name = input()
            print(f'Hello {name}!')

    class convert_input_to_int(ExerciseStep):
        """
Whatever you typed in (not including pressing Enter at the end) is returned from the `input()` function as a string.

It's essential to understand that `input()` ***always returns a string***, no matter what the user typed in.
It's up to you to convert that string to the type you need.
Forgetting this detail is a common source of confusing bugs.

For example, this program looks fine at a glance, but if you try it out you'll see that it doesn't actually work:

    __copyable__
    super_secret_number = 7
    print("What number am I thinking of?")
    guess = input()
    if guess == super_secret_number:
        print("Amazing! Are you psychic?")
    else:
        print("Nope!")

Fix the program so that when the user inputs `7` the program prints `Amazing! Are you psychic?` as expected.
        """

        hints = """
`input()` always returns a string.
A string that looks like a number is still a string, not a number.
In `super_secret_number = 7`, `7` is a number, not a string.
That makes `super_secret_number` also a number.
A string cannot equal a number.
To check that two values are equal, make sure they're the same type first.
So to compare a number and a string, first convert the number to a string or convert the string to a number.
You learned how to convert between strings and numbers in the previous page.
Use `int()` to convert to an integer (whole number) or `str()` to convert to a string.
        """

        translated_tests = True

        def solution(self):
            super_secret_number = 7
            print("What number am I thinking of?")
            guess = input()
            if int(guess) == super_secret_number:
                print("Amazing! Are you psychic?")
            else:
                print("Nope!")

        @classmethod
        def generate_inputs(cls):
            return {
                "stdin_input": str(randint(1, 10))
            }

        tests = [
            ({"stdin_input": "7"}, "What number am I thinking of?\n<input: 7>\nAmazing! Are you psychic?"),
            ({"stdin_input": "0"}, "What number am I thinking of?\n<input: 0>\nNope!"),
            ({"stdin_input": "1"}, "What number am I thinking of?\n<input: 1>\nNope!"),
        ]

    final_text = """
Perfect!

There's at least three fixes that would work here. You can convert the input to a number:

    if int(guess) == super_secret_number:

or convert the correct answer to a string:

    if guess == str(super_secret_number):

or just make it a string to begin with:

    super_secret_number = '7'

    """


class NestedListAssignment(Page):
    title = "Nested List Assignment: Playing Moves on the Board"

    class modify_list_in_function(VerbatimStep):
        """
We've seen how to get input from the user, now let's use that to actually put pieces
on the board and play the game. For starters, try out this code:

    __copyable__
    __program_indented__
        """

        translate_output_choices = False
        predicted_output_choices = [
            "X",
            "' '",
            "'X'",
            "[' ']",
            "['X']",
            "[' ', ' ', ' ']",
            "['X', ' ', ' ']",
            "[' ', 'X', ' ']",
            "[' ', ' ', 'X']",
        ]

        def program(self):
            def play_move(board, player):
                board[1] = player

            def play_game():
                game_board = [" ", " ", " "]
                play_move(game_board, "X")
                print(game_board)

            play_game()

    class nested_assignment_two_lines(VerbatimStep):
        """
Note how calling `play_move(game_board, 'X')` actually *modifies* `game_board` directly.
The variable `board` inside the call to `play_move` and
the variable `game_board` inside the call to `play_game` point to the same list object.
There's no copying. Python Tutor is good at showing this with arrows.

This also means that in this case there's no need for `play_move` to return anything,
it can just modify `board` and the caller (`play_game` in this case) will see the effect.

However, our board is two dimensional, represented by a nested list.
So we need to assign `player` to an element of an inner list, something like this:

    __copyable__
    __program_indented__
        """

        def program(self):
            def play_move(board, player):
                row = board[1]
                row[0] = player

            def play_game():
                board = [
                    [" ", " ", " "],
                    [" ", " ", " "],
                    [" ", " ", " "],
                ]
                play_move(board, "X")
                print(board)

            play_game()

    class nested_assignment_input(ExerciseStep):
        r"""
These two lines:

    row = board[1]
    row[0] = player

can be combined into one:

    board[1][0] = player

The two pieces of code are pretty much exactly equivalent. Python first evaluates
`board[1]` to *get* the inner list, while the `[0] = ...` sets an element of `board[1]`.
You can see the value of `board[1]` in `birdseye` because it's an expression,
and you could actually replace it with any other expression.

Now you know how to set elements in nested lists, it's time to make this interactive!
Write your own version of `play_move` that takes input from the user
to determine where to play, instead of always playing at `board[1][0]`.
It should call `input()` twice, so the user can give the row and the column
as two separate numbers. Also, our users are not programmers, so they start counting from 1,
not 0.

For example, if the user types in these inputs:

    2
    1

that means they want to play a move in the second row and first column, which is the same
as our original example.

Here is some starting code:

    __copyable__
    def format_board(board):
        first_row = ' '
        for i in range(len(board)):
            first_row += str(i + 1)
        joined_rows = [first_row]
        for i in range(len(board)):
            joined_row = str(i + 1) + ''.join(board[i])
            joined_rows.append(joined_row)
        return "\n".join(joined_rows)

    def play_game():
        board = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
        ]
        print(format_board(board))
        print('\nX to play:\n')
        play_move(board, 'X')
        print(format_board(board))
        print('\nO to play:\n')
        play_move(board, 'O')
        print(format_board(board))

    def play_move(board, player):
        ...

    play_game()

This calls `play_move` twice so the user will need to enter two pairs of numbers.
Here's an example of what a 'game' should look like:

     123
    1
    2
    3

    X to play:

    2
    1
     123
    1
    2X
    3

    O to play:

    1
    3
     123
    1  O
    2X
    3

You don't need to use the provided code exactly, it's just to give you a feeling of what's happening.
The important thing is that your `play_move` function modifies the `board` argument correctly.
It doesn't need to return or print anything, that will not be checked.

You can assume that the user will always enter valid numbers. Later we will learn how to deal
with invalid inputs, like numbers out of range or inputs that aren't numbers at all.
        """

        hints = """
Your function needs to call `input()` twice. Input isn't passed to `play_move` as an argument.
`input()` always returns a string.
A string that looks like a number is still a string, not a number.
List indices have to be numbers, not strings.
If the board is 3x3, the user might input 1, 2, or 3 for each coordinate.
What are the valid indices of a list of length 3?
You need to take the input of 1, 2, or 3 and turn it into 0, 1, or 2.
You also need to be able to handle bigger boards, like 9x9 or beyond.
You can't do maths with strings, only numbers.
How can you convert a string to a number?
Once you've got two numbers, you need to modify the nested list `board` with them.
The code for this has been shown to you above.
You just need to use the numbers from user input instead of the hardcoded 1 and 0.
You can use nested subscripting in one line, or do it in two steps.
        """

        requirements = "Your function should modify the `board` argument. It doesn't need to `return` or `print` anything."
        no_returns_stdout = True

        def solution(self):
            def play_move(board, player):
                row = int(input()) - 1
                col = int(input()) - 1
                board[row][col] = player

            return play_move

        @classmethod
        def wrap_solution(cls, func):
            @returns_stdout
            @wrap_solution(func)
            def wrapper(**kwargs):
                board_name = t.get_code_bit("board")
                board = kwargs[board_name] = deepcopy(kwargs[board_name])

                def format_board():
                    first_row = ' '
                    for i in range(len(board)):
                        first_row += str(i + 1)
                    joined_rows = [first_row]
                    for i in range(len(board)):
                        joined_row = str(i + 1) + ''.join(board[i])
                        joined_rows.append(joined_row)
                    return "\n".join(joined_rows)

                func(**kwargs)
                print(format_board())
            return wrapper

        @classmethod
        def generate_inputs(cls):
            return {
                "stdin_input": [str(randint(1, 3)), str(randint(1, 3))],
                "player": choice(ascii_uppercase),
                "board": generate_board(choice(["row", "col", "diag"])),
            }

        tests = [
            (
                {
                    "stdin_input": ["2", "1"],
                    "board": [
                        [" ", " ", " "],
                        [" ", " ", " "],
                        [" ", " ", " "],
                    ],
                    "player": "X",
                },
                dedent("""\
                <input: 2>
                <input: 1>
                 123
                1
                2X
                3
                """),
            ),
            (
                {
                    "stdin_input": ["1", "3"],
                    "board": [
                        [" ", " ", " "],
                        ["X", " ", " "],
                        [" ", " ", " "],
                    ],
                    "player": "O",
                },
                dedent("""\
                <input: 1>
                <input: 3>
                 123
                1  O
                2X
                3
                """),
            ),
        ]

    final_text = """
Brilliant! You're almost ready to put it all together, keep going!
"""


class MakingTheBoard(Page):
    title = "Making the Board"

    class naive_make_board(VerbatimStep):
        """
So far the board has been provided for you as a nested list.
But for the full program, you need to create it yourself.
Should be easy, right? Here's some code to do that:

    __copyable__
    __program_indented__

It's close, but there's a subtle problem with it.
Make sure you understand the code,
and bonus points if you can spot the bug!
If not, don't feel bad or waste too much time on it.
        """

        def program(self):
            def make_board(size):
                row = []
                for _ in range(size):
                    row.append(' ')
                board = []
                for _ in range(size):
                    board.append(row)
                return board

            def test():
                board = make_board(3)
                assert_equal(board, [
                    [' ', ' ', ' '],
                    [' ', ' ', ' '],
                    [' ', ' ', ' '],
                ])
                board[0][0] = 'X'
                assert_equal(board, [
                    ['X', ' ', ' '],
                    [' ', ' ', ' '],
                    [' ', ' ', ' '],
                ])

            test()

    class fix_make_board(ExerciseStep):
        """
Can you see what happened?

Every row got an `'X'` in the first position!
It's as if the code actually did this:

    board[0][0] = 'X'
    board[1][0] = 'X'
    board[2][0] = 'X'

Try and figure out what's wrong by yourself.
But again, it's tricky, so don't drive yourself crazy over it.

If you want, here's some hints:

 - Try running the code through some debuggers.
 - Experiment. Make changes to the code and see what happens.
 - No, the code didn't do 3 assignments like I suggested above. There was just one list assignment.
 - There's no hidden loops or anything.
 - How many lists does `board` contain? 3?
 - The previous page has a subtle hint at what happened.
 - There is a page from a previous chapter where this kind of problem is explained directly.
 - Specifically [this page](#EqualsVsIs).
 - Try running the code with Python Tutor.

OK, if you're ready, here's the answer.

The list `row` was only created once, and reused several times.
`board` contains the same list three times. Not copies, just one list in three places.
It's like it did this:

    board = [row, row, row]

Which means that this code:

    board[0][0] = 'X'

is equivalent to:

    row[0] = 'X'

which affects 'all the lists' in `board` because they're all just the one list `row`.
In other words, the above line is *also* equivalent to each of these two lines:

    board[1][0] = 'X'
    board[2][0] = 'X'

because `row` is `board[0]`, `board[1]`, and `board[2]` all at once.

Your job now is to fix `make_board` to not have this problem.
It should still return a list of length `size` where each
element is also list of length `size` where each element is the string `' '`.
The sublists should all be separate list objects, not the same
list repeated.
        """

        parsons_solution = True
        requirements = "hints"

        hints = """
The existing code is almost correct.
There are several ways to solve this.
Some solutions involve adding something small.
You can also rearrange the code without adding or removing anything (except spaces).
The problem is that a single list `row` is used several times.
So one solution is to make copies of `row` which will all be separate.
Another solution is to make a new `row` from scratch each time.
There are a few ways to copy a list in Python with a tiny bit of code.
Making a new row each time can be done by just rearranging the code.
"""

        def solution(self):
            def make_board(size):
                board = []
                for _ in range(size):
                    row = []
                    for _ in range(size):
                        row.append(' ')
                    board.append(row)
                return board

            return make_board

        tests = {
            2: [
                [' ', ' '],
                [' ', ' ']
            ],
            3: [
                [' ', ' ', ' '],
                [' ', ' ', ' '],
                [' ', ' ', ' '],
            ],
        }

        @classmethod
        def generate_inputs(cls):
            return dict(size=randint(4, 12))

        class special_messages:
            class not_separate:
                text = "The sublists in the result are not all separate objects."
                program = "pass\ndef make_board(size): return [[' '] * size] * size"

        @classmethod
        def check_result(cls, func, inputs, expected_result):
            result = super().check_result(func, inputs, expected_result)
            if len(result) != len(set(map(id, result))):
                raise ExerciseError(cls.special_messages.not_separate.text)

    final_text = """
Well done!

This could be solved by moving the first loop inside the second to make a new `row` each time:

    def make_board(size):
        board = []
        for _ in range(size):
            row = []
            for _ in range(size):
                row.append(' ')
            board.append(row)
        return board

Another way is to make a copy of `row` each time, e.g. keep the original code but change one line:

    board.append(row.copy())

You can also copy `row` with `row[:]` or `list(row)`. But it's important to know that
all these methods make a *shallow copy* of the list.
That means they copy the whole list at the top level, without making copies of each element.
That's fine in this case where `row` only contains strings which can't be modified
and don't need copying. But if the elements are mutable objects like lists,
as is the case with `board`, you may run into the same problem again.
Here's an example:

    __copyable__
    def make_board(size):
        row = []
        for _ in range(size):
            row.append(' ')
        board = []
        for _ in range(size):
            board.append(row.copy())
        return board

    def make_cube(size):
        cube = []
        board = make_board(size)
        for _ in range(size):
            cube.append(board.copy())
        return cube

    def test():
        cube = make_cube(2)
        print(cube)
        cube[0][0][0] = 'X'
        print(cube)
        print(cube[0] is cube[1])
        print(cube[0][0] is cube[0][1])
        print(cube[0][0] is cube[1][0])

    test()

Here each element of `cube` is a separate list, a copy of `board`.
And within each of those copies, each element is also a separate list, a copy of `row`.
But the shallow copies of `board` all have the same first element as each other (the first copy of `row`),
the same second element, and so on.
Changing `make_board` won't fix anything here, the solution is to either:

- Call `make_board` repeatedly to make a new `board` each time, or
- Use the `deepcopy` function instead of `board.copy()`.
  `deepcopy` makes copies at every level of nested objects.

If you're still confused, don't worry.
This is just preparing you to deal with your code behaving weirdly in the future.
You're not required to understand this right now and this lesson will still be valuable.

Either way, we're ready to make the full game. You can do it!
"""


class TheFullTicTacToeGame(Page):
    title = "The Full Tic-Tac-Toe Game"

    class the_full_game(ExerciseStep):
        r"""
It's time to put it all together! Below is some code to get started.

It includes implementations of the various functions we defined in previous pages for solving parts
of the problem, using some tricks you haven't learned yet to make them shorter. Don't change them.

Your task is to implement `play_game` correctly. The current implementation shows what
should happen at the start of the game, but it's obviously incomplete.
The solution should work for any board size and continue the game until it's finished.
The last thing that `play_game` should do is either call `print_winner(player)`
if `winner(board)` is true, or call `print_draw()` if the board is filled up with no winner.

You can assume that the user will only enter valid inputs,
i.e. numbers from 1 to `board_size` to choose a cell on the board that isn't already taken.

    __copyable__
    def winning_line(strings):
        strings = set(strings)
        return len(strings) == 1 and ' ' not in strings

    def row_winner(board):
        return any(winning_line(row) for row in board)

    def column_winner(board):
        return row_winner(zip(*board))

    def main_diagonal_winner(board):
        return winning_line(row[i] for i, row in enumerate(board))

    def diagonal_winner(board):
        return main_diagonal_winner(board) or main_diagonal_winner(reversed(board))

    def winner(board):
        return row_winner(board) or column_winner(board) or diagonal_winner(board)

    def format_board(board):
        size = len(board)
        line = f'\n  {"+".join("-" * size)}\n'
        rows = [f'{i + 1} {"|".join(row)}' for i, row in enumerate(board)]
        return f'  {" ".join(str(i + 1) for i in range(size))}\n{line.join(rows)}'

    def play_move(board, player):
        print(f'{player} to play:')
        row = int(input()) - 1
        col = int(input()) - 1
        board[row][col] = player
        print(format_board(board))

    def make_board(size):
        return [[' '] * size for _ in range(size)]

    def print_winner(player):
        print(f'{player} wins!')

    def print_draw():
        print("It's a draw!")

    def play_game(board_size, player1, player2):
        board = make_board(board_size)
        print(format_board(board))

        play_move(board, player1)
        play_move(board, player2)
        play_move(board, player1)
        play_move(board, player2)

    play_game(3, 'X', 'O')
        """

        parsons_solution = True
        requirements = "hints"

        hints = """
You should use all of the functions `winner`, `format_board` (not counting its use in `play_move`), `play_move`, `make_board`, `print_winner`, and `print_draw` somewhere.
You only need to mention each of those functions once in your code, although some of them will be called several times as the program runs.
You will need a for loop to repeatedly play moves.
You don't need to check if the board has been filled up, because you can always calculate how many moves it takes to fill up the board.
So you can just use a loop that will run a fixed number of iterations, and inside the loop check if the loop needs to be ended early.
What's the maximum number of moves that can be played in a 3x3 board? 4x4?
A loop over a `range` is an easy way to iterate a fixed number of times.
So you can use `for _ in range(N):` to play at most `N` moves.
Once there's a winner, you need to end the loop and the game.
Either `print_winner` or `print_draw` should be called, not both.
Whichever function is called, it must be called exactly once.
One easy way to make sure you don't call a function multiple times is to call it outside of any loop.
We've learned about two ways to make a loop stop.
One way is `break`, which specifically ends one loop and no more.
The second way ends not just the loop but the whole function call.
The second way is `return`.
Don't play moves in pairs like `play_move(board, player1)` and `play_move(board, player2)` in the sample code.
Instead, each loop iteration should play one move.
You need a variable to keep track of which player's turn it is.
The player should be switched in each loop iteration.
An `if` statement is a good way to do this.
Especially combined with an `else`.
Make sure `player1` plays the first move.
Only call `print_winner` after checking `winner` with an `if` statement.
You need to check for the winner inside the loop since you don't know when a player might win.
Once you call `print_winner`, you can use `return` to end the function.
Just `return` by itself is fine, `play_game` isn't meant to return a value.
Don't use `else` after checking for a winner to call `print_draw` if there isn't a winner. Just because no one has won yet doesn't mean it's a draw already.
`print_draw` should only be called after all moves have been played and there's still no winner.
So it should be called after the loop, outside of it.
Check the indentation to make sure `print_draw` isn't in the body of the for loop.
"""

        def solution(self):
            def winning_line(strings):
                strings = set(strings)
                return len(strings) == 1 and ' ' not in strings

            def row_winner(board):
                return any(winning_line(row) for row in board)

            def column_winner(board):
                return row_winner(zip(*board))

            def main_diagonal_winner(board):
                return winning_line(row[i] for i, row in enumerate(board))

            def diagonal_winner(board):
                return main_diagonal_winner(board) or main_diagonal_winner(reversed(board))

            def winner(board):
                return row_winner(board) or column_winner(board) or diagonal_winner(board)

            def format_board(board):
                size = len(board)
                line = f'\n  {"+".join("-" * size)}\n'
                rows = [f'{i + 1} {"|".join(row)}' for i, row in enumerate(board)]
                return f'  {" ".join(str(i + 1) for i in range(size))}\n{line.join(rows)}'

            def play_move(board, player):
                print(f'{player} to play:')
                row = int(input()) - 1
                col = int(input()) - 1
                board[row][col] = player
                print(format_board(board))

            def make_board(size):
                return [[' '] * size for _ in range(size)]

            def print_winner(player):
                print(f'{player} wins!')

            def print_draw():
                print("It's a draw!")

            def play_game(board_size, player1, player2):
                board = make_board(board_size)
                print(format_board(board))

                player = player1
                for _ in range(board_size * board_size):
                    play_move(board, player)

                    if winner(board):
                        print_winner(player)
                        return

                    if player == player1:
                        player = player2
                    else:
                        player = player1

                print_draw()

            return play_game

        @classmethod
        def wrap_solution(cls, func):
            return returns_stdout(func)

        translated_tests = True

        tests = [
            (dict(board_size=2, player1="A", player2="B", stdin_input=["1", "1", "1", "2", "2", "1"]),
             """\
  1 2
1  |
  -+-
2  |
A to play:
<input: 1>
<input: 1>
  1 2
1 A|
  -+-
2  |
B to play:
<input: 1>
<input: 2>
  1 2
1 A|B
  -+-
2  |
A to play:
<input: 2>
<input: 1>
  1 2
1 A|B
  -+-
2 A|
A wins!
"""),
            (dict(board_size=3, player1="X", player2="O",
                  stdin_input=["1", "1",
                               "2", "2",
                               "3", "3",
                               "1", "3",
                               "3", "1",
                               "2", "1",
                               "3", "2"]),
             """\
  1 2 3
1  | |
  -+-+-
2  | |
  -+-+-
3  | |
X to play:
<input: 1>
<input: 1>
  1 2 3
1 X| |
  -+-+-
2  | |
  -+-+-
3  | |
O to play:
<input: 2>
<input: 2>
  1 2 3
1 X| |
  -+-+-
2  |O|
  -+-+-
3  | |
X to play:
<input: 3>
<input: 3>
  1 2 3
1 X| |
  -+-+-
2  |O|
  -+-+-
3  | |X
O to play:
<input: 1>
<input: 3>
  1 2 3
1 X| |O
  -+-+-
2  |O|
  -+-+-
3  | |X
X to play:
<input: 3>
<input: 1>
  1 2 3
1 X| |O
  -+-+-
2  |O|
  -+-+-
3 X| |X
O to play:
<input: 2>
<input: 1>
  1 2 3
1 X| |O
  -+-+-
2 O|O|
  -+-+-
3 X| |X
X to play:
<input: 3>
<input: 2>
  1 2 3
1 X| |O
  -+-+-
2 O|O|
  -+-+-
3 X|X|X
X wins!
"""),
            (dict(board_size=3, player1="X", player2="O",
                  stdin_input=["1", "2",
                               "1", "1",
                               "2", "2",
                               "2", "1",
                               "1", "3",
                               "3", "1"]),
             """\
  1 2 3
1  | |
  -+-+-
2  | |
  -+-+-
3  | |
X to play:
<input: 1>
<input: 2>
  1 2 3
1  |X|
  -+-+-
2  | |
  -+-+-
3  | |
O to play:
<input: 1>
<input: 1>
  1 2 3
1 O|X|
  -+-+-
2  | |
  -+-+-
3  | |
X to play:
<input: 2>
<input: 2>
  1 2 3
1 O|X|
  -+-+-
2  |X|
  -+-+-
3  | |
O to play:
<input: 2>
<input: 1>
  1 2 3
1 O|X|
  -+-+-
2 O|X|
  -+-+-
3  | |
X to play:
<input: 1>
<input: 3>
  1 2 3
1 O|X|X
  -+-+-
2 O|X|
  -+-+-
3  | |
O to play:
<input: 3>
<input: 1>
  1 2 3
1 O|X|X
  -+-+-
2 O|X|
  -+-+-
3 O| |
O wins!
"""),
            (dict(board_size=3, player1="X", player2="O",
                  stdin_input=["1", "1",
                               "1", "2",
                               "1", "3",
                               "2", "1",
                               "2", "3",
                               "3", "3",
                               "3", "1",
                               "2", "2",
                               "3", "2"]),
             """\
  1 2 3
1  | |
  -+-+-
2  | |
  -+-+-
3  | |
X to play:
<input: 1>
<input: 1>
  1 2 3
1 X| |
  -+-+-
2  | |
  -+-+-
3  | |
O to play:
<input: 1>
<input: 2>
  1 2 3
1 X|O|
  -+-+-
2  | |
  -+-+-
3  | |
X to play:
<input: 1>
<input: 3>
  1 2 3
1 X|O|X
  -+-+-
2  | |
  -+-+-
3  | |
O to play:
<input: 2>
<input: 1>
  1 2 3
1 X|O|X
  -+-+-
2 O| |
  -+-+-
3  | |
X to play:
<input: 2>
<input: 3>
  1 2 3
1 X|O|X
  -+-+-
2 O| |X
  -+-+-
3  | |
O to play:
<input: 3>
<input: 3>
  1 2 3
1 X|O|X
  -+-+-
2 O| |X
  -+-+-
3  | |O
X to play:
<input: 3>
<input: 1>
  1 2 3
1 X|O|X
  -+-+-
2 O| |X
  -+-+-
3 X| |O
O to play:
<input: 2>
<input: 2>
  1 2 3
1 X|O|X
  -+-+-
2 O|O|X
  -+-+-
3 X| |O
X to play:
<input: 3>
<input: 2>
  1 2 3
1 X|O|X
  -+-+-
2 O|O|X
  -+-+-
3 X|X|O
It's a draw!
"""),
        ]

        @classmethod
        def generate_inputs(cls):
            size = randint(4, 6)
            points = itertools.product(range(1, size + 1), repeat=2)
            return dict(
                board_size=size,
                player1=choice(ascii_uppercase),
                player2=choice(ascii_uppercase),
                stdin_input=list(map(str, itertools.chain.from_iterable(shuffled(points)))),
            )

    final_text = """
### ***CONGRATULATIONS!!!***

You did it!
"""
