import ast
import re
from textwrap import indent, dedent

from astcheck import is_ast_like
from markdown import markdown

from main.exercises import generate_short_string, check_result, check_exercise
from main.utils import no_weird_whitespace, returns_stdout

text_parts = []
steps = []


def step(text, *, program="", hints=()):
    if isinstance(hints, str):
        hints = hints.strip().splitlines()
    hints = [markdown(text) for text in hints]
    no_weird_whitespace(text)
    no_weird_whitespace(program)
    program = program.strip()
    if "__program_" in text:
        assert program
        text = text.replace("__program__", program)
        indented = indent(program, '    ')
        text = re.sub(r" *__program_indented__", indented, text, flags=re.MULTILINE)
    else:
        assert not program
    assert "__program_" not in text

    text = markdown(text.strip())

    def decorator(f):
        f.hints = hints
        f.text = text
        f.program = program
        text_parts.append(text)
        steps.append(f.__name__)
        return f

    return decorator


class Steps:
    def __init__(self, code_entry, console, program):
        self.input = code_entry.input
        self.result = code_entry.output
        self.code_source = code_entry.source
        self.console = console
        self.program = program

    def check_exercise(self, *args, **kwargs):
        if self.code_source == "editor":
            return check_exercise(self.input, *args, **kwargs)

    @property
    def tree(self):
        return ast.parse(self.input)

    @property
    def stmt(self):
        return self.tree.body[0]

    @property
    def expr(self):
        return self.stmt.value

    def tree_matches(self, template):
        return is_ast_like(self.tree, ast.parse(template))

    def matches_program(self):
        return self.tree_matches(self.program)

    def input_matches(self, pattern, remove_spaces=True):
        inp = self.input.rstrip()
        if remove_spaces:
            inp = re.sub(r'\s', '', inp)
        return re.match(pattern + '$', inp)

    @step("""
# The shell

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

    @step("""
Awesome! Here's a tip: often you will want to re-run a previously entered bit of code, or a slightly modified version of it. You can copy and paste, but that's tedious and gets in the way of experimenting. A better method is to press the Up Arrow key on your keyboard. This will insert the previous line of code into the shell. Keep pressing it to go further back in your history, and if you go too far, press the Down Arrow key to go the other way. Try using it now.

# Strings

Python lets you do much more than calculate. In fact, we're not going to touch numbers or maths for a while. Instead, we're going to look at *strings*. Strings are essentially snippets of text. For example, enter the following into the shell, quotes (`'`) included:

__program_indented__
    """, program="'hello'")
    def hello_string(self):
        return self.matches_program()

    @step("""
The shell simply gives the same thing back because there's nothing to further to calculate. `'hello'` is simply equal to `'hello'`.

A string is a sequence of characters - in this case the 5 characters `hello`. The quotes are not part of the string - they are there to tell both humans and computers that this is a string consisting of whatever characters are between the quotes.

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
          hints="The space character must be somewhere inside quotes.")
    def hello_world_space(self):
        if "'hello world'" not in self.result:
            return False

        if search_ast(
                self.expr,
                ast.BinOp(left=ast.Str(), op=ast.Add(), right=ast.Str()),
        ):
            return True

        return dict(message="You must still add two or more strings together.")

    @step("""
Well done! Any of the following are valid solutions:

    'hello ' + 'world'
    'hello' + ' world'
    'hello' + ' ' + 'world'

# Variables

To make interesting programs, we can't always manipulate the same values. We need a way to refer to values that are unknown ahead of time and can change - values that can vary. These are called *variables*.

Run this code:

__program_indented__
    """, program="word = 'Hello'")
    def word_assign(self):
        # TODO // case sensitive
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

    @step("""
The answer is that `sunshine` looks like a variable, so Python tries to look up its value, but since we never defined a variable with that name we get an error.

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

    @step("""
Hooray! No more quotes! We'll break down what's happening in this code later. For now just know that `print(<something>)` displays `<something>` in the console. In particular it displays the actual content of strings that we usually care about, instead of a representation of strings that's suitable for code which has things like quotes. The word `print` here has nothing to do with putting ink on paper.

# Writing programs

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

    @step("""
Congratulations, you have run your first actual program!

Take some time to understand this program. Python runs each line one at a time from top to bottom. You should try simulating this process in your head - think about what each line does. See how the value of `word` was changed and what effect this had. Note that when `print` is used multiple times, each thing (`Hello World` and `Goodbye World` in this case) is printed on its own line.

Some things to note about programs in the editor:

1. The program runs in the shell, meaning that the variables defined in the program now exist in the shell with the last values they had in the program. This lets you explore in the shell after the program completes. For example, `name` now has the value `'World'` in the shell.
2. Programs run in isolation - they don't depend on any previously defined variables. The shell is reset and all previous variables are cleared. So even though `word` currently exists in the shell, if you delete the first line of the program and run it again, you'll get an error about `word` being undefined.
3. If you enter code in the shell and it has a value, that value will automatically be displayed. That doesn't happen for programs in the editor - you have to print values. If you remove `print()` from the program, changing the two lines to just `word + ' ' + name`, nothing will be displayed.

I recommend that you check all of these things for yourself.

# `for` loops

Good news! You've made it past the boring basics. We can start to write some interesting programs and have a bit of fun. One of the most powerful concepts in programming is the *loop*, which lets you repeat the same code over and over. Python has two kinds of loop: `for` loops and `while` loops. Here is an example of a for loop, try running this program:

__program_indented__
    """, program="""
name = 'World'
for character in name: print(character)
""")
    def first_for_loop(self):
        return self.matches_program()

    @step("""
You can read the code almost like normal English:

> For each character in the string `name`, print that character.

Each character is just a normal string. `character` is a normal variable that is given a new value before the code after the `:` runs. So the code above is equivalent to:

    name = 'World'

    character = 'W'
    print(character)

    character = 'o'
    print(character)

    character = 'r'
    print(character)

    character = 'l'
    print(character)

    character = 'd'
    print(character)

Note that we could use a different variable name, `character` just makes it clearer.

A for loop generally follows this structure:

    for <variable> in <collection>: <code to repeat>

The `for`, `in`, and `:` are all essential.

Actually, the example above is simplified; it would usually (and should) be written like so:

    for character in name:
        print(character)

Specifically, the code to be repeated (known as the *body*) starts on a new line after the colon (`:`), and it must be *indented*, i.e. have some spaces before it. The code below without indentation is invalid, run it to see for yourself:

    for character in name:
    print(character)
    """)
    def missing_indentation(self):
        return 'expected an indented block' in self.result

    @step("""
The spaces are required to tell Python which lines of code belong to the body of the for loop. This is critical when the loop contains several lines, which it often will. For example, run this code:

    __program_indented__
    """, program="""
name = 'World'

for character in name:
    print(character)
    print('---')
""")
    def two_indented_lines(self):
        return self.matches_program()

    @step("""
There are two indented lines, so they're both part of the body, so `---` gets printed after each character. Now try running the same code without the indentation in the last line:

    __program_indented__
    """, program="""
name = 'World'

for character in name:
    print(character)
print('---')
""")
    def one_indented_line(self):
        return self.matches_program()

    @step("""
Since `print('---')` is not indented, it's not part of the loop body. This means it only runs once, after the whole loop has finished running.

Both programs are valid, they just do different things. The below program is invalid, try running it:

    for character in name:
        print(character)
      print('---')
    """)
    def mismatched_indentations(self):
        return 'unindent does not match any outer indentation level' in self.result

    @step("""
The problem is that both lines are indented, but by different amounts. The first line starts with 4 spaces, the second line starts with 2. When you indent, you should always indent by 4 spaces. Any consistent indentation is actually acceptable, but 4 spaces is the convention that almost everyone follows. Note that the editor generally makes this easy for you. For example, if you press the 'Tab' key on your keyboard in the editor, it will insert 4 spaces for you.

Time for some exercises! Modify this program:

    name = 'World'

    for character in name:
        print(character)
        print('---')

to instead output:

    ---W
    ---o
    ---r
    ---l
    ---d
    """, hints="""
You should only use one print, since each print outputs on a different line.
You will need to use `+`.
    """)
    def loop_exercise_1(self):
        @returns_stdout
        def solution(name):
            for character in name:
                print('---' + character)

        def test(func):
            check_result(func, {"name": "World"}, """\
---W
---o
---r
---l
---d
""")
            check_result(func, {"name": "Bob"}, """\
---B
---o
---b
""")

        def generate_inputs():
            return {"name": generate_short_string()}

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    @step("""
Splendid! Now write a program which prints `name` once for each character in `name`. For example, for `name = 'Amy'`, it should output:

    Amy
    Amy
    Amy

For `name = 'World'`, it should output:

    World
    World
    World
    World
    World
    """, hints="""
Forget loops for a moment. How would you write a program which prints `name` 3 times?
The solution looks very similar to the other programs we've seen in this section.
The for loop will create a variable such as `character`, but the program doesn't need to use it.
""")
    def loop_exercise_2(self):
        @returns_stdout
        def solution(name):
            for _ in name:
                print(name)

        def test(func):
            check_result(func, {"name": "World"}, """\
World
World
World
World
World
""")
            check_result(func, {"name": "Bob"}, """\
Bob
Bob
Bob
""")

        def generate_inputs():
            return {"name": generate_short_string()}

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    @step("""
Fabulous! Before we look at some more loops, we need to quickly learn another concept. Look at this program:


What do you think the line `hello = hello + '!'` does? What do you think the program will output? Make a prediction, then run it to find out.

__program_indented__
    """, program="""
hello = 'Hello'
print(hello)
hello = hello + '!'
print(hello)
    """)
    def hello_plus_equals(self):
        return self.matches_program()

    @step("""
Python doesn't care that `hello` is on both the left and the right of the `=`, it just does what it would always do if the variables were different: it calculates `hello + '!'` which at the time is `'Hello' + '!'` which is `'Hello!'`, and that becomes the new value of `hello`. If it helps, you can think of that line as split into two steps:

    temp = hello + '!'
    hello = temp

or:

    temp = hello
    hello = temp + '!'

This is very useful in a loop. Think about what this program will do, then run it:

__program_indented__

By the way, `''` is called the *empty string* - a string containing no characters.
    """, program="""
name = 'World'
line = ''
for char in name:
    line = line + char
    print(line)
    """)
    def name_triangle(self):
        return self.matches_program()

    @step("""
The details in the above program are important. What goes wrong if you swap the last two lines and run this program instead?

__program_indented__
    """, program="""
name = 'World'
line = ''
for char in name:
    print(line)
    line = line + char
""")
    def name_triangle_missing_last_line(self):
        return self.matches_program()

    @step("""
The last character in `name` only gets added to `line` at the end of the loop, after `print(line)` has already run for the last time. So that character and the full `name` never get printed at the bottom of the triangle.

Exercise: modify the original program to add a space after every character in the triangle, so the output looks like this:

    W
    W o
    W o r
    W o r l
    W o r l d
    """, hints="""
You will need to use one more `+`.
You will need to use a string consisting of one space: `' '`.
""")
    def name_triangle_spaced(self):
        @returns_stdout
        def solution(name):
            line = ''
            for char in name:
                line = line + char + ' '
                print(line)

        def test(func):
            check_result(func, {"name": "World"}, """\
W 
W o 
W o r 
W o r l 
W o r l d 
""")
            check_result(func, {"name": "Bob"}, """\
B 
B o 
B o b 
""")

        def generate_inputs():
            return {"name": generate_short_string()}

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    @step("""
Tremendous! Now modify the program so that each line is backwards, like this:

    W
    oW
    roW
    lroW
    dlroW
    """, hints="""
The solution is very similar to the original triangle program, just make one small change.
You still want to add one character to `line` at a time, it's just a question of where you add it.
You want the lines to be reversed, so you need to reverse/flip something.
You need to add the character before the string, instead of after.
3 + 7 is equal to 7 + 3. Same for all numbers. Is this also true for strings?
""")
    def name_triangle_backwards(self):
        @returns_stdout
        def solution(name):
            line = ''
            for char in name:
                line = char + line
                print(line)

        def test(func):
            check_result(func, {"name": "World"}, """\
W
oW
roW
lroW
dlroW
""")
            check_result(func, {"name": "Amy"}, """\
A
mA
ymA
""")

        def generate_inputs():
            return {"name": generate_short_string()}

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    @step("""
Brilliant!

Code like:

    line = line + char

is so common that Python lets you abbreviate it. This means the same thing:

    line += char

Note that there is no abbreviation for `line = char + line`.

Now use `+=` and a for loop to write your own program which prints `name` 'underlined', like this:

    World
    -----

There should be one `-` for each character in `name`.
    """, hints="""
Look at the triangle program for inspiration.
Look at the program where you printed `name` once for each character for inspiration.
You will need to build up a string of dashes (`-`) one character at a time.
The for loop will create a variable such as `char`, but the program doesn't need to use it.
""")
    def name_underlined(self):
        @returns_stdout
        def solution(name):
            line = ''
            for _ in name:
                line += '-'
            print(name)
            print(line)

        def test(func):
            check_result(func, {"name": "World"}, """\
World
-----
""")
            check_result(func, {"name": "Bob"}, """\
Bob
---
""")

        def generate_inputs():
            return {"name": generate_short_string()}

        return self.check_exercise(solution, test, generate_inputs, functionise=True)

    @step("""
Fantastic!

By the way, when you don't need to use a variable, it's common convention to name that variable `_` (underscore), e.g. `for _ in name:`. This doesn't change how the program runs, but it's helpful to readers.

Let's make this fancier. Extend your program to draw a box around the name, like this:

    +-------+
    | World |
    +-------+

Note that there is a space between the name and the pipes (`|`).
    """, hints=[
        "You did all the hard stuff in the previous exercise. Now it's just some simple string concatenation.",
        "You only need one for loop - the one used to make the line of dashes from the previous exercise.",
        "Don't try and do everything at once. Break the problem up into smaller, easier subproblems.",
        dedent("""\
        Try writing programs that output:

            -----
            World
            -----

        and:

            | World |

        and:

            +-----+
            |World|
            +-----+

        (i.e. no spaces around `World`)
        """),
    ])
    def name_box(self):
        # TODO handle using two loops
        @returns_stdout
        def solution(name):
            line = ''
            for _ in name:
                line += '-'
            line = '+-' + line + '-+'
            print(line)
            print('| ' + name + ' |')
            print(line)

        def test(func):
            check_result(func, {"name": "World"}, """\
+-------+
| World |
+-------+
        """)
            check_result(func, {"name": "Bob"}, """\
+-----+
| Bob |
+-----+
        """)

        def generate_inputs():
            return {"name": generate_short_string()}

        @returns_stdout
        def missing_spaces_solution(name):
            line = ''
            for _ in name:
                line += '-'
            line = '+' + line + '+'
            print(line)
            print('|' + name + '|')
            print(line)

        def missing_spaces_test(func):
            check_result(func, {"name": "World"}, """\
+-----+
|World|
+-----+
            """)
            check_result(func, {"name": "Bob"}, """\
+---+
|Bob|
+---+
            """)

        if self.check_exercise(
                missing_spaces_solution,
                missing_spaces_test,
                generate_inputs,
                functionise=True,
        ) is True:
            return dict(
                message="You're almost there! Just add a few more characters to your strings. "
                        "Your loop is perfect."
            )

        result = self.check_exercise(solution, test, generate_inputs, functionise=True)
        if result is True:
            if sum(isinstance(node, ast.For) for node in ast.walk(self.tree)) > 1:
                return dict(
                    message="Well done, this solution is correct! However, it can be improved. "
                            "You only need to use one loop - using more is inefficient. "
                            "You can reuse the variable containing the line of `-` and `+`."
                )
        return result

    @step("""
You're getting good at this! Looks like you need more of a challenge...maybe instead of putting a name in a box, the name should be the box? Write a program that outputs this:

    +World+
    W     W
    o     o
    r     r
    l     l
    d     d
    +World+
    """, hints="""
You will need two for loops over `name`, one after the other.
Each line except for the first and last has the same characters in the middle. That means you can reuse something.
Create a variable containing the spaces in the middle and use it many times.
Use one loop to create a bunch of spaces, and a second loop to print a bunch of lines using the previously created spaces.
""")
    def name_box_2(self):
        # TODO only allow two loops
        # TODO no nested loops
        @returns_stdout
        def solution(name):
            line = '+' + name + '+'
            spaces = ''
            for _ in name:
                spaces += ' '

            print(line)
            for char in name:
                print(char + spaces + char)
            print(line)

        def test(func):
            check_result(func, {"name": "World"}, """\
+World+
W     W
o     o
r     r
l     l
d     d
+World+
""")
            check_result(func, {"name": "Bob"}, """\
+Bob+
B   B
o   o
b   b
+Bob+
""")

        def generate_inputs():
            return {"name": generate_short_string()}

        result = self.check_exercise(solution, test, generate_inputs, functionise=True)
        if result is True:
            for outer in ast.walk(self.tree):
                if isinstance(outer, ast.For):
                    for inner in ast.walk(outer):
                        if isinstance(inner, ast.For) and outer != inner:
                            return dict(
                                message="Well done, this solution is correct! "
                                        "And you used a nested loop (a loop inside a loop) which we "
                                        "haven't even covered yet! "
                                        "However, in this case a nested loop is inefficient. "
                                        "You can make a variable containing spaces and reuse that in each line."
                            )

        return result

    @step("""
Sweet! You're really getting the hang of this! If you want, here's one more optional bonus challenge. Try writing a program that outputs:

    W
     o
      r
       l
        d

Or don't, it's up to you.
    """)
    def end_of_book(self):
        return False


def search_ast(node, template):
    return any(
        is_ast_like(child, template)
        for child in ast.walk(node)
    )
