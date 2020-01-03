import ast

from main.text import Page, step, search_ast


class IntroducingStrings(Page):
    @step("""
Python lets you do much more than calculate. In fact, we're not going to touch numbers or maths for a while. Instead, we're going to look at *strings*. Strings are essentially snippets of text. For example, enter the following into the shell, quotes (`'`) included:

__program_indented__
    """, program="'hello'")
    def hello_string(self):
        return self.matches_program()

    final_text = """
The shell simply gives the same thing back because there's nothing to further to calculate. `'hello'` is simply equal to `'hello'`.

A string is a sequence of characters. A character is a single symbol such as a letter, number, punctuation, space, etc. In this case the string contains the 5 characters `hello`. The quotes are not part of the string - they are there to tell both humans and computers that this is a string consisting of whatever characters are between the quotes.
"""


class AddingStrings(Page):
    @step("""
Strings can be added together using `+`, although this means something very different from adding numbers. For example, try:

__program_indented__
    """, program="'hello' + 'world'")
    def hello_world_concat(self):
        return self.matches_program()

    @step("""
You can see that `+` combines or joins two strings together end to end. Technically, this is called concatenation.

Here's an exercise: change the previous code slightly so that the result is the string `'hello world'`, i.e. with a space between the words.

By the way, if you get stuck, you can click the lightbulb icon in the bottom right for a hint.
          """,
          hints=[
              "A space is a character just like any other, like `o` or `w`.",
              "The space character must be somewhere inside quotes.",
          ])
    def hello_world_space(self):
        if "'hello world'" not in self.result:
            return False

        if search_ast(
                self.expr,
                ast.BinOp(left=ast.Str(), op=ast.Add(), right=ast.Str()),
        ):
            return True

        return dict(message="You must still add two or more strings together.")

    final_text = """
Well done! Any of the following are valid solutions:

    'hello ' + 'world'
    'hello' + ' world'
    'hello' + ' ' + 'world'
"""
