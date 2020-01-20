import random
from textwrap import dedent
from typing import List

from main.exercises import generate_list, generate_string
from main.text import Page, VerbatimStep, ExerciseStep, Step
from main.utils import returns_stdout


class IntroducingLists(Page):
    class first_list(VerbatimStep):
        """
It's time to learn about a powerful new type of value called lists. Here's an example:

__program_indented__
        """

        def program(self):
            words = ['This', 'is', 'a', 'list']

            for word in words:
                print(word)

    class can_contain_anything(VerbatimStep):
        """
A list is a *sequence* (an ordered collection/container) of any number of values.
The values are often referred to as *elements*.
They can be anything: numbers, strings, booleans, even lists! They can also be a mixture of types.

To create a list directly, like above:

1. Write some square brackets: `[]`
2. If you don't want an empty list, write some expressions inside to be the elements.
3. Put commas (`,`) between elements to separate them.

Here's another example of making a list:

__program_indented__
        """

        def program(self):
            x = 1
            things = ['Hello', x, x + 3]
            print(things)

    class numbers_sum(VerbatimStep):
        """
As you saw above, lists are *iterable*, meaning you can iterate over them with a `for loop`.
Here's a program that adds up all the numbers in a list:

__program_indented__
        """

        def program(self):
            numbers = [3, 1, 4, 1, 5, 9]

            total = 0
            for number in numbers:
                total += number

            print(total)

    class strings_sum(ExerciseStep):
        """
Now modify the program so that it can add up a list of strings instead of numbers.
For example, given:

    words = ['This', 'is', 'a', 'list']

it should print:

    Thisisalist
        """

        hints = """
This is very similar to the exercises you've done building up strings character by character.
The solution is very similar to the program that adds numbers.
In fact, what happens if you try running that program with a list of strings?
The problem is that 0. You can't add 0 to a string because numbers and strings are incompatible.
Is there a similar concept among strings to 0? A blank initial value?
"""

        @returns_stdout
        def solution(self, words: List[str]):
            total = ''
            for word in words:
                total += word

            print(total)

        tests = [
            (['This', 'is', 'a', 'list'], 'Thisisalist'),
            (['The', 'quick', 'brown', 'fox', 'jumps'], 'Thequickbrownfoxjumps'),
        ]

    class double_numbers(ExerciseStep):
        """
Optional bonus challenge: extend the program to insert a separator string *between* each word.
For example, given

    words = ['This', 'is', 'a', 'list']
    separator = ' - '

it would output:

    This - is - a - list

Lists and strings have a lot in common.
For example, you can add two lists to combine them together into a new list.
You can also create an empty list that has no elements.
Check for yourself:

    numbers = [1, 2] + [3, 4]
    print(numbers)
    new_numbers = []
    new_numbers += numbers
    new_numbers += [5]
    print(new_numbers)

With that knowledge, write a program which takes a list of numbers
and prints a list where each number has been doubled. For example, given:

    numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]

it would print:

    [6, 2, 8, 2, 10, 18, 4, 12, 10]
        """

        hints = """
Remember that you can multiply numbers using `*`.
This program is structurally very similar to the programs you've written to build up strings character by character.
Make a new list, and then build it up element by element in a for loop.
Start with an empty list.
You can make a list with one element `x` by just writing `[x]`.
You can add an element to a list by adding a list containing one element.
        """

        @returns_stdout
        def solution(self, numbers: List[int]):
            double = []
            for number in numbers:
                double += [number * 2]
            print(double)

        tests = [
            ([3, 1, 4, 1, 5, 9, 2, 6, 5], [6, 2, 8, 2, 10, 18, 4, 12, 10]),
            ([0, 1, 2, 3], [0, 2, 4, 6]),
        ]

    class filter_numbers(ExerciseStep):
        """
Great!

When you want to add a single element to the end of a list, instead of:

    some_list += [element]

it's actually more common to write:

    some_list.append(element)

There isn't really a big difference between these, but `.append`
will be more familiar and readable to most people.

Now use `.append` to write a program which prints a list containing only the numbers bigger than 5.

For example, given:

    numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]

it would print:

    [9, 6]
        """

        hints = """
This is very similar to the previous exercise.
The difference is that sometimes you should skip appending to the new list.
Use an `if` statement.
Use a comparison operator to test if a number is big enough to add.
        """

        # TODO enforce not using +=

        @returns_stdout
        def solution(self, numbers: List[int]):
            big_numbers = []
            for number in numbers:
                if number > 5:
                    big_numbers.append(number)
            print(big_numbers)

        tests = [
            ([3, 1, 4, 1, 5, 9, 2, 6, 5], [9, 6]),
            ([0, 2, 4, 6, 8, 10], [6, 8, 10]),
        ]

    final_text = """
Fantastic! We're making great progress.
"""


class UsingBreak(Page):
    title = "Using `break` to end a loop early"

    class list_contains_exercise(ExerciseStep):
        """
Exercise: write a program which takes a list and a value and checks
if the list contains the value. For example, given:

    things = ['This', 'is', 'a', 'list']
    thing_to_find = 'is'

it should print `True`, but for

    thing_to_find = 'other'

it should print `False`.
        """

        hints = """
You will need a loop.
You will need an `if` statement.
You will need a comparison operator.
Specifically `==`.
You need a boolean variable that you print at the end.
If you find the element in the list you should set that variable to `True`.
Once you've found the element, you can't unfind it.
That means that once you set the variable to `True`, it should never be set to anything else after that.
Don't use an `else`.
There is no reason to ever set the variable to `False` inside the loop.
        """

        @returns_stdout
        def solution(self, things, thing_to_find):
            found = False
            for thing in things:
                if thing == thing_to_find:
                    found = True

            print(found)

        tests = [
            ((['This', 'is', 'a', 'list'], 'is'), True),
            ((['This', 'is', 'a', 'list'], 'other'), False),
            (([1, 2, 3, 4], 1), True),
            (([1, 2, 3, 4], 0), False),
        ]

        @classmethod
        def generate_inputs(cls):
            contained = random.choice([True, False])
            things = generate_list(int)
            if contained:
                thing_to_find = random.choice(things)
            else:
                thing_to_find = random.choice([
                    min(things) - 1,
                    max(things) + 1,
                ])
            return dict(
                things=things,
                thing_to_find=thing_to_find,
            )

    final_text = """
Nice!

A typical solution looks something like this:

    found = False
    for thing in things:
        if thing == thing_to_find:
            found = True

    print(found)

Your solution is probably similar. It's fine, but it's a bit inefficient.
That's because it'll loop over the entire list even if it finds the element at the beginning.
You can stop any loop using a `break` statement, like so:

    for thing in things:
        if thing == thing_to_find:
            found = True
            break

This is just as correct but skips unnecessary iterations and checks once it finds the element.
You can use snoop to see the difference.
        """


class GettingElementsAtPosition(Page):
    title = "Getting Elements at a Position"

    class introducing_subscripting(VerbatimStep):
        """
Looping is great, but often you just want to retrieve a single element from the list at a known position.
Here's how:

__program_indented__
        """

        def program(self):
            words = ['This', 'is', 'a', 'list']

            print(words[0])
            print(words[1])
            print(words[2])
            print(words[3])

    class index_error(Step):
        """
In general, you can get the element at the position `i` with `words[i]`. The operation is called *subscripting* or *indexing*, and the position is called the *index*.

You've probably noticed that the first index is 0, not 1. In programming, counting starts at 0. It seems weird, but that's how most programming languages do it, and it's generally agreed to be better.

This also means that the last index in this list of 4 elements is 3. What happens if you try getting an index greater than that?
        """

        program = "words[4]"

        def check(self):
            return "IndexError" in self.result

    class introducing_len_and_range(VerbatimStep):
        """
There you go. `words[4]` and beyond don't exist, so trying that will give you an error.

By the way, you can get the number of elements in a list (commonly called the *length*) using `len(words)`.
That means that the last valid index of the list is `len(words) - 1`, so the last element is `words[len(words) - 1]`. Try these for yourself.

So in general, the valid indices are:

    [0, 1, 2, ..., len(words) - 2, len(words) - 1]

There's a handy built in function to give you these values, called `range`:

__program_indented__
        """

        def program(self):
            for i in range(10):
                print(i)

    class range_len(VerbatimStep):
        """
`range(n)` is similar to the list `[0, 1, 2, ..., n - 2, n - 1]`.
This gives us an alternative way to loop over a list:

__program_indented__
        """

        def program(self):
            words = ['This', 'is', 'a', 'list']

            for index in range(len(words)):
                print(index)
                print(words[index])

    class zip_exercise(ExerciseStep):
        """
By the way, indexing and `len()` also work on strings. Try them out in the shell.

Let's get some exercise! Given two strings of equal length, e.g:

    string1 = "Hello"
    string2 = "World"

print them vertically side by side, with a space between each character:

    H W
    e o
    l r
    l l
    o d
        """

        hints = """
Did you experiment with indexing and `len()` with strings in the shell?
Forget loops for a moment. How would you print just the first line, which has the first character of each of the two strings?
In the second line you want to print the second character of each string, and so on.
You will need a `for` loop.
You will need indexing (subscripting).
You will need `range`.
You will need `len`.
You will need `+`.
You will need to index both strings.
You will need to pass the same index to both strings each time to retrieve matching characters.
"""

        @returns_stdout
        def solution(self, string1, string2):
            for i in range(len(string1)):
                char1 = string1[i]
                char2 = string2[i]
                print(char1 + ' ' + char2)

        tests = {
            ("Hello", "World"): dedent("""\
                    H W
                    e o
                    l r
                    l l
                    o d
                    """),
            ("Having", "ablast"): dedent("""\
                    H a
                    a b
                    v l
                    i a
                    n s
                    g t
                    """),
        }

        @classmethod
        def generate_inputs(cls):
            length = random.randrange(5, 11)
            return dict(
                string1=generate_string(length),
                string2=generate_string(length),
            )

    final_text = """
TODO
    """
