# flake8: NOQA E501
import ast
import random
from textwrap import dedent
from typing import List

from core.exercises import generate_list, generate_string
from core.text import (
    ExerciseStep,
    MessageStep,
    Page,
    Step,
    VerbatimStep,
    search_ast,
    Disallowed,
)


class IntroducingLists(Page):
    class first_list(VerbatimStep):
        """
It's time to learn about a powerful new type of value called *lists*. Here's an example:

__program_indented__
        """

        auto_translate_program = False

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

    __no_auto_translate__
    words = ['This', 'is', 'a', 'list']

it should print:

    __no_auto_translate__
    Thisisalist
        """

        hints = """
This is very similar to the exercises you've done building up strings character by character.
The solution is very similar to the program that adds numbers.
In fact, what happens if you try running that program with a list of strings?
The problem is that 0. You can't add 0 to a string because numbers and strings are incompatible.
Is there a similar concept among strings to 0? A blank initial value?
"""

        def solution(self, words: List[str]):
            total = ''
            for word in words:
                total += word

            print(total)

        tests = [
            (['This', 'is', 'a', 'list'], 'Thisisalist'),
            (['The', 'quick', 'brown', 'fox', 'jumps'], 'Thequickbrownfoxjumps'),
        ]

    class strings_sum_bonus(ExerciseStep):
        """
Excellent!

If you'd like, you can just continue to the [next page](#BuildingNewLists) now.

For an optional bonus challenge: extend the program to insert a separator string *between* each word.
For example, given

    __no_auto_translate__
    words = ['This', 'is', 'a', 'list']
    separator = ' - '

it would output:

    __no_auto_translate__
    This - is - a - list
        """

        hints = """
This is similar to the previous exercise. You can start with your solution from that.
This exercise doesn't require anything fancy and the final solution can be quite simple. But it's tricky to get it right and you need to think about the approach carefully.
In each iteration, in addition to a word in the list, you also have to add the separator.
But you don't want to add the separator after adding the last word in the list.
Unfortunately there is no "subtraction" with strings; you can't add the last separator then remove it.
Let's back up. The final result should contain each word, and `n - 1` separators, where `n` is the number of words.
So you want to add a separator in every iteration except one.
You can skip adding the separator in one particular iteration using an `if` statement.
Later on you will learn a way to iterate over a list and check if you're in the last iteration, but right now you have no way of doing that.
However, the iteration you skip doesn't have to be the last one!
You *can* write a program that checks if you're in the *first* iteration of a loop.
Just make a boolean variable to keep track of this. No need for any comparison operators or numbers.
We looked at programs that did something like this [here](#UnderstandingProgramsWithSnoop).
So if you only skip adding the separator in the first iteration, you will have `n - 1` separators. Now you just need to think carefully about how to make sure the separators are in the right place.
Forgetting the loop for a moment, you need to add the following to the string in this order: the first word, the separator, the second word, the separator, the third word, etc.
That means that in the first iteration, you just add the first word. In the second iteration, you add the separator, then the second word. In the third iteration, you add the separator, then the third word. And so on.
So inside your loop, add the separator first, add the word after.
Skip adding the separator in the first iteration by checking a boolean variable.
Create the boolean variable before the loop, then change it inside the loop.
Only change it in the loop after checking it, or you won't be able to skip the first iteration.
        """

        # TODO message: catch the "obvious solution" where the user adds the separator after the last word?

        parsons_solution = True

        def solution(self, words: List[str], separator: str):
            total = ''
            not_first = False

            for word in words:
                if not_first:
                    total += separator
                total += word
                not_first = True

            print(total)

        tests = [
            ((['This', 'is', 'a', 'list'], ' - '), 'This - is - a - list'),
            ((['The', 'quick', 'brown', 'fox', 'jumps'], '**'), 'The**quick**brown**fox**jumps'),
        ]

    final_text = """
Congratulations! That was very tricky! One solution looks like this:

    __no_auto_translate__
    words = ['This', 'is', 'a', 'list']
    separator = ' - '
    total = ''
    not_first = False

    for word in words:
        if not_first:
            total += separator
        total += word
        not_first = True

    print(total)
        """


class BuildingNewLists(Page):
    class double_numbers(ExerciseStep):
        """
Lists and strings have a lot in common.
For example, you can add two lists to combine them together into a new list.
You can also create an empty list that has no elements.
Check for yourself:

    __copyable__
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

        disallowed = Disallowed(
            ast.AugAssign,
            message="Well done, that's correct! However, you should use `.append()` instead of `+=`.",
        )

        parsons_solution = True

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

    __no_auto_translate__
    things = ['This', 'is', 'a', 'list']
    thing_to_find = 'is'

it should print `True`, but for

    __no_auto_translate__
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

        parsons_solution = True

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
    title = "Getting elements at a position, `range()`, and `len()`"

    class introducing_subscripting(VerbatimStep):
        """
Looping is great, but often you just want to retrieve a single element from the list at a known position.
Here's how:

__program_indented__
        """

        auto_translate_program = False

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

        auto_translate_program = False

        program = "words[4]"

        def check(self):
            return "IndexError" in self.result

    class improve_with_list_and_loop(VerbatimStep):
        """
There you go. `words[4]` and beyond don't exist, so trying that will give you an error.
That first program is a bit repetitive. Let's improve it with a list and a loop!

__program_indented__
        """

        auto_translate_program = False

        def program(self):
            words = ['This', 'is', 'a', 'list']
            indices = [0, 1, 2, 3]

            for index in indices:
                print(index)
                print(words[index])

    class using_range_instead_of_indices(VerbatimStep):
        """
That's a bit better, but writing out `[0, 1, 2, ...]` isn't great, especially if it gets long.
There's a handy function `range` to do that part for you. Replace `[0, 1, 2, 3]` with `range(4)`,
i.e. `indices = range(4)`.
        """

        program_in_text = False

        auto_translate_program = False

        def program(self):
            words = ['This', 'is', 'a', 'list']
            indices = range(4)

            for index in indices:
                print(index)
                print(words[index])

    class printing_the_range(VerbatimStep):
        """
As you can see, the result is the same. Try this:

    __copyable__
    __program_indented__
        """

        predicted_output_choices = ["""\
0
1
2
3
""", """\
1
2
3
4
""", """\
[0]
[1]
[2]
[3]
""", """\
[1]
[2]
[3]
[4]
""", """\
This
is
a
list
""",
                                    ]

        def program(self):
            indices = range(4)

            print(indices[0])
            print(indices[1])
            print(indices[2])
            print(indices[3])

    class indices_out_of_bounds(VerbatimStep):
        """
Now try `__program__` in the shell. What do you expect the output to be?
        """

        predicted_output_choices = ["0", "1", "2", "3", "4"]

        correct_output = "Error"

        expected_code_source = "shell"

        program = "indices[4]"

    class range_almost_the_same_as_list(VerbatimStep):
        """
`range(4)` is the same thing as `[0, 1, 2, 3]` ... almost. Try `__program__` in the shell.
        """

        expected_code_source = "shell"

        program = "range(4)"

    class range_versus_list(VerbatimStep):
        """
That's probably a bit surprising. If you're curious, the `0` represents the start of the range.
`0` is the default start, so `range(4)` is equal to `range(0, 4)`.
`4` is the end of the range, but the end is always excluded, so the last value is `3`.
If you're confused now, don't worry about it.

There's a good reason for why `range(4)` is not actually a list - it makes programs faster and more efficient.
It's not worth explaining that more right now.

But you can easily convert it to a list: try `__program__` in the shell.

What do you expect the output to be?
        """
        predicted_output_choices = [
            "range(4)",
            "range(0, 4)",
            "list(range(4))",
            "list(range(0, 4))",
            "range(0, 1, 2, 3)",
            "(0, 1, 2, 3)",
            "[0, 1, 2, 3]"
        ]

        expected_code_source = "shell"

        program = "list(range(4))"

    class introducing_len_and_range(VerbatimStep):
        """
That's just a demonstration to let you see a range in a more familiar form.
You should almost never actually do that.

If you're feeling overwhelmed, don't worry! All you need to know is that `range(n)`
is very similar to the list:

    [0, 1, 2, ..., n - 2, n - 1]

By the way, you can get the number of elements in a list (commonly called the *length*) using the `len` function.
Run the following code:

    __copyable__
    __program_indented__
        """
        auto_translate_program = False

        predicted_output_choices = ["0", "1", "2", "3", "4"]

        def program(self):
            words = ['This', 'is', 'a', 'list']
            print(len(words))

    class print_last_element(ExerciseStep):
        """
Exercise: for any non-empty list `words`, print the last element. For example, if

    __no_auto_translate__
    words = ['This', 'is', 'a', 'list']

your program should print `list`.
        """

        hints = """
To access the last element of the list, you'll need the index of the last position.
If the list has 2 elements, the first element is at index 0, so the last element is at index 1.
Likewise, if the list had 3 elements, the last element would be at index 2.
Do you see a pattern between those numbers? How can you express it?
Can you come up with a general solution that works for any length?
        """

        def solution(self, words: List[str]):
            print(words[len(words) - 1])

        tests = [
            (["Python"], "Python"),
            (['Hello', 'world'], "world"),
            (['futurecoder', 'is', 'cool!'], "cool!"),
            (['This', 'is', 'a', 'list'], "list")
        ]

    class range_len(ExerciseStep):
        """
So in general, the valid indices are:

    [0, 1, 2, ..., len(words) - 2, len(words) - 1]

Exercise: for any non-empty list `words`, print each index and element of the list. For example, if

    __no_auto_translate__
    words = ['This', 'is', 'a', 'list']

your program should print:

    0
    This
    1
    is
    2
    a
    3
    list

        """

        hints = """
This is similar to an earlier step, where we looped through two lists `words` and `indices` at the same time.
This time there is only one list, and it could be of any length.
Think back to earlier steps. We replaced `indices` with a function.
How can you combine the two functions you just learned, `range()` and `len()`, to help you here?
        """

        def solution(self, words: List[str]):
            for index in range(len(words)):
                print(index)
                print(words[index])

        tests = [
            (['Python'], """\
0
Python
                        """),
            (['Hello', 'world'], """\
0
Hello
1
world
                    """),
            (['futurecoder', 'is', 'cool!'], """\
0
futurecoder
1
is
2
cool!
                    """),
            (['This', 'is', 'a', 'list'], """\
0
This
1
is
2
a
3
list
                    """),
        ]

    class index_exercise(ExerciseStep):
        """
Using `range` and `len` in combination is a very important skill! At first it may seem complicated.
If you'd like some more practice with `range` and `len`, here are a few suggestions for you to practice on your own.
Don't feel like you have to do all of these, just as much as you need to.

For any list `words` and any positive number `n`:

Print the numbers from `1` to `n` inclusive.

Print the word `Python` `n` times.

Print each word in `words` except for the last one.

Print each word in `words` in reverse order.

Go back and revisit the bonus problem on the [Introducing Lists page](#IntroducingLists), even if you've done it. It's now much easier with `range` and `len`!

Let's get some more exercise! Given a list `things` and a value `to_find`,
print the first index of `to_find` in the list, i.e. the lowest number `i` such that
`things[i]` is `to_find`. For example, for

    __no_auto_translate__
    things = ['on', 'the', 'way', 'to', 'the', 'store']
    to_find = 'the'

your program should print `1`.

You can assume that `to_find` appears at least once.
        """

        hints = """
You will need to look at all the possible indices of `things` and check which one is the answer.
To look at all possible indices, you will need a loop over `range(len(things))`.
To check if an index is the answer, you will need to use:
- `if`
- the index in a subscript
- `==`
Since you're looking for the first index, you need to stop the loop once you find one.
You learned how to stop a loop in the middle recently.
You need to use `break`.
        """

        class all_indices(MessageStep, ExerciseStep):
            """
            You're almost there! However, this prints all the indices,
            not just the first one.
            """

            def solution(self, things, to_find):
                for i in range(len(things)):
                    if to_find == things[i]:
                        print(i)

            tests = [
                ((['on', 'the', 'way', 'to', 'the', 'store'], 'the'), "1\n4"),
                (([0, 1, 2, 3, 4, 5, 6, 6], 6), "6\n7"),
            ]

        class last_index(MessageStep, ExerciseStep):
            """
            You're almost there! However, this prints the *last* index,
            not the first one.
            """

            def solution(self, things, to_find):
                answer = None
                for i in range(len(things)):
                    if to_find == things[i]:
                        answer = i
                print(answer)

            tests = [
                ((['on', 'the', 'way', 'to', 'the', 'store'], 'the'), 4),
                (([0, 1, 2, 3, 4, 5, 6, 6], 6), 7),
            ]

        def solution(self, things, to_find):
            for i in range(len(things)):
                if to_find == things[i]:
                    print(i)
                    break

        tests = [
            ((['on', 'the', 'way', 'to', 'the', 'store'], 'the'), 1),
            (([0, 1, 2, 3, 4, 5, 6, 6], 6), 6),
        ]

        @classmethod
        def generate_inputs(cls):
            things = generate_list(str)
            to_find = generate_string()
            things += [to_find] * random.randint(1, 3)
            random.shuffle(things)
            return dict(
                things=things,
                to_find=to_find,
            )

    class zip_exercise(ExerciseStep):
        """
Nice!

By the way, indexing and `len()` also work on strings. Try them out in the shell.

Here's another exercise. Given two strings of equal length, e.g:

    __no_auto_translate__
    string1 = 'Hello'
    string2 = 'World'

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

    class zip_longest_exercise(ExerciseStep):
        """
Incredible!

Your solution probably looks something like this:

    for i in range(len(string1)):
        char1 = string1[i]
        char2 = string2[i]
        print(char1 + ' ' + char2)

This doesn't work so well if the strings have different lengths.
In fact, it goes wrong in different ways depending on whether `string1` or `string2` is longer.
Your next challenge is to fix this problem by filling in 'missing' characters with spaces.

For example, for:

    __no_auto_translate__
    string1 = 'Goodbye'
    string2 = 'World'

output:

    G W
    o o
    o r
    d l
    b d
    y
    e

and for:

    __no_auto_translate__
    string1 = 'Hello'
    string2 = 'Elizabeth'

output:

    H E
    e l
    l i
    l z
    o a
      b
      e
      t
      h
        """

        hints = [
            "The solution has the same overall structure and "
            "essential elements of the previous solution, "
            "but it's significantly longer and will require "
            "a few additional ideas and pieces.",
            dedent("""
            In particular, it should still contain something like:

                for i in range(...):
                    ...
                    print(char1 + ' ' + char2)
            """),
            "What should go inside `range()`? Neither `len(string1)` nor `len(string2)` is good enough.",
            "You want a loop iteration for every character in the longer string.",
            "That means you need `range(<length of the longest string>)`",
            "In other words you need to find the biggest of the two values "
            "`len(string1)` and `len(string2)`. You've already done an exercise like that.",
            "Once you've sorted out `for i in range(...)`, `i` will sometimes be too big "
            "to be a valid index for both strings. You will need to check if it's too big before indexing.",
            "Remember, the biggest valid index for `string1` is `len(string1) - 1`. "
            "`len(string)` is too big.",
            "You will need two `if` statements, one for each string.",
            "You will need to set e.g. `char1 = ' '` when `string1[i]` is not valid.",
        ]

        # TODO message: catch user writing string1 < string2 instead of comparing lengths

        parsons_solution = True

        def solution(self, string1, string2):
            length1 = len(string1)
            length2 = len(string2)

            if length1 > length2:
                length = length1
            else:
                length = length2

            for i in range(length):
                if i < len(string1):
                    char1 = string1[i]
                else:
                    char1 = ' '

                if i < len(string2):
                    char2 = string2[i]
                else:
                    char2 = ' '

                print(char1 + ' ' + char2)

        tests = {
            ("Goodbye", "World"): dedent("""\
                    G W
                    o o
                    o r
                    d l
                    b d
                    y
                    e
                    """),
            ("Hello", "Elizabeth"): dedent("""\
                    H E
                    e l
                    l i
                    l z
                    o a
                      b
                      e
                      t
                      h
                    """),
        }

        @classmethod
        def generate_inputs(cls):
            length1 = random.randrange(5, 11)
            length2 = random.randrange(12, 20)
            if random.choice([True, False]):
                length1, length2 = length2, length1
            return dict(
                string1=generate_string(length1),
                string2=generate_string(length2),
            )

    final_text = """
Magnificent! Take a break, you've earned it!
    """


class CallingFunctionsTerminology(Page):
    title = "Terminology: Calling functions and methods"

    class print_functions(VerbatimStep):
        """
It's time to expand your vocabulary some more.

`print` and `len` are ***functions***. See for yourself:

__program_indented__
        """

        def program(self):
            print(len)
            print(print)

    class introducing_callable(VerbatimStep):
        """
An expression like `len(things)` or `print(things)` is a function ***call*** - when you write that, you are ***calling*** the function `len` or `print`. The fact that this is possible means that functions are ***callable***:

__program_indented__
        """

        def program(self):
            print(callable(len))

    class not_callable(VerbatimStep):
        """
Most things are not callable, so trying to call them will give you an error:

__program_indented__
        """

        # noinspection PyCallingNonCallable
        def program(self):
            f = 'a string'
            print(callable(f))
            f()

    class print_returns_none(VerbatimStep):
        """
In the call `len(things)`, `things` is an ***argument***. Sometimes you will also see the word ***parameter***, which means basically the same thing as argument. It's a bit like you're giving the argument to the function - specifically we say that the argument `things` is *passed* to `len`, and `len` *accepts* or *receives* the argument.

`len(things)` will evaluate to a number such as 3, in which case we say that `len` ***returned*** 3.

All calls have to return something...even if it's nothing. For example, `print`'s job is to display something on screen, not to return a useful value. So it returns something useless instead:

__program_indented__
        """

        # noinspection PyNoneFunctionAssignment
        def program(self):
            things = [1, 2, 3]
            length = len(things)
            printed = print(length)
            print(printed)

    class len_of_none(VerbatimStep):
        """
`None` is a special 'null' value which can't do anything interesting. It's a common placeholder that represents the lack of a real useful value. Functions that don't want to return anything return `None` by default. If you see an error message about `None` or `NoneType`, it often means you assigned the wrong thing to a variable:

__program_indented__
        """

        # noinspection PyNoneFunctionAssignment,PyUnusedLocal,PyTypeChecker
        def program(self):
            things = print([1, 2, 3])
            length = len(things)

    class methods_of_str(VerbatimStep):
        """
A ***method*** is a function which belongs to a type, and can be called on all values of that type using `.`. For example, `upper` and `lower` are methods of strings, which are called with e.g. `word.upper()`:

__program_indented__
        """

        def program(self):
            word = 'Hello'
            print(word.upper)
            print(word.upper())

    class no_append_for_str(VerbatimStep):
        """
Another example is that `append` is a method of lists. But you can't use `.upper` on a list or `.append` on a string:

__program_indented__
        """

        # noinspection PyUnresolvedReferences
        def program(self):
            word = 'Hello'
            word.append('!')

    final_text = """
    The word 'attribute' in the error message refers to the use of `.` - the error actually comes just from `word.append`, without even a call.
        """


class FunctionsAndMethodsForLists(Page):
    title = "Functions and Methods for Lists"

    class append_vs_concatenate(VerbatimStep):
        """
Let's review how to work with lists. Suppose we have a list `nums = [1, 2, 3]`. You can use:

- **`append`**: Add an element to the end of the list. `nums.append(4)` changes the list to `[1, 2, 3, 4]`.
- **`len`**: Returns the number of elements. `len(nums)` is `3`.
- **`range`**: `range(n)` is an object similar to the list of numbers from 0 to `n - 1`. That means it contains `n` numbers. In particular, `range(len(nums))` is like `[0, 1, 2]`, which are the indices of every element in `nums`.
- **`subscripting`**: Get a value at an index. `nums[0]` is 1, `nums[1]` is 2, `nums[2]` is 3.
- **`+`**: Concatenates lists. `nums + [4, 5]` is `[1, 2, 3, 4, 5]`.

Note that `nums.append(4)` modifies the existing list `nums`, while `nums + [4, 5]` does not.
One way to preserve the value of `nums + [4, 5]` is to assign it to a *new variable*.
Run the following code:

    __copyable__
    __program_indented__
        """

        def program(self):
            nums = [1, 2, 3]
            new_nums = nums + [4, 5]
            print(new_nums)
            print(nums)
            nums.append(4)
            print(nums)

    class subscript_assignment_predict(VerbatimStep):
        """
As you can see, `+` does not modify `nums`, but `append` does.

Here's some new things.

**`subscript assignment`**: Set a value at an index (replacing the value that was there before) using the syntax

    some_list[index] = new_value

Raises an error if `index` is not a valid index of `some_list`. For example, run this program:

__program_indented__
        """

        predicted_output_choices = [
            "[9, 1, 2, 3]",
            "[1, 9, 2, 3]",
            "[1, 2, 9, 3]",
            "[9, 2, 3]",
            "[1, 9, 3]",
            "[1, 2, 9]",
        ]

        def program(self):
            nums = [1, 2, 3]
            nums[1] = 9
            print(nums)

    class index_predict_exercise(VerbatimStep):
        """
**`index`**: Returns the first index of a value in a list using the syntax

    some_list.index(value)

Raises an error if the value isn't there. For example run this line in the shell:

__program_indented__
        """

        predicted_output_choices = [
            "[7, 8]",
            "[7, 8, 9]",
            "[7, 8, 9, 8]",
            "1",
            "2",
            "3",
        ]

        expected_code_source = "shell"

        program = "[7, 8, 9, 8].index(8)"

    class pop_predict_exercise(VerbatimStep):
        """
**`pop`**: Removes and returns an element at a given *index* using the syntax

    some_list.pop(index)

Without an argument, i.e. just `some_list.pop()`, it will remove and return the last element.
Raises an error if `index` is not a valid index of `some_list`. For example run this program:

__program_indented__
        """

        predicted_output_choices = [
            "1\n"
            "[1, 3]",
            "2\n"
            "[1, 3]",
            "1\n"
            "[2, 3]",
            "2\n"
            "[2, 3]",
            "1\n"
            "[2, 1, 3]",
            "2\n"
            "[2, 1, 3]",
        ]

        def program(self):
            nums = [1, 2, 3]
            print(nums.pop(1))
            print(nums)

    class remove_predict_exercise(VerbatimStep):
        """
**`remove`**: Removes the first occurrence of the given *value* using the syntax

    some_list.remove(value)

Raises an error if the value isn't in the list. For example run this program:

__program_indented__
        """

        predicted_output_choices = [
            "[1, 2]",
            "[1, 3]",
            "[2, 3]",
            "1",
            "2",
            "3",
        ]

        def program(self):
            nums = [1, 2, 3]
            nums.remove(1)
            print(nums)

    class pop_remove_index_subscript_assignment(VerbatimStep):
        """
Now you will solve four short exercises involving these concepts.
Below is a list of correct and incorrect lines of code mixed together.
Each upcoming exercise has a solution that includes exactly one of the lines below,
and you must find the correct line from the list.

    x[len(x)] = x[0]
    x[len(x) - 1] = x[0]
    x[len(x) + 1] = x[0]
    x + x[0]
    [x] + x[0]
    x + [x[0]]
    [x] + [x[0]]
    x + x.pop(0)
    [x] + x.pop(0)
    x + [x.pop(0)]
    [x] + [x.pop(0)]
    x.pop(x.append(0))
    x.append(x.pop(0))
    x.append(x[0])
    x.append(x.index(0))
    x.index(x.append(0))
    x.pop(x.index(0))
    x.index(x.pop(0))

Here is an incomplete program:

    __copyable__
    x = ['a', 'b', 'c']
    (insert_one_line_from_above)
    print(x)

Replace the middle line with one line from the list above. The final program should modify `x` to move the first element to the end, so that it prints `['b', 'c', 'a']`.
        """

        program_in_text = False

        def program(self):
            x = ['a', 'b', 'c']
            x.append(x.pop(0))
            print(x)

        hints = """
Your solution should have exactly three statements: `x = ['a', 'b', 'c']`, then one line copied exactly from the list (no additions), and `print(x)`.
Moving the first element to the end requires two things.
Removing the first element...
and adding it to the end.
Which functions/methods can you use for this?
Remember that the first index is 0.
"""

    class subscript_assignment_exercise(VerbatimStep):
        """
Good job. For the next exercise, start with the same incomplete program:

    __copyable__
    x = ['a', 'b', 'c']
    (insert_one_line_from_above)
    print(x)

Choose a line of code from the list that overwrites the last element of `x` with the first element,
so now it should print `['a', 'b', 'a']`.
        """

        program_in_text = False

        def program(self):
            x = ['a', 'b', 'c']
            x[len(x) - 1] = x[0]
            print(x)

        hints = """
Your solution should have exactly three statements: `x = ['a', 'b', 'c']`, then one line copied exactly from the list (no additions), and `print(x)`.
You need to get the value of the first element in `x`...
and assign that value to the last position in `x`.
How do you assign a value at a specific index in the list?
What are the indices of the first and last last elements in `x`?
"""

    class negative_index_concatenation_exercise(VerbatimStep):
        """
Excellent!

You might realize that working with the last element via `x[len(x) - 1]` is a bit cumbersome.
The same can be achieved by `x[-1]`.
Similarly, the second to last element `x[len(x) - 2]` can be written as `x[-2]`, and so on.
Python allows us to count the index backwards too, starting at the last element with `-1`:

| Index     | First elt. | Second elt. | Third elt.  | ... | 2nd to last elt. | Last elt.  |
|-----------|------------|-------------|-------------|-----|------------------|------------|
| Forwards  | `0`        | `1`         | `2`         | ... | `len(x) - 2`     |`len(x) - 1`|
| Backwards | `-len(x)`  |`-len(x) + 1`|`-len(x) + 2`| ... | `-2`             |  `-1`      |

Next exercise:

This time, rather than modifying the list `x`, you will create a new list `y`:

    __copyable__
    x = ['a', 'b', 'c']
    y = (insert_one_line_from_above)
    print(y)

`y` should be the same as `x` but also have the first element repeated at the end.
Therefore the program will print `['a', 'b', 'c', 'a']`.
        """

        program_in_text = False

        def program(self):
            x = ['a', 'b', 'c']
            y = x + [x[0]]
            print(y)

        hints = """
Your solution should have exactly three statements: `x = ['a', 'b', 'c']`, `y = ` followed by one line copied exactly from the list, and `print(y)`.
Which lines of code create a new list rather than modifying?
`x` is a list. Each element of `x` is a string.
You can add lists together, you can add strings together, but you can't add a string and a list.
How do you make a list containing one element?
"""

    class remove_exercise(VerbatimStep):
        """
Great work. Now the final exercise:

    __copyable__
    x = [1, 2, 0, 3]
    x.remove(0)
    print(x)

Replace the middle line `x.remove(0)` with a line from the list that does the same thing.
        """

        program_in_text = False

        def program(self):
            x = [1, 2, 0, 3]
            x.pop(x.index(0))
            print(x)

        hints = """
Your solution should have exactly three statements: `x = [1, 2, 0, 3]`, one line copied exactly from the list (no additions), and `print(x)`.
What does `x.remove(0)` do?
It removes an element!
Which function/method can also remove an element?
The other function/method can't simply be told 'remove 0', it needs a different kind of information.
Specifically, it needs to be told where 0 is.
Which function/method provides that kind of information?
"""

    final_text = """
Great job!
    """


class MoreListFunctionsAndMethods(Page):
    title = "More List Functions and Methods"

    class sorted_predict_exercise(VerbatimStep):
        """
Here are a few more useful functions/methods.

**`sorted`**: Takes an iterable and returns a list of the elements in order from smallest to largest, using the syntax

    sorted(some_list)

For example run this line in the shell:

__program_indented__
        """

        predicted_output_choices = [
            "[9, 8, 6, 5, 2, 1]",
            "[1, 8, 6, 2, 5, 9]",
            "[1, 2, 5, 6, 8, 9]",
            "[2, 9, 1, 8, 5, 6]"
        ]

        expected_code_source = "shell"

        program = "sorted([2, 9, 1, 8, 5, 6])"

    class in_predict_exercise(VerbatimStep):
        """
**`in`**: A comparison operator that checks if a value is in a list, using the syntax

    value in some_list

For example run this program:

__program_indented__
        """

        translate_output_choices = False
        predicted_output_choices = [
            "True\n"
            "False",
            "False\n"
            "True",
            "True\n"
            "True",
            "False\n"
            "False",
        ]

        def program(self):
            nums = [2, 9, 1, 8, 5, 64]
            print(7 in nums)
            print(2 in nums)

    class sum_predict_exercise(VerbatimStep):
        """
**`sum`**: Add up an iterable of numbers using the syntax

    sum(some_list)

For example run this line in the shell:

__program_indented__
        """

        predicted_output_choices = ["10", "12", "7"]
        expected_code_source = "shell"

        def program(self):
            sum([5, 3, 4])

    class count_predict_exercise(VerbatimStep):
        """
**`count`**: Returns the number of times the argument appears in the list using the syntax

    some_list.count(value)

For example run this line in the shell:

__program_indented__
        """

        predicted_output_choices = ["0", "1", "2", "3"]

        expected_code_source = "shell"

        program = "[1, 2, 3, 2, 7, 2, 5].count(2)"

    class count_in_sorted_sum(VerbatimStep):
        """
You may recognise some of these from your exercises. I assure you that those exercises were not pointless,
as you've now learned valuable fundamental skills. For example, you can use `in` to check if a list contains 5,
but there's no similarly easy way to check for a number bigger than 5.

Now you will solve another set of four exercises involving these new concepts.
Again, correct and incorrect lines of code are mixed together,
and you must choose the correct line from the list.

    sum(len(x))
    sum(range(x))
    sum(range(len(x)))
    sum(len(range(x)))
    sum(range(x)) + 1
    sum(range(x + 1))
    sum(x) / len(x)
    sum(x) / range(x)
    sum(x) / range(len(x))
    sum(x) / len(range(x))
    sorted(x)[1]
    sorted(x)[2]
    sorted(x)[-1]
    sorted(x)[-2]
    x.count(1) >= 0
    x.count(1) > 0
    x.count(1) > 1

Here is a program:

    __copyable__
    x = [1, 2, 0, 3]
    y = 1 in x
    print(y)

Replace the part `1 in x` (leave in the `y = `) with one line from the list above that does the same thing.
        """

        program_in_text = False

        def program(self):
            x = [1, 2, 0, 3]
            y = x.count(1) > 0
            print(y)

        hints = """
Your solution should have exactly three statements: `x = ['a', 'b', 'c']`, `y = ` followed by one line copied exactly from the list, and `print(y)`.
When is `1 in x` True?
When `1` is in `x`!
Could be that `1` is in `x` once, or twice, or three times...
...but not zero times!
"""

    class average_exercise(VerbatimStep):
        """
Excellent work! For the next exercise, start with this incomplete program:

    __copyable__
    x = [15, 12, -6, 3]
    y = (insert_one_line_from_above)
    print(y)

Replace the part after `y = ` with one line from the list above.
The final program should print the average (technically the *mean*) of the numbers in `x`.
        """

        program_in_text = False

        def program(self):
            x = [15, 12, -6, 3]
            y = sum(x) / len(x)
            print(y)

        hints = """
Your solution should have exactly three statements: `x = [15, 12, -6, 3]`, `y = ` followed by one line copied exactly from the list, and `print(y)`.
If you're not sure, look up how to calculate the average/mean.
To calculate the average of numbers in `x` we need two things.
Which two functions/methods give you those two things?
How do you combine those two things to calculate the average?
"""

    class sum_range_exercise(VerbatimStep):
        """
Good job! For the next exercise, start with this incomplete program:

    __copyable__
    x = 100
    y = (insert_one_line_from_above)
    print(y)

Replace the part after `y = ` with one line from the list above.
The final program should print the result of adding up all the numbers from `1` to `x` inclusive, i.e. `1 + 2 + 3 + ... + x`.
        """

        program_in_text = False

        def program(self):
            x = 100
            y = sum(range(x + 1))
            print(y)

        hints = """
Your solution should have exactly three statements: `x = 100`, `y = ` followed by one line copied exactly from the list, and `print(y)`.
What function/method can be used to add up things?
Which function/method gives us the numbers `1, 2, 3, ..., x`?
You have to make a small tweak, otherwise that last number `x` will be left out.
"""

    class second_smallest_in_list_exercise(VerbatimStep):
        """
Excellent. And the last one:

    __copyable__
    x = [12, -6, 2, -1, 3]
    y = (insert_one_line_from_above)
    print(y)

Replace the part after `y = ` with one line from the list above.
The final program should print the *second smallest value* in `x`.
        """

        program_in_text = False

        def program(self):
            x = [12, -6, 2, -1, 3]
            y = sorted(x)[1]
            print(y)

        hints = """
Your solution should have exactly three statements: `x = [12, -6, 2, -1, 3]`, `y = ` followed by one line copied exactly from the list, and `print(y)`.
The numbers in `x` seem to be all out of order. Can you do something about that?
If you figured that part out, try using that function in the shell to play around with it.
How would you use that function to get the smallest value in a list? What about the biggest?
After that, how can you get the *second* smallest value?
"""

    final_text = """
Congratulations! You are now a master of list methods and functions!
    """


class StringMethodsUnderstandingMutation(Page):
    title = "String Methods and Immutability"

    class string_in_step(VerbatimStep):
        """
You've already seen that `len` and subscripting work with strings, a bit as if strings are lists of characters.
Strings also support some of the new methods we've learned, not just for characters but for any substring.
For example, try the following:

    __copyable__
    __program_indented__
        """

        auto_translate_program = False

        program = "print('the' in 'feed the dog and the cat')"

    class string_count_index(VerbatimStep):
        """
`in` works on strings like it does on lists! The command returned `True` because `the` occurs in `feed the dog and the cat` as a *substring*.
How about `count` and `index`?

    __copyable__
    __program_indented__
        """

        auto_translate_program = False

        def program(self):
            string = 'feed the dog and the cat'
            print(string.count('the'))
            print(string.index('the'))

    class mutation_string_append(VerbatimStep):
        """
Again these two methods also work on strings similar to how they work on lists.
`index` returns the *beginning index* of the search word `'the'` in the longer string
`'feed the dog and the cat'`, which is `5`.

|  0   |  1   |  2   |  3   |  4   | **5** |  6   |  7   |  8   | ...  |
| :--: | :--: | :--: | :--: | :--: | :---: | :--: | :--: | :--: | :--: |
|  f   |  e   |  e   |  d   |      | **t** |  h   |  e   |      | ...  |

Note that in most cases, methods which *modify a list in place* (`append`, `insert`, `remove`) merely return `None`,
while the remaining functions/methods return a new useful value without changing the original argument.
The only exception is the `pop` method.

Modifying a value directly is called *mutation* - types of values which can be mutated are *mutable*,
while those that can't are *immutable*. Lists are mutable.
Strings are immutable - they don't have any methods like `append` or even subscript assignment.
See for yourself:

    __copyable__
    __program_indented__
        """
        program = "'Python'.append(' is cool!')"

    class string_lower_upper(VerbatimStep):
        """
You simply can't change a string - you can only create new strings and use those instead.
That means that this is a useless statement on its own:

    word.lower()

The string referred to by `word` isn't modified, instead `word.lower()` returned a new string which was immediately discarded.
If you want to change the value that `word` refers to, you have to assign a new value to the variable:

    __copyable__
    __program_indented__
        """

        def program(self):
            sentence = "Python rocks!"
            new_sentence = sentence.upper()
            print(sentence)
            print(new_sentence)

    final_text = """
Observe that `sentence.upper()` does not change the original `sentence`.

You can also use `word.lower()` immediately in a larger expression, e.g.

    if word.lower() == 'yes':

    """


class HowToFindInformationWithGoogleAndMore(Page):
    title = "How to Find Information with Google, and more"

    class sum_list(Step):
        """
It's useful to know the functions we just covered, but it's not easy to learn them all, and there's many more. A more important skill is being able to look things up. For example, here are some typical ways you might Google the above functions if you forgot their names:

- `append`
    - python add element to list
    - python add item at end of list
- `len`
    - python size of list
    - python number of elements in list
    - python how many characters in string
- `sum`
    - python add list of numbers
    - python total of numbers
- `in`
    - python check if list contains value
    - python test if list has element
- `index`
    - python get position of element
    - python get index of value

Let's practice this skill now. Find a function/method that returns the value in a list which is bigger than any other value. For example, given the list `[21, 55, 4, 91, 62, 49]`, it will return `91`. You should write the answer in the shell as a single small expression. For example, if you were looking for the function `sum`, you could write `sum([21, 55, 4, 91, 62, 49])`. Don't solve this manually with a loop. Note that the function you're looking for hasn't been mentioned here before.
    """

        hints = """
Use the words 'python' and 'list' in your search query.
In one word, what's special about `91` in the list `[21, 55, 4, 91, 62, 49]`?
'biggest' or 'largest'
'python biggest value in list'
"""

        program = "max([21, 55, 4, 91, 62, 49])"

        def check(self):
            return search_ast(
                self.tree,
                ast.Call(func=ast.Name(id='max')),
            )

    class list_insert(Step):
        """
Good find! Let's do one more. Consider this program:

    nums = [1, 2, 3, 4, 5]
    nums.append(9)
    print(nums)

This changes `nums` so that it prints:

    [1, 2, 3, 4, 5, 9]

But suppose you don't want the 9 to be at the end, you want it to go between the second and third elements, so the output is:

    [1, 2, 9, 3, 4, 5]

Replace the middle line `nums.append(9)` with the right function/method call to do that.
        """

        hints = """
Use the words 'python' and 'list' in your search query.
Instead of putting the value at the beginning or end, we want to put it ____________?
'in the middle' or 'at an index' or 'at a particular position'
'python add value at index'
"""

        def program(self):
            nums = [1, 2, 3, 4, 5]
            nums.insert(2, 9)
            print(nums)

        def check(self):
            return search_ast(
                self.tree,
                ast.Call(func=ast.Attribute(attr='insert'),
                         args=[ast.Constant(value=2),
                               ast.Constant(value=9)]),
            )

    class dir_list(VerbatimStep):
        """
Perfect!

It can also be useful to Google things like "python list tutorial", e.g. if:

- Googling a specific method has failed so you want to find it manually.
- You're still confused about lists after this course.
- It's been a while since you learned about lists and you need a reminder.
- You're struggling to solve a problem with lists and you need to go back to basics and strengthen your foundations.

There are also ways to find information without any googling. Try `__program__` in the shell.
        """

        program = "dir([])"

    final_text = """
`dir()` returns a list of the argument's attributes, which are mostly methods. Many will start with `__` which you can ignore for now - scroll to the end of the list and you'll see some familiar methods.
        """


class UnderstandingProgramsWithPythonTutor(Page):
    class run_with_python_tutor(VerbatimStep):
        """
It's time to learn about another tool to explore programs.
Copy the code below into the editor and then click the new "Python Tutor" button.
The button opens a new tab with a visualisation from [pythontutor.com](http://pythontutor.com).
There you can navigate through the program step by step with the "Prev" or "Next" buttons, or drag
the slider left or right. You can also see the values of variables on the right.

    __copyable__
    __program_indented__
        """

        expected_code_source = "pythontutor"

        def program(self):
            all_numbers = [2, 4, 8, 1, 9, 7]

            small_numbers = []
            big_numbers = []

            for number in all_numbers:
                if number <= 5:
                    small_numbers.append(number)
                else:
                    big_numbers.append(number)

            print(small_numbers)
            print(big_numbers)

    final_text = """
Note that the code runs twice separately: once here, once on pythontutor.com.
Depending on your program, the two runs may produce different results.
"""


class EqualsVsIs(Page):
    title = "`==` vs `is`, and Having Multiple Names for One Value"

    class two_separate_lists(VerbatimStep):
        """
It's time to learn some technical details that are often misunderstood and lead to errors.
Run this program:

    __copyable__
    __program_indented__
        """

        def program(self):
            list1 = [1, 2, 3]
            list2 = [1, 2, 3]

            print(list1)
            print(list2)
            print(list1 == list2)

            print(list1 is list2)

            list1.append(4)

            print(list1)
            print(list2)

    class same_list(VerbatimStep):
        """
This program is quite straightforward and mostly consists of things you're familiar with.
We create two variables which refer to lists.
The lists have the same elements, so they are equal: `list1 == list2` is `True`.

But then there's a new comparison operator: `is`. Here `list1 is list2` is `False`.
That means that regardless of the two lists being equal,
they are still two separate, distinct, individual lists.
As a result, when you append 4 to `list1`, only `list1` changes.

Now change `list2 = [1, 2, 3]` to `list2 = list1` and see what difference it makes.
        """

        program_in_text = False

        def program(self):
            list1 = [1, 2, 3]
            list2 = list1

            print(list1)
            print(list2)
            print(list1 == list2)

            print(list1 is list2)

            list1.append(4)

            print(list1)
            print(list2)

    final_text = """
Now `list1 is list2` is `True`, because *there is only one list*, and the two variables
`list1` and `list2` both refer to that same list. `list1.append(4)` appends to the one list
and the result can be seen in both `print(list1)` and `print(list2)` because both lines
are now just different ways of printing the same list.

I recommend running both versions with Python Tutor to see how it visualises the difference.
In the second case, the two variables both have arrows pointing to a single list object.

`list2 = list1` doesn't create an eternal link between the variables. If you assign a new value
to *either* of the variables, e.g. `list1 = [7, 8, 9]`, the other variable will be unaffected
and will still point to the original list.

Basically, an assignment like:

    list2 = <expression>

means 'make the variable `list2` refer to whatever `<expression>` evaluates to'.
It doesn't make a copy of that value, which is how both variables can end up pointing to the same list.
But as we've learned before, `list2` doesn't remember `<expression>`, only the value.
It doesn't know about other variables.

You can copy a list with the `copy` method:

    list2 = list1.copy()

This will make the program behave like the first version again.

If you come across this kind of problem and you're still having trouble understanding this stuff, read the essay [Facts and myths about Python names and values](https://nedbatchelder.com/text/names.html).
"""


class ModifyingWhileIterating(Page):
    class run_broken_with_python_tutor(VerbatimStep):
        """
Consider this program. It loops through a list of numbers and removes the ones smaller than 10. Or at least, it tries to.
Run it with Python Tutor.

    __copyable__
    __program_indented__

(remember that `numbers.pop(i)` removes the element from `numbers` at index `i`)
        """

        expected_code_source = "pythontutor"

        def program(self):
            numbers = [10, 7, 8, 3, 12, 15]
            for i in range(len(numbers)):
                number = numbers[i]
                if number <= 10:
                    numbers.pop(i)
            print(numbers)

    class remove_instead_of_pop(VerbatimStep):
        """
As it runs, it clearly skips even looking at 7 or 3 and doesn't remove them, and at the end it fails when it tries to access an index that's too high. Can you see why this happens?

The index variable `i` runs through the usual values 0, 1, 2, ... as it's supposed to, but as the list changes those are no longer the positions we want. For example in the first iteration `i` is 0 and `number` is 10, which gets removed. This shifts the rest of the numbers left one position, so now 7 is in position 0. But then in the next iteration `i` is 1, and `numbers[i]` is 8. 7 got skipped.

We could try writing the program to use `remove` instead of `pop` so we don't have to use indices. It even looks nicer this way.

__program_indented__
        """

        def program(self):
            numbers = [10, 7, 8, 3, 12, 15]
            for number in numbers:
                if number <= 10:
                    numbers.remove(number)
            print(numbers)

    class make_copy(VerbatimStep):
        """
But it turns out this does nearly the same thing - it doesn't end in an error, but it still doesn't remove 7 or 3.
This happens for the same reason - iterating over a list still goes through the indices under the hood.

The lesson here is to ***never modify something while you iterate over it***. Keep mutation and looping separate.

The good news is that there are many ways to solve this. You can instead just loop over a copy, as in:

    for number in numbers.copy():
        """

        program_in_text = False

        def program(self):
            numbers = [10, 7, 8, 3, 12, 15]
            for number in numbers.copy():
                if number <= 10:
                    numbers.remove(number)
            print(numbers)

    class make_copy2(VerbatimStep):
        """
Now the list being modified and the list being itererated over are separate objects, even if they start out with equal contents.

Similarly, you could loop over the original and modify a copy:

__program_indented__
        """

        def program(self):
            numbers = [10, 7, 8, 3, 12, 15]
            big_numbers = numbers.copy()

            for number in numbers:
                if number <= 10:
                    big_numbers.remove(number)
            print(big_numbers)

    class make_new_list(VerbatimStep):
        """
Or you could build up a new list from scratch. In this case, we've already done a similar thing in an exercise:

__program_indented__
        """

        def program(self):
            numbers = [10, 7, 8, 3, 12, 15]
            big_numbers = []

            for number in numbers:
                if number > 10:
                    big_numbers.append(number)
            print(big_numbers)

    final_text = """
To reiterate, ***never modify something while you iterate over it***. Your options are:

- Modify a copy
- Iterate over a copy
- Don't modify anything, make a new version instead.
    """
