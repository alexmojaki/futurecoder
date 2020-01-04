import ast
from textwrap import dedent

from main.exercises import generate_short_string, check_result
from main.text import Page, step
from main.utils import returns_stdout


class IntroducingForLoops(Page):
    @step("""
Good news! You've made it past the boring basics. We can start to write some interesting programs and have a bit of fun. One of the most powerful concepts in programming is the *loop*, which lets you repeat the same code over and over. Python has two kinds of loop: `for` loops and `while` loops. Here is an example of a for loop, try running this program:

__program_indented__
    """, program="""
name = 'World'
for character in name: print(character)
""")
    def first_for_loop(self):
        return self.matches_program()

    final_text = """
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
"""


class Indentation(Page):
    @step("""
This example loop:

    for character in name: print(character)

works, but actually it would usually (and should) be written like this:

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

    final_text = """
The problem is that both lines are indented, but by different amounts. The first line starts with 4 spaces, the second line starts with 2. When you indent, you should always indent by 4 spaces. Any consistent indentation is actually acceptable, but 4 spaces is the convention that almost everyone follows. Note that the editor generally makes this easy for you. For example, if you press the 'Tab' key on your keyboard in the editor, it will insert 4 spaces for you.
"""


class BasicForLoopExercises(Page):
    @step("""
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

By the way, you can set `name` to anything in the first line. Only the rest of the program after that will be checked.
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

    final_text = """
We're making really good progress! You're solving problems and writing new code!
Let's keep making things more interesting.
"""


class BuildingUpStrings(Page):
    @step("""
Before we look at some more loops, we need to quickly learn another concept. Look at this program:

__program_indented__

What do you think the line `hello = hello + '!'` does? What do you think the program will output? Make a prediction, then run it to find out.
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

    final_text = """
The last character in `name` only gets added to `line` at the end of the loop, after `print(line)` has already run for the last time. So that character and the full `name` never get printed at the bottom of the triangle.
"""


class BuildingUpStringsExercises(Page):
    @step("""
Modify this program:

    name = 'World'
    line = ''
    for char in name:
        line = line + char
        print(line)

to add a space after every character in the triangle, so the output looks like this:

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
        Try writing a program that outputs:

            -----
            World
            -----
        """),
        "Since you need to output three separate lines of text, you will need to call `print()` three times.",
        dedent("""\
        Try writing a program that outputs:

            | World |
        """),
        dedent("""\
        Try writing a program that outputs:

            +-----+
            |World|
            +-----+

        (i.e. no spaces around `World`)
        """),
    ])
    def name_box(self):
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
You will need two separate for loops over `name`.
Each line except for the first and last has the same characters in the middle. That means you can reuse something.
Create a variable containing the spaces in the middle and use it many times.
Use one loop to create a bunch of spaces, and a second loop to print a bunch of lines using the previously created spaces.
""")
    def name_box_2(self):
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

    final_text = """
Sweet! You're really getting the hang of this! If you want, here's one more optional bonus challenge. Try writing a program that outputs:

    W
     o
      r
       l
        d

Or don't, it's up to you.
    """


class BasicTerminology(Page):
    final_text = """
Here's some words you need to know:

An ***expression*** is a piece of code that has a value. For example, in this line of code:

    sentence = 'Hello ' + name

there are three expressions:

1. `'Hello '`
2. `name`
3. `'Hello ' + name`

By contrast, the full line `sentence = ...` is a ***statement***. It's a command that tells the computer to perform an action. It has no value of its own. This means, for example, that you can't add statements together. This code is invalid:

    (word = 'Hello') + (name = 'Bob')

Specifically, a statement like `sentence = ...` where a variable is given a value is called ***assignment*** - the value is *assigned to* the the variable.

A program is a list of statements which are executed in order. A `for` loop is a *compound statement*, meaning it has a body of its own which contains other statements. Most statements will also contain expressions, and expressions can contain other smaller expressions, but expressions cannot contain statements.

The process of calculating the value of an expression is called ***evaluation*** - note how it almost contains the word 'value'. The computer *evaluates* `1 + 2` to get the value `3`.

The process of executing a loop is called ***iteration***. Code like `for char in 'Hello':` is *iterating over* the string `'Hello'`. The fact that it's possible means that strings are *iterable*. By contrast, numbers are not iterable, which is exactly what Python will tell you if you try `for char in 3:`. Each run through the loop is *one iteration*, so in this example there will be 5 iterations.
"""
