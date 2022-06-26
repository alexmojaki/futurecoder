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



class IntroducingSets(Page):
    class introduce_iterables(VerbatimStep):
        """
Before introducing sets, it's helpful to understand iterables.

An iterable is an object that you can iterate over. We've seen some iterables already.

We have seen strings, lists and ranges.

Here is a reminder of what this looks like:

__program_indented__
        """

        auto_translate_program = False

        def program(self):
            for s in "ABCD": print(s)
        
            for j in [1, 2, "abc"]: print(j)

            for i in range(4): print(i)


    class first_set(VerbatimStep):
        """
Now lets learn about a powerful new type of value called *sets*. Here's an example:

__program_indented__
        """

        auto_translate_program = False

        def program(self):
            words = set(('This', 'is', 'a', 'set'))
            print(words)

    
    class can_contain_anything(VerbatimStep):
        """
A set is an unordered collection of any number of distinct values.

The values are often referred to as *elements*.

Sets are constructed out of iterables, as introduced above.


Here are some ways to create a set directly:

1. Construct a set from a tuple, or a collection of values enclosed by parenthesis as shown above. 
2. Construct from a list by saying set([...]).
3. Construct from a range by saying set(range(...))
4. You can also insert individual elements into a set by using the add method.

Here's another example of making a set:

__program_indented__
        """

        def program(self):
            x = 1
            things = set(['Hello', x, x + 3])
            things.add(42)
            print(things)

    class numbers_sum(VerbatimStep):
        """
Sets are also iterables, meaning you can iterate over them with a `for loop`.

Here's a program that adds up all the numbers in a set:

__program_indented__
        """

        def program(self):
            numbers = set([3, 1, 4, 1, 5, 9])

            total = 0
            for number in numbers:
                total += number

            print(total)

    class set_usefullness(ExerciseStep):
        """
Now we will explore when a set is useful. 
A set is useful when you want to know something about the data stored in aggreggate.

For example, suppose that you want to know how many distinct words are used in a text.

A set would allow you to easily determine this number.

Write a program that will do so now.
        """

        hints = """
Remember that a set only contains unique values.
Storing everything into a set removes all duplicates.
Then, you can just print the length of the set.
"""

        def solution(self, words: List[str]):
            words = set(words)
            print(len(words))

        tests = [
            (['This', 'is', 'a', 'list'], 4),
            ([1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 1, 3], 6),
        ]
    final_text = """
To recap, sets are an unordered collection of unique elements. They can be created out of iterables or by manually inserting elements.
"""


class SetOperations(Page):
    class SetOperationsIntro(VerbatimStep):
        """
Sets are also useful for performing mathematical operations.

These include unions, intersections, differences and symmetric differences.

A union of two sets is a set of elements which are contained in either of the sets or in both.

For example:


__program_indented__
        """

        def program(self):
            vegetables = set(["Tomato", "Lettuce", "Cabbage", "Cucumber", "Spinach"])
            fruits = set(["Apple", "Orange", "Banana", "Kiwi", "Pineapple", "Watermelon"])

            vegetable_or_fruit = vegetables.union(fruits)
            print(vegetable_or_fruit)

    class SetIntersection(VerbatimStep):
        """
A set intersection is a set of elements contained in both initial sets.

For example:

__program_indented__
        """

        def program(self):
            multiples_of_3 = set([3, 6, 9, 12, 15, 18, 21, 24, 27, 30])
            multiples_of_2 = set([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])

            multiples_of_2_and_3 = multiples_of_2.intersection(multiples_of_3)
            print(multiples_of_2_and_3)

    class SetDifference(VerbatimStep):
        """
A set difference is a set of elements that are in one set but not in the other.

For example:

__program_indented__
        """

        def program(self):
            odd_numbers = set([1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39])
            prime_numbers = set([1,2,3,5,7,11,13,17,19,23,29,31,37])

            # Note that unlike unions or intersections, difference is not symmetric
            # The order of operands matters here
            odd_not_prime = odd_numbers.difference(prime_numbers)
            prime_not_odd = prime_numbers.difference(odd_numbers)
            print(odd_not_prime, prime_not_odd)

    class SymmetricDifference(VerbatimStep):
        """
Symmetric Difference of two sets is a set of elements that are in either set but not both.

For example:

__program_indented__
        """

        def program(self):
            odd_numbers = set([1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39])
            prime_numbers = set([1,2,3,5,7,11,13,17,19,23,29,31,37])

            not_prime_and_odd = odd_numbers.symmetric_difference(prime_numbers)
            print(not_prime_and_odd)

    class IntegerSort(ExerciseStep):
        """
Now lets use what we've learned about sets!

Print all numbers below an integer n which are divisible by 3 and 7 in numerical order.

The sorted function sorts any iterable, you will need it for your code.

Try not to use any loops or if statements.

        """
        hints = """
Remember, ranges can have more than one parameter!
You can construct sets from any iterable, including ranges.
Use the set intersection function.
        """

        def solution(self, num:int):
            threes = set(range(0, num, 3))
            sevens = set(range(0, num, 7))
            print(sorted(threes.intersection(sevens)))

        tests = [
            (100, [0, 21, 42, 63, 84]),
            (30, [0, 21]),
            (70, [0, 21, 42, 63]),
        ]


    final_text = """
Sets support mathematical operations such as unions, intersections, and differences.

These operations are useful when you want to find common phrases in two documents, or count distinct words in a text, or find all doctors who live in a given city.
    """

class LookupSpeed(Page):
    class search_time(VerbatimStep):
        """
Sets differ from lists in another important aspect.

Lookups in a set are much faster than lookups in a list and don't take longer when the size of the set increases.

The program below creates a set and a list of the same size and measures the time it takes to do a lookup of an element that is in the container and another element that is not.

Run this program:

    __copyable__
    __program_indented__

        """
        def program(self):
            import time
            for size in [256, 512, 1024]:
                # This is a list of numbers from 0 to 99
                numlist = [i for i in range(size)]
                # This is a set of the same numbers
                numset = set(numlist)

                print("Comparing a list and a set of size ", size)

                # In order to provide accurate timing, we repeat lookup operations
                # this many times
                TIMES=100000

                start = time.time_ns();
                for j in range(TIMES):
                    size-1 in numlist
                    2*size in numlist
                list_time = time.time_ns() - start
                print(f"list search: {list_time:20}")

                start = time.time_ns();
                for j in range(TIMES):
                    size-1 in numset
                    2*size in numset
                set_time = time.time_ns() - start
                print(f"set search: {set_time:21}")

                print("Speedup", int(float(list_time)/set_time), "\n")


    final_text = """
As you can see, when we double the size of the containers, the lookup time in a list nearly doubles.

But for a set, the lookup time barely increases as the set size doubles.
    """
