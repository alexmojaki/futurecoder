# flake8: NOQA E501
import ast
import re

from astcheck import is_ast_like

from main.text import MessageStep, Page, Step, VerbatimStep


class word_must_be_hello(VerbatimStep):
    def check(self):
        if self.console.locals.get("word") != "Hello":
            return dict(
                message="Oops, you need to set `word = 'Hello'` before we can continue."
            )
        return super().check()


class IntroducingVariables(Page):

    class word_assign(VerbatimStep):
        """
To make interesting programs, we can't always manipulate the same values. We need a way to refer to values that are unknown ahead of time and can change - values that can vary. These are called *variables*.

Run this code:

__program_indented__
        """

        program = "word = 'Hello'"

    class word_check(word_must_be_hello):
        """
This creates a variable with the name `word` that refers to the string value `'Hello'`.

Now see what happens when you run `__program__` in the shell by itself.
        """

        program = "word"
        predicted_output_choices = ["word", "'word'", "Hello", "'Hello'"]

    class word_string_check(VerbatimStep):
        """
Good. For comparison, run `__program__` in the shell by itself, with the quotes.
        """

        program = "'word'"
        predicted_output_choices = ["word", "'word'", "Hello", "'Hello'"]

    class sunshine_undefined_check(VerbatimStep):
        """
As you can see, the quotes make all the difference. `'word'` is literally just `'word'`, hence it's technically called a *string literal*. On the other hand, `word` is a variable, whose value may be anything.

Similarly, `'sunshine'` is `'sunshine'`, but what's `__program__` without quotes?
        """

        program = "sunshine"
        predicted_output_choices = ["sunshine", "'sunshine'", "Hello", "'Hello'"]
        correct_output = "Error"

    final_text = """
The answer is that `sunshine` looks like a variable, so Python tries to look up its value, but since we never defined a variable with that name we get an error.
"""


class UsingVariables(Page):
    title = "Using Variables and `print()`"

    class name_assign(Step):
        """
Previously we made a variable called `word` with the value `'Hello'` with this code:

    word = 'Hello'

Now make a variable called `your_name` whose value is another string.

(The character `_` in `your_name` is called an *underscore*. Use it to separate words when you want a variable name containing multiple words. You can type it on most keyboards by pressing Shift and hyphen/dash/minus (`-`).)
        """

        program = "your_name = 'Alex'"

        class assigned_something_else(MessageStep):
            """Put `your_name` before the `=` to create a variable called `your_name`."""
            program = "foo = 3"

            def check(self):
                match = re.match(r"(.*)=", self.input)
                return bool(match and match.group(1).strip() != "your_name")

        class name_equals_something_else(MessageStep):
            """You've got the `your_name = ` part right, now put a string (use quotes) on the right of the `=`."""
            program = "your_name = 3"

            def check(self):
                return self.input_matches("your_name=[^'\"].*")

        class empty_string(MessageStep):
            """For this exercise, choose a non-empty string"""
            program = "your_name = ''"
            after_success = True

            def check(self):
                return not self.console.locals['your_name']

        class starts_with_space(MessageStep):
            """For this exercise, choose a name that doesn't start with a space."""
            program = "your_name = ' Alex'"
            after_success = True

            def check(self):
                return self.console.locals['your_name'].startswith(' ')

        def check(self):
            return (
                    is_ast_like(
                        self.tree,
                        ast.Module(body=[ast.Assign(targets=[ast.Name(id='your_name')])])
                    )
                    and isinstance(self.console.locals.get('your_name'), str)
            )

    class hello_plus_name(VerbatimStep):
        """
You can use variables in calculations just like you would use literals. For example, try:

__program_indented__
        """

        program = "'Hello ' + your_name"

    class word_plus_name(word_must_be_hello):
        """
Or you can just add variables together. Try:

    __program_indented__
        """

        program = "word + your_name"

    class word_plus_name_with_space(word_must_be_hello):
        """
Oops...that doesn't look nice. Can you modify the code above so that there's a space between the word and your name?
        """

        hints = """
You will need to use `+` twice, like 1+2+3.
Your answer should contain a mixture of variables (no quotes) and string literals (quotes).
You will need to have a space character inside quotes.
        """

        program = "word + ' ' + your_name"
        program_in_text = False

    class word_assign_goodbye(VerbatimStep):
        """
Perfect!

Variables can also change their values over time. Right now `word` has the value `'Hello'`. You can change its value in the same way that you set it for the first time. Run this:

    __program_indented__
        """

        program = "word = 'Goodbye'"

    class goodbye_plus_name(VerbatimStep):
        """
Now observe the effect of this change by running `__program__` again.
        """

        program = "word + ' ' + your_name"

    class first_print(VerbatimStep):
        """
Those quotes around strings are getting annoying. Try running this:

    __program_indented__
        """

        program = "print(word + ' ' + your_name)"

    final_text = """
Hooray! No more quotes! We'll break down what's happening in this code later. For now just know that `print(<something>)` displays `<something>` in the shell. In particular it displays the actual content of strings that we usually care about, instead of a representation of strings that's suitable for code which has things like quotes. The word `print` here has nothing to do with putting ink on paper.
"""


class WritingPrograms(Page):

    class editor_hello_world(VerbatimStep):
        """
It's time to stop doing everything in the shell. In the top right you can see the *editor*. This is a place where you can write and run longer programs. The shell is great and you should keep using it to explore, but the editor is where real programs live.

Type the program below into the editor, then click the 'Run' button:

    __program_indented__
        """

        def program(self):
            word = 'Hello'
            name = 'World'
            print(word + ' ' + name)
            word = 'Goodbye'
            print(word + ' ' + name)

    final_text = """
Congratulations, you have run your first actual program!

Take some time to understand this program. Python runs each line one at a time from top to bottom. You should try simulating this process in your head - think about what each line does. See how the value of `word` was changed and what effect this had. Note that when `print` is used multiple times, each thing (`Hello World` and `Goodbye World` in this case) is printed on its own line.

Some things to note about programs in the editor:

1. The program runs in the shell, meaning that the variables defined in the program now exist in the shell with the last values they had in the program. This lets you explore in the shell after the program completes. For example, `name` now has the value `'World'` in the shell.
2. Programs run in isolation - they don't depend on any previously defined variables. The shell is reset and all previous variables are cleared. So even though `word` currently exists in the shell, if you delete the first line of the program and run it again, you'll get an error about `word` being undefined.
3. If you enter code in the shell and it has a value, that value will automatically be displayed. That doesn't happen for programs in the editor - you have to print values. If you remove `print()` from the program, changing the two lines to just `word + ' ' + name`, nothing will be displayed.

I recommend that you check all of these things for yourself.
"""


class StoringCalculationsInVariables(Page):

    class sentence_equals_word_plus_name(VerbatimStep):
        """
Often you will use variables to store the results of calculations. This will help to build more complex programs. For example, try this program:

    __program_indented__
        """

        def program(self):
            word = 'Hello'
            name = 'World'
            sentence = word + ' ' + name
            print(sentence)

    class sentence_doesnt_change(VerbatimStep):
        """
Now `sentence` has the value `'Hello World'` which can be used multiple times. Note that it will continue to have this value until it is directly reassigned, e.g. with another statement like `sentence = <something>`. For example, add these two lines to the end of the program:

    word = 'Goodbye'
    print(sentence)
        """
        program_in_text = False

        # noinspection PyUnusedLocal
        def program(self):
            word = 'Hello'
            name = 'World'
            sentence = word + ' ' + name
            print(sentence)
            word = 'Goodbye'
            print(sentence)

    final_text = """
Unlike a spreadsheet where formulas update automatically, a variable like `sentence` doesn't remember how it was calculated and won't change if the underlying values `word` or `name` are changed.
"""
