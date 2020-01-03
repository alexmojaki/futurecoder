import ast
import re

from astcheck import is_ast_like

from main.text import Page, step


class IntroducingVariables(Page):
    @step("""
To make interesting programs, we can't always manipulate the same values. We need a way to refer to values that are unknown ahead of time and can change - values that can vary. These are called *variables*.

Run this code:

__program_indented__
    """, program="word = 'Hello'")
    def word_assign(self):
        return self.matches_program()

    @step("""
This creates a variable with the name `word` that refers to the string value `'Hello'`.

Check now that this is true by simply running `__program__` in the shell by itself.
    """, program='word')
    def word_check(self):
        return self.matches_program()

    @step("""
Good. For comparison, run `__program__` in the shell by itself, with the quotes.
    """, program="'word'")
    def word_string_check(self):
        return self.matches_program()

    @step("""
As you can see, the quotes make all the difference. `'word'` is literally just `'word'`, hence it's technically called a *string literal*. On the other hand, `word` is a variable, whose value may be anything.

Similarly, `'sunshine'` is `'sunshine'`, but what's `__program__` without quotes?
    """, program='sunshine')
    def sunshine_undefined_check(self):
        return self.matches_program()

    final_text = """
The answer is that `sunshine` looks like a variable, so Python tries to look up its value, but since we never defined a variable with that name we get an error.
"""


class UsingVariables(Page):
    @step("""
Previously we made a variable called `word` with the value `'Hello'` with this code:

    word = 'Hello'

Now make a variable called `name` whose value is another string. The string can be anything...how about your name?
    """)
    def name_assign(self):
        match = re.match(r"(.*)=", self.input)
        if match and match.group(1).strip() != "name":
            return dict(message="Put `name` before the `=` to create a variable called `name`.")

        if self.input_matches("name=[^'\"].*"):
            return dict(message="You've got the `name = ` part right, now put a string on "
                                "the right of the `=`.")

        if not is_ast_like(
                self.tree,
                ast.Module(body=[ast.Assign(targets=[ast.Name(id='name')],
                                            value=ast.Constant())])
        ):
            return False
        name = self.console.locals.get('name')
        if isinstance(name, str):
            if not name:
                return dict(message="Choose a non-empty string")
            if name[0] == " ":
                return dict(message="For this exercise, choose a name "
                                    "that doesn't start with a space.")

            return True

    @step("""
You can use variables in calculations just like you would use literals. For example, try:

__program_indented__
    """, program="'Hello ' + name")
    def hello_plus_name(self):
        return self.matches_program()

    @step("""
Or you can just add variables together. Try:

    __program_indented__
    """, program="word + name")
    def word_plus_name(self):
        return self.matches_program()

    @step("""
Oops...that doesn't look nice. Can you modify the code above so that there's a space between the word and the name?
          """,
          hints="""
You will need to use `+` twice, like 1+2+3.
Your answer should contain a mixture of variables (no quotes) and string literals (quotes).
You will need to have a space character inside quotes.""")
    def word_plus_name_with_space(self):
        return self.tree_matches("word + ' ' + name")

    @step("""
Perfect!

Variables can also change their values over time. Right now `word` has the value `'Hello'`. You can change its value in the same way that you set it for the first time. Run this:

    __program_indented__
    """, program="word = 'Goodbye'")
    def word_assign_goodbye(self):
        return self.matches_program()

    @step("""
Now observe the effect of this change by running `word + ' ' + name` again.
    """)
    def goodbye_plus_name(self):
        return self.word_plus_name_with_space()

    @step("""
Those quotes around strings are getting annoying. Try running this:

    __program_indented__
    """, program="print(word + ' ' + name)")
    def first_print(self):
        return self.matches_program()

    final_text = """
Hooray! No more quotes! We'll break down what's happening in this code later. For now just know that `print(<something>)` displays `<something>` in the shell. In particular it displays the actual content of strings that we usually care about, instead of a representation of strings that's suitable for code which has things like quotes. The word `print` here has nothing to do with putting ink on paper.
"""


class WritingPrograms(Page):
    @step("""
It's time to stop doing everything in the shell. In the top right you can see the *editor*. This is a place where you can write and run longer programs. The shell is great and you should keep using it to explore, but the editor is where real programs live.

Copy the program below into the editor, then click the 'Run' button:

    __program_indented__
    """, program="""
word = 'Hello'
name = 'World'
print(word + ' ' + name)
word = 'Goodbye'
print(word + ' ' + name)
    """)
    def editor_hello_world(self):
        return self.matches_program()

    final_text = """
Congratulations, you have run your first actual program!

Take some time to understand this program. Python runs each line one at a time from top to bottom. You should try simulating this process in your head - think about what each line does. See how the value of `word` was changed and what effect this had. Note that when `print` is used multiple times, each thing (`Hello World` and `Goodbye World` in this case) is printed on its own line.

Some things to note about programs in the editor:

1. The program runs in the shell, meaning that the variables defined in the program now exist in the shell with the last values they had in the program. This lets you explore in the shell after the program completes. For example, `name` now has the value `'World'` in the shell.
2. Programs run in isolation - they don't depend on any previously defined variables. The shell is reset and all previous variables are cleared. So even though `word` currently exists in the shell, if you delete the first line of the program and run it again, you'll get an error about `word` being undefined.
3. If you enter code in the shell and it has a value, that value will automatically be displayed. That doesn't happen for programs in the editor - you have to print values. If you remove `print()` from the program, changing the two lines to just `word + ' ' + name`, nothing will be displayed.

I recommend that you check all of these things for yourself.
"""
