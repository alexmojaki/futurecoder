# flake8: NOQA E501

from main.text import ExerciseStep, Page, VerbatimStep
from main.utils import returns_stdout


class DefiningFunctions(Page):
    class define_greet(VerbatimStep):
        """
You've seen how to call functions such as `print()` and `len()`. Now you're going to learn how to write your own
functions that you or other people can use. This is very important as programs get bigger and more complicated.

Here's a simple example:

__program_indented__

This defines a function called `greet` which accepts one parameter. Below the definition, we call the function twice.
Run the code to see what happens.
        """

        def program(self):
            def greet(name):
                print("Hello " + name + "!")

            greet("Alice")
            greet("Bob")

    class how_are_you(VerbatimStep):
        """
A function definition is a compound statement. Like `if` and `for`, it has a header line followed by an indented body
which can contain one or more statements.

Add another statement to the function so that it looks like this:

    def greet(name):
        print("Hello " + name + "!")
        print("How are you?")

Then run the program again.
        """

        program_in_text = False

        def program(self):
            def greet(name):
                print("Hello " + name + "!")
                print("How are you?")

            greet("Alice")
            greet("Bob")

    class change_function_name(VerbatimStep):
        """
Note how the output of the program changed. `How are you?` is printed twice. You can think of the whole program as being
equivalent to this:

    name = "Alice"
    print("Hello " + name + "!")
    print("How are you?")

    name = "Bob"
    print("Hello " + name + "!")
    print("How are you?")

This shows one of the most useful things about functions. They let you reuse the same code multiple times without
having to repeat yourself. It's like writing a program within a program.

The header line of a function definition always has these parts:

1. The special keyword `def`, followed by a space.
2. The name of the function. This is like a variable name - you can choose the name you want, but there are some constraints,
e.g. it can't contain a space.
3. A pair of parentheses `(` and `)`
4. Zero or more parameter names between the parentheses, separated by commas if there's more than one. Here we have
one parameter called `name`.
5. A colon `:`

Let's do some simple exercises. Change the name of the function from `greet` to `say_hello`.
Make sure the whole program stays working as before, but don't change anything else.
"""

        program_in_text = False

        hints = """
You have to change the name in the function definition header, but that's not all.
If you just change the name in the function definition header, what happens?
You get an error. Look at the message. What is it telling you? Where does the error come from?
If your function is called `say_hello`, what does `greet("Alice")` mean?
You need to change exactly 3 lines of the program.
In each line you change, change exactly one word.
Don't touch the body of the function. It should still have `print("How are you?")`.
You should still call the function twice after defining it, with arguments `"Alice"` and `"Bob"`.
"""

        def program(self):
            def say_hello(name):
                print("Hello " + name + "!")
                print("How are you?")

            say_hello("Alice")
            say_hello("Bob")

    class change_parameter_name(VerbatimStep):
        """
Good! Now do a similar exercise: change the name of the parameter from `name` to `person_name`.
"""

        program_in_text = False

        hints = """
You have to change the parameter name in the function definition header, but that's not all.
If you just change the parameter name in the function definition header, what happens?
You get an error. Look at the message. What is it telling you? Where does the error come from?
If the parameter is called `person_name`, what does `print("Hello " + name + "!")` mean?
You need to change exactly 2 lines of the program.
In each line you change, change exactly one word.
Don't touch the part after the function definition, i.e. `say_hello("Alice")` and `say_hello("Bob")`.
You should still have two statements in the function body, including `print("How are you?")`.
"""

        def program(self):
            def say_hello(person_name):
                print("Hello " + person_name + "!")
                print("How are you?")

            say_hello("Alice")
            say_hello("Bob")

    class print_twice_exercise(ExerciseStep):
        """
Well done!

Now write your own function called `print_twice` which accepts one argument `x` and prints that argument twice
on two lines.

For example, `print_twice("Hello")` should output:

    Hello
    Hello

You can test your function by calling it after the function definition, but it's not required.
"""

        hints = """
There's no clever problem solving here, this is just about following the recipe for defining a function.
Make sure you have all the parts of a function listed above.
That includes `def`, `()`, and `:`.
Make sure your function is named `print_twice`.
Make sure it accepts one parameter in between the parentheses `()`.
Look at the other functions defined above for help.
Use the parameter inside the function body.
Make sure the body is indented.
The body needs two statements or a very simple loop.
Make sure that you don't call `print_twice` inside the function body of `print_twice`. Check your indentation.
"""

        def solution():
            @returns_stdout
            def print_twice(_, x: str):
                print(x)
                print(x)

            return print_twice

        tests = {
            "Hello": "Hello\nHello\n",
            123: "123\n123\n",
        }

    class print_many(VerbatimStep):
        """
Functions can have many parameters. Here's an example:

__program_indented__
"""

        def program(self):
            def print_many(thing, n):
                for _ in range(n):
                    print(thing)

            print_many("Hello", 3)

    class swap_parameters(VerbatimStep):
        """
Note the commas used to separate parameters in the function definition and arguments in the function call,
and the correspondence between the definition and the call:

    def print_many(thing, n):
                     ^    ^
                     |    |
      print_many("Hello", 3)

So calling `print_many("Hello", 3)` is like running:

    thing = "Hello"
    n = 3
    for _ in range(n):
        print(thing)

Now for another simple exercise. Swap around the parameters in the function definition header so that it says:

    def print_many(n, thing):

If you do this and nothing else, you will get an error. Fix the rest of the program so that it behaves like before.
*Don't change the body of the function*.
"""
        program_in_text = False

        hints = """
The only change to the function definition should be the swapping of parameters as instructed, nothing else.
You need to fix the call to `print_many`.
If the function is defined as `def print_many(n, thing)`, what does `print_many("Hello", 3)` mean?
We still want `thing = "Hello"` and `n = 3`.
"""

        def program(self):
            def print_many(n, thing):
                for _ in range(n):
                    print(thing)

            print_many(3, "Hello")

    final_text = """
Perfect! Now you have a solid foundation of the basics of defining functions.
"""


class CallingFunctionsWithinFunctions(Page):
    class print_twice_call_print_many(VerbatimStep):
        """
The body of a function can contain anything, including function calls. In fact we've already done that by calling
print. But calling one of our own functions is no different, so our functions can call each other!

For example, we can implement `print_twice` using `print_many`:

__program_indented__
"""

        def program(self):
            def print_many(n, thing):
                for _ in range(n):
                    print(thing)

            def print_twice(x):
                print_many(2, x)

            print_twice("Hello")

    class see_stack_in_snoop(print_twice_call_print_many):
        text = """
It's important to get a good sense of what's going on here and to know how
to explore function calls, so we're going to try this out in each debugger.

First, run the program again with Snoop.
        """

        expected_code_source = "snoop"
        program_in_text = False

    class see_stack_in_pythontutor(print_twice_call_print_many):
        text = """
Snoop starts each function call with:

1. A new level of indentation in the logs.
2. `>>> Call to <function name>`
3. The values of the arguments.
4. The function header line.

It ends the call with `<<< Return value from <function name>`. We'll learn about return values soon.

Now run the program again with Python Tutor.
        """

        expected_code_source = "pythontutor"
        program_in_text = False

    class see_stack_in_birdseye(print_twice_call_print_many):
        text = """
Each time a function is called, a new *frame* is created, which contains the local variable values
in that call and other information about what's currently happening.
When the function call completes, the frame is deleted.

You can see this in Python Tutor on the right under "Frames". At the top is the Global frame,
the top level frame where the whole program is running. As you click Next, new frames appear
and then disappear. In each one you can see the values of the variables.

Finally, run the program with Bird's Eye.
        """

        expected_code_source = "birdseye"
        program_in_text = False

    final_text = """
Bird's Eye only shows one frame (function call) at a time. At first you see the global frame.
At the bottom is the call to `print_twice`. Click on the little blue arrow to take
you into that frame, and then click on the next one to enter `print_many`.
"""


class ReturningValuesFromFunctions(Page):
    class first_return(VerbatimStep):
        """
Functions can be especially useful when they *return* values, rather than just printing them. Try this example:

__program_indented__
        """

        def program(self):
            def double(x):
                return x * 2

            number = 5
            twice = double(number)
            print(number)
            print(twice)

    class losing_return_value(VerbatimStep):
        """
Here we passed `number` (which has value `5`) as the argument `x` to the function `double`, and `double` *returned*
`x * 2`, i.e. `5 * 2`, i.e. `10`, which became the value of the variable `twice`. The special keyword `return` inside
`double` makes `double(number)` an expression with a value - specifically the value which was returned.
It's a bit like `twice = double(number)` is equivalent to `double = number * 2`, although that's not
exactly what happens.

Note that `double(number)` *didn't change `number`*. At the end, `number` is still `5`. Rather, `double(number)`
returned a new value. It's crucial that the program made use of that returned value, in this case by storing
it in a variable. Immediately printing it with `print(double(number))` also works. On the other hand,
this doesn't work:

__program_indented__
        """

        def program(self):
            def double(x):
                return x * 2

            number = 5
            double(number)
            print(number)

    class quadruple_exercise(ExerciseStep):
        """
Here `double(number)` still returned `10`, but we didn't make use of that so it was lost. `number` is still `5`.

Write a function `quadruple` which takes one argument and returns that argument multiplied by 4.
You must only use the `double` function - no numbers or multiplication are allowed directly in the body
of `quadruple`.
        """

        hints = """
To multiply by 4, multiply by 2 twice.
That means you need to call `double` twice.
Make sure you use the returned value from `double` each time.
Make sure you have all the parts of a function definition.
That includes `def`, `()`, and `:`.
Make sure your function is named `quadruple`.
Make sure it accepts one parameter in between the parentheses `()`.
Use the parameter inside the function body.
Make sure the body is indented.
Make sure you `return` something at the end.
Look at the definition of `double` for an example.
Make sure that you don't call `quadruple` inside the function body of `quadruple`. Check your indentation.
"""

        def solution():
            def double(x):
                return x * 2

            def quadruple(_, x: int):
                return double(double(x))

            return quadruple

        tests = {3: 12, 10: 40}

    final_text = """
Well done! Here are two possible solutions:

    def quadruple(x):
        x = double(x)
        x = double(x)
        return x

    def quadruple(x):
        return double(double(x))
        """
