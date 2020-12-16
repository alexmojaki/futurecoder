# flake8: NOQA E501
import ast
from string import ascii_uppercase
from typing import List
from random import choice, randint

from main.text import ExerciseStep, Page, MessageStep, Disallowed


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
            winning = choice([True, False])
            size = randint(3, 10)
            char1 = choice(ascii_uppercase)
            char2 = choice(ascii_uppercase)
            chars = [char1, char2, ' ']
            board = [[choice(chars) for _ in range(size)] for _ in range(size)]

            if winning:
                row = randint(0, size - 1)
                winning_piece = choice([char1, char2])
                board[row] = [winning_piece for _ in range(size)]

            return {
                "board": board
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
            winning = choice([True, False])
            size = randint(3, 10)
            char1 = choice(ascii_uppercase)
            char2 = choice(ascii_uppercase)
            chars = [char1, char2, ' ']
            board = [[choice(chars) for _ in range(size)] for _ in range(size)]

            if winning:
                column = randint(0, size - 1)
                winning_piece = choice([char1, char2])
                for i in range(size):
                    board[i][column] = winning_piece

            return {
                "board": board
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
            winning = choice([True, False])
            size = randint(3, 10)
            char1 = choice(ascii_uppercase)
            char2 = choice(ascii_uppercase)
            chars = [char1, char2, ' ']
            board = [[choice(chars) for _ in range(size)] for _ in range(size)]

            if winning:
                diag = choice([True, False])
                winning_piece = choice([char1, char2])
                for i in range(size):
                    if diag:
                        board[i][i] = winning_piece
                    else:
                        board[i][-i-1] = winning_piece

            return {
                "board": board
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

    def row_winner(board):
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

    def column_winner(board):
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

    def diagonal_winner(board):
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
            def row_winner(board):
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

            def column_winner(board):
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

            def diagonal_winner(board):
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

            def winner(board: List[List[str]]):
                return row_winner(board) or column_winner(board) or diagonal_winner(board)

            return winner

        @classmethod
        def generate_inputs(cls):
            winning = choice([True, False])
            size = randint(3, 10)
            char1 = choice(ascii_uppercase)
            char2 = choice(ascii_uppercase)
            chars = [char1, char2, ' ']
            board = [[choice(chars) for _ in range(size)] for _ in range(size)]

            if winning:
                winning_piece = choice([char1, char2])
                winner = choice(['row', 'col', 'diag'])
                random = randint(0, size - 1)
                if winner == 'row':
                    board[random] = [winning_piece for _ in range(size)]
                if winner == 'col':
                    for i in range(size):
                        board[i][random] = winning_piece
                if winner == 'diag':
                    diag = choice([True, False])
                    for i in range(size):
                        if diag:
                            board[i][i] = winning_piece
                        else:
                            board[i][-i-1] = winning_piece

            return {
                "board": board
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
