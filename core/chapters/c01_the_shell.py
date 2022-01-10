# flake8: NOQA E501
import ast
from textwrap import dedent

from core.text import MessageStep, Page, Step, VerbatimStep, search_ast


class IntroducingTheShell(Page):
    class first_expression(VerbatimStep):
        """
On the right is the *shell*. This is a place for running small bits of Python code. Just type in some code, press enter, and it'll run! Try it now:

1. Click anywhere on the shell (the black area).
2. Type `__program__`
3. Press the Enter key on your keyboard.
        """

        program = "1+2"

        class anything_else(MessageStep):
            """
            Awesome, you're trying out your own experiments!
            That's a great sign. Keep it up.
            Just letting you know that you do need to eventually type `1+2` for the book to move forward.
            """

            program = "'literally anything'"

            def check(self):
                return True

    class more_calculation(Step):
        """
Great! Python evaluated `1+2` and got the result `3`, so the shell displays that.

The shell is probably your most important tool for learning Python, and you should spend lots of time experimenting and exploring in it. Be curious! Constantly ask yourself "What would happen if I ran X?" and then immediately answer that question by running it! Never be scared to try something out - if you get something wrong, nothing bad will happen.

Try doing some more calculations now. You can multiply numbers with `*`, divide with `/`, and subtract with `-`. You can also use parentheses, i.e. `(` and `)`.
        """

        program = "5 - 6"

        class special_messages:
            class multiply_with_x:
                """
                I see an 'x'. If you're trying to multiply, use an asterisk, e.g:

                    3 * 4
                """

                program = "3 x 4"

        def check(self):
            try:
                return search_ast(self.tree, (ast.Mult, ast.Div, ast.Sub))
            except SyntaxError:
                if "x" in self.input:
                    return self.special_messages.multiply_with_x

    final_text = """
Excellent! Keep experimenting. When you're ready, click 'Next' to continue.
"""


class NavigatingShellHistory(Page):
    final_text = """
Here's a tip: often you will want to re-run a previously entered bit of code, or a slightly modified version of it. You can copy and paste, but that's tedious and gets in the way of experimenting. A better method is to press the Up Arrow key on your keyboard. This will insert the previous line of code into the shell. Keep pressing it to go further back in your history, and if you go too far, press the Down Arrow key to go the other way. Try using it now.
    """
