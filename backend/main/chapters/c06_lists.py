# flake8: NOQA E501
import ast
import random
from textwrap import dedent
from typing import List

from main.exercises import generate_list, generate_string
from main.text import ExerciseStep, MessageStep, Page, Step, VerbatimStep, search_ast


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

    class index_exercise(ExerciseStep):
        """
Let's get some exercise! Given a list `things` and a value `to_find`,
print the first index of `to_find` in the list, i.e. the lowest number `i` such that
`things[i]` is `to_find`. For example, for

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

    string1 = "Goodbye"
    string2 = "World"

output:

    G W
    o o
    o r
    d l
    b d
    y  
    e  

and for:

    string1 = "Hello"
    string2 = "Elizabeth"

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

        # TODO catch user writing string1 < string2

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

    # TODO this is quite the information dump and I'd like it to be a little more interactive,
    # but users don't need to know these functions off by heart.

    class sum_list(Step):
        """
Let's review how to work with lists. Suppose we have a list `nums = [1, 2, 3]`. You can use:

- **`append`**: Add an element to the end of the list. `nums.append(4)` changes the list to `[1, 2, 3, 4]`.
- **`len`**: Returns the number of elements. `len(nums)` is `3`.
- **`range`**: `range(n)` is an object similar to the list of numbers from 0 to `n - 1`. In particular, `range(len(nums))` is like `[0, 1, 2]`.
- **`subscripting`**: Get a value at an index. `nums[0]` is 1, `nums[1]` is 2, `nums[2]` is 3.
- **`+`**: Concatenates lists. `nums + [4, 5]` is `[1, 2, 3, 4, 5]`.

Here's some new things. Try them out in the shell.

- **`subscript assignment`**: Set a value at an index. `nums[0] = 9` changes the list to `[9, 2, 3]`.
- **`join`**: Add a list of strings with a separator in between. This is a method of strings (the separator) which takes an iterable of strings as an argument. `'--'.join(['apples', 'oranges', 'bananas'])` returns `'apples--oranges--bananas'`. You can also use an empty string if you don't want a separator, e.g. `''.join(['apples', 'oranges', 'bananas'])` returns `'applesorangesbananas'`. 
- **`sum`**: Add a list of numbers. `sum(nums)` is 6.
- **`in`**: A comparison operator that checks if a value is in a list. `2 in nums` is `True`, but `4 in nums` is `False`.
- **`index`**: Returns the first index of a value in a list. `[7, 8, 9, 8].index(8)` is 1. Raises an error if the value isn't there.

You may recognise some of these from your exercises. I assure you that those exercises were not pointless, as you've now learned valuable fundamental skills. For example, you can use `in` to check if a list contains 5, but there's no similarly easy way to check for a number bigger than 5.

It's useful to know these functions, but it's not easy to learn them all, and there's many more. A more important skill is being able to look things up. For example, here are some typical ways you might Google the above functions if you forgot their names:

- `append`
    - python add element to list
    - python add item at end of list
- `len`
    - python size of list
    - python number of elements in list
    - python how many characters in string
- `join`
    - python combine list of strings with separator
    - python add together list of strings with string in between
- `sum`
    - python add list of numbers
    - python total of numbers
- `in`
    - python check if list contains value
    - python test if list has element
- `index`
    - python get position of element
    - python get index of value

Let's practice this skill now. Find a function/method that returns the value in a list which is bigger than any other value. For example, given the list `[21, 55, 4, 91, 62, 49]`, it will return `91`. You should write the answer in the shell as a single small expression. For example, if you were looking for the function `sum`, you could write `sum([21, 55, 4, 91, 62, 49])`. Don't solve this manually with a loop.
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
                self.stmt,
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

Replace the middle line (i.e. the call to `append`) with the right function/method call to do that. 
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

Here are a few more useful functions/methods. Suppose `nums = [28, 99, 10, 81, 59, 64]`

- **`sorted`**: Takes an iterable and returns a list of the elements in order. `sorted(nums)` returns `[10, 28, 59, 64, 81, 99]`.
- **`pop`**: Removes and returns an element at a given index. `nums.pop(3)` removes `nums[3]` (`81`) from the list and returns it. Without an argument, i.e. just `nums.pop()`, it will remove and return the last element.
- **`remove`**: Removes the first occurrence of the given element. `nums.remove(10)` will leave `nums` as `[28, 99, 81, 59, 64]`. Raises an error if the value doesn't exist. Equivalent to `nums.pop(nums.index(10))`.
- **`count`**: Returns the number of times the argument appears in the list. `[1, 2, 3, 2, 7, 2, 5].count(2)` is 3.

You've already seen that `len` and subscripting work with strings, a bit as if strings are lists of characters. Strings also support some of the new methods we've learned, not just for characters but for any substring. For example:

- `'the' in 'feed the dog and the cat'` is `True`
- `'feed the dog and the cat'.count('the')` is 2
- `'feed the dog and the cat'.index('the')` is 5

Note that in most cases, methods which modify a list in place (`append`, `insert`, `remove`) merely return `None`, while the remaining functions/methods return a new useful value without changing the original argument. The only exception is the `pop` method.

Modifying a value directly is called *mutation* - types of values which can be mutated are *mutable*, while those that can't are *immutable*. Strings are immutable - they don't have any methods like `append` or even subscript assignment. You simply can't change a string - you can only create new strings and use those instead. That means that this is a useless statement on its own:

    word.upper()

The string referred to by `word` isn't modified, instead `word.upper()` returned a new string which was immediately discarded. If you want to change the value that `word` refers to, you have to assign a new value to the variable:

    word = word.upper()

Or you can use `word.upper()` immediately in a larger expression, e.g.

    if word.lower() == 'yes':
        """


class UnderstandingProgramsWithPythonTutor(Page):
    class run_with_python_tutor(VerbatimStep):
        """
It's time to learn about another tool to explore programs.
Copy the code below into the editor and then click the new "Python Tutor" button.
The button opens a new tab with a visualisation from [pythontutor.com](http://pythontutor.com).
There you can navigate through the program step by step with the "Prev" or "Next" buttons, or drag
the slider left or right. You can also see the values of variables on the right.

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
    title = "`==` vs `is`"

    class two_separate_lists(VerbatimStep):
        """
It's time to learn some technical details that are often misunderstood and lead to errors.
Run this program:

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
    final_text = """
Consider this program. It loops through a numbers and removes the ones smaller than 10. Or at least, it tries to. I recommend running it with Python Tutor.

    numbers = [10, 7, 8, 3, 12, 15]
    for i in range(len(numbers)):
        number = numbers[i]
        if number <= 10:
            numbers.pop(i)
    print(numbers)

(remember that `numbers.pop(i)` removes the element from `numbers` at index `i`)

As it runs, it clearly skips even looking at 7 or 3 and doesn't remove them, and at the end it fails when it tries to access an index that's too high. Can you see why this happens?

The index variable `i` runs through the usual values 0, 1, 2, ... as it's supposed to, but as the list changes those are no longer the positions we want. For example in the first iteration `i` is 0 and `number` is 10, which gets removed. This shifts the rest of the numbers left one position, so now 7 is in position 0. But then in the next iteration `i` is 1, and `numbers[i]` is 8. 7 got skipped. 

We could try writing the program to use `remove` instead of `pop` so we don't have to use indices. It even looks nicer this way.

    numbers = [10, 7, 8, 3, 12, 15]
    for number in numbers:
        if number <= 10:
            numbers.remove(number)
    print(numbers)

But it turns out this does the same thing, for the same reason. Iterating over a list still goes through the indices under the hood.

The lesson here is to ***never modify something while you iterate over it***. Keep mutation and looping separate.

The good news is that there are many ways to solve this. You can instead just loop over a copy, as in:

    for number in numbers.copy():

Now the list being modified and the list being itererated over are separate objects, even if they start out with equal contents.

Similarly, you could loop over the original and modify a copy:

    numbers = [10, 7, 8, 3, 12, 15]
    big_numbers = numbers.copy()

    for number in numbers:
        if number <= 10:
            big_numbers.remove(number)
    print(big_numbers)

Or you could build up a new list from scratch. In this case, we've already done a similar thing in an exercise:

    numbers = [10, 7, 8, 3, 12, 15]
    big_numbers = []

    for number in numbers:
        if number > 10:
            big_numbers.append(number)
    print(big_numbers)
"""
