# flake8: NOQA E501
import ast
from string import ascii_uppercase
from typing import List
from random import choice, randint

from main.text import ExerciseStep, Page, MessageStep, Disallowed, VerbatimStep


def generate_board(board_type):
    winning = choice([True, False])
    size = randint(3, 10)
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

     123
    1
    2
    3

    X to play
    Enter row: 2
    Enter column: 2
     123
    1
    2 X
    3

    O to play
    Enter row: 1
    Enter column: 3
     123
    1  O
    2 X
    3

We will break up the project into several small functions, which will be exercises.

You will use many of the concepts you have learned so far: strings,
nested lists, nested loops, `range`, calling functions within functions, comparisons, and booleans.

Along the way you will also learn some new concepts: `input`, the newline character, types in Python, and `while` loops.

Here is a rough outline of the project:

- three functions `row_winner`, `column_winner`,  `diagonal_winner`  that check the whole board for winning rows, columns, and diagonals
- a function `winner` that checks the whole board for a winner, combining the above functions
- a function `format_board` that displays the current state of the game
- a function `get_coordinate` that takes user input to play a move,
- finally a `main` function that puts it all together and runs the game interactively.
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
That covers the outer loop, which goes through each column. Then you need an inner loop to go thread each element in the column.
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
            diagonal2.append(board[i][i])
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
                    diagonal2.append(board[i][i])
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
Next we will tackle the problem of displaying the board on the screen.
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
(either `'''` or `\"""`) around the contents of the string:

__program_indented__
        """

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

        def check(self):
            string = self.console.locals.get("string", "")
            if not (isinstance(string, str) and '\n' in string):
                return dict(
                    message="Oops, `string` doesn't have the right value. "
                            "Run the program from the previous step again."
                )
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

If you'd like, you can just continue to the next page now. Or you can do a bonus challenge!

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

        # TODO link to next page

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
