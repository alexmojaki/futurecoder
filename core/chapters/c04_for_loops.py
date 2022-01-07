# flake8: NOQA E501
import ast
from textwrap import dedent

from core.text import ExerciseStep, MessageStep, Page, Step, VerbatimStep, search_ast, Disallowed


class IntroducingForLoops(Page):

    class first_for_loop(VerbatimStep):
        """
Good news! You've made it past the boring basics. We can start to write some interesting programs and have a bit of fun. One of the most powerful concepts in programming is the *loop*, which lets you repeat the same code over and over. Python has two kinds of loop: `for` loops and `while` loops. Here is an example of a for loop, try running this program:

__program_indented__
        """

        def program(self):
            name = 'World'
            for character in name: print(character)

    final_text = """
You can read the code almost like normal English:

> For each character in the string `name`, print that character.

Each character is just a normal string. `character` is a normal variable that is given a new value before the code after the `:` runs. So the code above is equivalent to:

    __no_auto_translate__
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

    class missing_indentation(Step):
        """
This example loop:

    for character in name: print(character)

works, but actually it would usually (and should) be written like this:

    for character in name:
        print(character)

Specifically, the code to be repeated (known as the *body*) starts on a new line after the colon (`:`), and it must be *indented*, i.e. have some spaces before it. The code below without indentation is invalid, run it to see for yourself:

__program_indented__
        """

        program = """
for character in name:
print(character)
"""

        def check(self):
            return 'expected an indented block' in self.result

    class two_indented_lines(VerbatimStep):
        """
The spaces are required to tell Python which lines of code belong to the body of the for loop. This is critical when the loop contains several lines, which it often will. For example, run this code:

    __program_indented__
        """

        def program(self):
            name = 'World'

            for character in name:
                print(character)
                print('---')

    class one_indented_line(VerbatimStep):
        """
There are two indented lines, so they're both part of the body, so `---` gets printed after each character. Now try running the same code without the indentation in the last line:

    __program_indented__
        """

        def program(self):
            name = 'World'

            for character in name:
                print(character)
            print('---')

    class mismatched_indentations(Step):
        """
Since `print('---')` is not indented, it's not part of the loop body. This means it only runs once, after the whole loop has finished running. Both programs are valid, they just do different things.

The program below is invalid. Both lines in the loop body are indented, but by different amounts. The first line starts with 4 spaces, the second line starts with 2. Try running it.

__program_indented__
        """

        program = """
for character in name:
    print(character)
  print('---')
"""

        def check(self):
            return 'unindent does not match any outer indentation level' in self.result

    final_text = """
When you indent, you should always indent by 4 spaces. Any consistent indentation is actually acceptable, but 4 spaces is the convention that almost everyone follows. Note that the editor generally makes this easy for you. For example, if you press the 'Tab' key on your keyboard in the editor, it will insert 4 spaces for you.
"""


class BasicForLoopExercises(Page):

    class loop_exercise_1(ExerciseStep):
        """
Time for some exercises! Modify this program:

    name = 'World'

    for character in name:
        print(character)
        print('---')

to instead output:

    __no_auto_translate__
    ---W
    ---o
    ---r
    ---l
    ---d
        """

        hints = """
You should only use one `print`, since each print outputs on a different line.
You will need to use `+`.
        """

        def solution(self, name: str):
            for character in name:
                print('---' + character)

        tests = {
            'World': """\
---W
---o
---r
---l
---d
""",
            'Bob': """\
---B
---o
---b
""",
        }

    class loop_exercise_2(ExerciseStep):
        """
Splendid! Now write a program which prints `name` once for each character in `name`. For example, for `name = 'Amy'`, it should output:

    __no_auto_translate__
    Amy
    Amy
    Amy

For `name = 'World'`, it should output:

    __no_auto_translate__
    World
    World
    World
    World
    World

By the way, you can set `name` to anything in the first line. Only the rest of the program after that will be checked.
        """

        hints = """
Forget loops for a moment. How would you write a program which prints `name` 3 times?
The solution looks very similar to the other programs we've seen in this section.
The for loop will create a variable such as `character`, but the program doesn't need to use it.
        """

        def solution(self, name: str):
            for _ in name:
                print(name)

        tests = {
            'World': """\
World
World
World
World
World
""",
            'Bob': """\
Bob
Bob
Bob
""",
        }

    final_text = """
We're making really good progress! You're solving problems and writing new code!
Let's keep making things more interesting.
"""


class BuildingUpStrings(Page):

    class hello_plus_equals(VerbatimStep):
        """
Before we look at some more loops, we need to quickly learn another concept. Look at this program:

__program_indented__

What do you think the line `hello = hello + '!'` does? Run the program to find out.
        """

        predicted_output_choices = [
            "Hello\n"
            "Hello",
            "Hello\n"
            "Hello!",
            "Hello!\n"
            "Hello!",
        ]

        def program(self):
            hello = 'Hello'
            print(hello)
            hello = hello + '!'
            print(hello)

    class name_triangle(VerbatimStep):
        """
Python doesn't care that `hello` is on both the left and the right of the `=`, it just does what it would always do if the variables were different: it calculates `hello + '!'` which at the time is `'Hello' + '!'` which is `'Hello!'`, and that becomes the new value of `hello`. If it helps, you can think of that line as split into two steps:

    temp = hello + '!'
    hello = temp

or:

    temp = hello
    hello = temp + '!'

This is very useful in a loop. Try out this program:

__program_indented__
        """

        predicted_output_choices = [
            "-\n"
            "W\n"
            "-\n"
            "o\n"
            "-\n"
            "r\n"
            "-\n"
            "l\n"
            "-\n"
            "d",
            "-W\n"
            "-o\n"
            "-r\n"
            "-l\n"
            "-d",
            "-World",
            "-W-o-r-l-d",
            "-W\n"
            "-Wo\n"
            "-Wor\n"
            "-Worl\n"
            "-World\n",
            "-World\n"
            "-Worl\n"
            "-Wor\n"
            "-Wo\n"
            "-W\n",
            "-World\n"
            "-World\n"
            "-World\n"
            "-World\n"
            "-World\n",
            "-World\n"
            "--World\n"
            "---World\n"
            "----World\n"
            "-----World\n",
        ]

        def program(self):
            name = 'World'
            line = '-'
            for char in name:
                line = line + char
                print(line)

    class name_triangle_missing_last_line(VerbatimStep):
        """
Take your time to make sure you understand this program fully. It's doing something like this:

    line = '-'

    char = 'W'
    line = line + char
         = '-'  + 'W'
         = '-W'
    print('-W')

    char = 'o'
    line = line  + char
         = '-W'  + 'o'
         = '-Wo'
    print('-Wo')

    char = 'r'
    line = line  + char
         = '-Wo' + 'r'
         = '-Wor'
    print('-Wor')

    ...

The details are important. What happens if you swap the last two lines and run this program instead?

__program_indented__
        """

        predicted_output_choices = [
            "-W\n"
            "-Wo\n"
            "-Wor\n"
            "-Worl\n"
            "-World\n",
            "-Wo\n"
            "-Wor\n"
            "-Worl\n"
            "-World\n",
            "-\n"
            "-W\n"
            "-Wo\n"
            "-Wor\n"
            "-Worl\n"
        ]

        def program(self):
            name = 'World'
            line = '-'
            for char in name:
                print(line)
                line = line + char

    class empty_string(VerbatimStep):
        """
The last character in `name` only gets added to `line` at the end of the loop, after `print(line)` has already run for the last time. So that character and the full `name` never get printed at the bottom of the triangle. If you're confused, try putting `print(line)` both before and after `line = line + char`.

Let's get rid of those `-` characters in the output. You might already be able to guess how.

An *empty string* is a string containing no characters at all.
It's written as just a pair of quotes surrounding nothing: `''`.
It's like the zero of strings.
Adding it to another string just gives you the other string unchanged,
in the same way that `0 + 5` is just `5`.

Try this in the shell:

__program_indented__
        """

        expected_code_source = "shell"

        program = "'' + '' + ''"

        predicted_output_choices = [
            "''",
            "' '",
            "'  '",
            "'   '",
            "'' + '' + ''",
            "''''''",
            "'' '' ''",
            "' '' '' '",
            "++",
        ]

    class name_triangle_empty_string(ExerciseStep):
        """
Don't confuse the empty string with `' '`, which is a non-empty string containing one character: a space.

Now fix the original program to get rid of those lines in the output, so that
for `name = 'World'` it prints:

    __no_auto_translate__
    W
    Wo
    Wor
    Worl
    World
        """

        hints = """
First make sure you're not working from the broken version of the previous program on this page.
That is, `line = line + char` should come before `print(line)`.
Apart from that, you only need to make one ***tiny*** change.
We want to get rid of the `-`. So just do that. Literally.
Use an empty string!
        """

        def solution(self, name: str):
            line = ''
            for char in name:
                line = line + char
                print(line)

        tests = {
            'World': """\
W
Wo
Wor
Worl
World
""",
            'Bob': """\
B
Bo
Bob
""",
        }

    final_text = """
Isn't that pretty?

The pattern of starting with something empty and building it up with a `for` loop is *very* common
and you're going to get lots of practice with it. Some initial empty values are
`''`, `0`, and `[]` - an empty list, which you'll see soon.
"""


class BuildingUpStringsExercises(Page):

    class name_triangle_spaced(ExerciseStep):
        """
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
        """

        hints = """
You will need to use one more `+`.
You will need to use a string consisting of one space: `' '`.
        """

        def solution(self, name: str):
            line = ''
            for char in name:
                line = line + char + ' '
                print(line)

        tests = {
            'World': """\
W
W o
W o r
W o r l
W o r l d
""",
            'Bob': """\
B
B o
B o b
""",
        }

    class name_triangle_backwards(ExerciseStep):
        """
Tremendous! Now modify the program so that each line is backwards, like this:

    __no_auto_translate__
    W
    oW
    roW
    lroW
    dlroW
        """

        hints = """
The solution is very similar to the original triangle program, just make one small change.
You still want to add one character to `line` at a time, it's just a question of where you add it.
You want the lines to be reversed, so you need to reverse/flip something.
You need to add the character before the string, instead of after.
3 + 7 is equal to 7 + 3. Same for all numbers. Is this also true for strings?
        """

        def solution(self, name: str):
            line = ''
            for char in name:
                line = char + line
                print(line)

        tests = {
            'World': """\
W
oW
roW
lroW
dlroW
""",
            'Amy': """\
A
mA
ymA
""",
        }

    class name_underlined(ExerciseStep):
        """
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
        """

        hints = """
Look at the triangle program for inspiration.
Look at the program where you printed `name` once for each character for inspiration.
You will need to build up a string of dashes (`-`) one character at a time.
The for loop will create a variable such as `char`, but the program doesn't need to use it.
        """

        parsons_solution = True

        def solution(self, name: str):
            line = ''
            for _ in name:
                line += '-'
            print(name)
            print(line)

        tests = {
            'World': """\
World
-----
""",
            'Bob': """\
Bob
---
""",
        }

    class name_box(ExerciseStep):
        """
Fantastic!

By the way, when you don't need to use a variable, it's common convention to name that variable `_` (underscore), e.g. `for _ in name:`. This doesn't change how the program runs, but it's helpful to readers.

Let's make this fancier. Extend your program to draw a box around the name, like this:

    +-----+
    |World|
    +-----+
        """

        hints = [
            "You did all the hard stuff in the previous exercise. Now it's just some simple adding of strings.",
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

                |World|
            """),
        ]

        parsons_solution = True

        def solution(self, name: str):
            line = ''
            for _ in name:
                line += '-'
            line = '+' + line + '+'
            print(line)
            print('|' + name + '|')
            print(line)

        tests = {
            "World": """\
+-----+
|World|
+-----+
""",
            "Bob": """\
+---+
|Bob|
+---+
""",
        }

        disallowed = [
            Disallowed(
                ast.For,
                max_count=1,
                message="""
                    Well done, this solution is correct! However, it can be improved.
                    You only need to use one loop - using more is inefficient.
                    You can reuse the variable containing the line of `-` and `+`.
                    """,
            )
        ]

    class name_box_2(ExerciseStep):
        """
You're getting good at this! Looks like you need more of a challenge...maybe instead of putting a name in a box, the name should be the box? Write a program that outputs this:

    +World+
    W     W
    o     o
    r     r
    l     l
    d     d
    +World+
        """

        hints = """
You will need two separate for loops over `name`.
Each line except for the first and last has the same characters in the middle. That means you can reuse something.
Create a variable containing the spaces in the middle and use it many times.
Use one loop to create a bunch of spaces, and a second loop to print a bunch of lines using the previously created spaces.
        """

        parsons_solution = True

        def solution(self, name: str):
            line = '+' + name + '+'
            spaces = ''
            for _ in name:
                spaces += ' '

            print(line)
            for char in name:
                print(char + spaces + char)
            print(line)

        tests = {
            "World": """\
+World+
W     W
o     o
r     r
l     l
d     d
+World+
""",
            "Bob": """\
+Bob+
B   B
o   o
b   b
+Bob+
""",
        }

        disallowed = [
            Disallowed(
                ast.For,
                predicate=lambda outer: search_ast(outer, ast.For),
                message="""
                    Well done, this solution is correct!
                    And you used a nested loop (a loop inside a loop) which we haven't even covered yet!
                    However, in this case a nested loop is inefficient.
                    You can make a variable containing spaces and reuse that in each line.
                """
            ),
        ]

    class diagonal_name_bonus_challenge(ExerciseStep):
        """
Sweet! You're really getting the hang of this!

If you want you can do one more optional bonus challenge below.
If not, you can just continue to the [next page](#BasicTerminology) now.
You can come back and do this later if you want.

Try writing a program that outputs the given `name` in a diagonal line, e.g:

    W
     o
      r
       l
        d
        """

        hints = """
The first letter should have 0 spaces before it, the second letter should have 1 space before it, the third should have 2, etc.
You should keep the spaces in a variable and build them up in a loop, as before.
The difference is that you need to print letters at the same time as building up spaces.
In other words, you need a single loop that does both.
The body of the loop needs to print the spaces and letter, and also add a space.
Since the first letter should have no spaces before it, you need to add a space after printing a letter.
        """

        # TODO message: catch print(spaces, char) instead of print(spaces + char)

        parsons_solution = True

        def solution(self, name: str):
            spaces = ''
            for char in name:
                print(spaces + char)
                spaces += ' '

        tests = {
            'World': """\
W
 o
  r
   l
    d
""",
            'Bob': """\
B
 o
  b
""",
        }

        class add_space_first(MessageStep, ExerciseStep):
            """
            Almost there! You have one space too many before each letter.
            Make sure that the first time your loop calls `print`
            your variable which will contain the spaces is an empty string.
            Check the order of your code.
            """
            def solution(self, name: str):
                spaces = ''
                for char in name:
                    spaces += ' '
                    print(spaces + char)

            tests = {
                'World': """\
 W
  o
   r
    l
     d
""",
                'Bob': """\
 B
  o
   b
""",
            }

    final_text = """
Wow, nothing can stop you!
    """


class BasicTerminology(Page):
    final_text = """
Here's some words you need to know:

An ***expression*** is a piece of code that has a value. For example, in this line of code:

    __no_auto_translate__
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
