from textwrap import dedent

from main.text import Page, step


class IntroducingTheShell(Page):
    @step("""
At the bottom right of the screen is the *shell*. This is a place for running small bits of Python code. Just type in some code, press enter, and it'll run! Try it now:

1. Click anywhere on the shell (the black area).
2. Type `__program__`
3. Press the Enter key on your keyboard.
    """, program='1+2')
    def first_expression(self):
        if self.matches_program():
            return True

        return dict(
            message=dedent("""
                Awesome, you're trying out your own experiments!
                That's a great sign. Keep it up.
                Just letting you know that you do need to eventually type `1+2`
                for the book to move forward.
                """)
        )

    @step("""
Great! Python evaluated `1+2` and got the result `3`, so the shell displays that.

The shell is probably your most important tool for learning Python, and you should spend lots of time experimenting and exploring in it. Be curious! Constantly ask yourself "What would happen if I ran X?" and then immediately answer that question by running it! Never be scared to try something out - if you get something wrong, nothing bad will happen.

Try doing some more calculations now. You can multiply numbers with `*`, divide with `/`, and subtract with `-`. You can also use parentheses, i.e. `(` and `)`.
    """)
    def more_calculation(self):
        if 'x' in self.input:
            return dict(
                message=dedent("""
                    I see an 'x'.
                    If you're trying to multiply, use an asterisk, e.g:

                        3 * 4
                    """)
            )
        return self.input_matches(r'\d[-*/]\d')

    final_text = """
Excellent! Keep experimenting. When you're ready, click 'Next' to continue.
"""


class NavigatingShellHistory(Page):
    final_text = """
Here's a tip: often you will want to re-run a previously entered bit of code, or a slightly modified version of it. You can copy and paste, but that's tedious and gets in the way of experimenting. A better method is to press the Up Arrow key on your keyboard. This will insert the previous line of code into the shell. Keep pressing it to go further back in your history, and if you go too far, press the Down Arrow key to go the other way. Try using it now.
    """
