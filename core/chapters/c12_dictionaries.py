# flake8: NOQA E501
import ast
import random
from textwrap import dedent
from typing import List, Dict, Mapping

import sys

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


class IntroducingDictionaries(Page):
    class first_dict(VerbatimStep):
        """
We've seen several types: `str`, `int`, `float`, `bool`, and `list`.
Only one of these types can contain multiple values: `list`.
Now we're going to learn about another container type: `dict`, short for ***dictionary***.

Think of the familiar kind of dictionary where you look up a word to find its definition or a translation in another language.
Dictionaries in Python are similar, but more general. You look up a *key* (e.g. a word) to get the associated *value* (e.g. a definition or translation).

For example, here's a little dictionary translating English words to French:
Run the line below in the shell.

    __program_indented__
        """

        def program(self):
            french = {'apple':'pomme', 'box': 'boite'}

    class dict_access(VerbatimStep):
        """
`french` is a dictionary with two key-value pairs:

- `'apple': 'pomme'` where `'apple'` is the key and `'pomme'` is the value.
- `'box': 'boite'` where `'box'` is the key and `'boite'` is the value.

Like lists, a comma (`,`) is used to separate items (key-value pairs) from each other. A colon (`:`) separates the keys from the values.
Note that curly brackets (`{}`) are used to create the dictionary instead of the square brackets (`[]`) used when writing lists.

Remember that with lists, you get values based on their *index*, i.e. their position in the list.
So if `words = ['apple', 'box']`, then `words[0]` is `'apple'` and `words[1]` is `'box'`.
Try this in the shell:

__program_indented__
        """

        program = "french[0]"


    class dict_access2(VerbatimStep):
        """
That doesn't work because the position of items in a dictionary usually doesn't matter.

You don't usually care what's the 2nd or 5th or 100th word of the dictionary,
you just want to find a specific word like 'apple'. So try that instead:

__program_indented__
        """

        auto_translate_program = False

        program = "french['apple']"

        def check(self):
            return "pomme" in self.result

    class dict_access3(VerbatimStep):
        """
That's better!

Now run a similar line in the shell to look up the translation for 'box'.


        """

        auto_translate_program = False
        program_in_text = False

        program = "french['box']"

        def check(self):
            return "boite" in self.result

    class dict_access4(VerbatimStep):
        """
And now you know both Python and French!

Now let's translate from French to English:

__program_indented__
        """

        auto_translate_program = False

        program = "french['pomme']"

        def check(self):
            return "KeyError" in self.result

    final_text = """
Sorry, you can't do that either. You can only look up a key to get its value, not the other way around.

The dictionary `french` only has 2 keys: `'apple'` and `'box'`. `'pomme'` is a value, not a key.

We'll soon learn why you can't just look up values directly, and what you can do about it.


Note that both `french[0]` and `french['pomme']` raised the same type of error: a `KeyError`.

This error means that the provided key (`0` or `'pomme'` in this case) wasn't found in the dictionary.

It's not that `french[0]` isn't *allowed*, it's just that it means the same thing as always:
find the value associated with the key `0`. In this case it finds that no such key exists.

But `0` *could* be a key, because many types of keys are allowed, including strings and numbers.
"""


class UsingDictionaries(Page):
    class shopping_cart1(ExerciseStep):
        """
Let's see dictionaries in a real life problem. Imagine you're building an online shopping website.

You keep the prices of all your items in a dictionary:

    prices = {'apple': 2, 'box': 5, 'cat': 100, 'dog': 100}

Here you can see one reason why looking up values in a dictionary could be a problem.

What would `prices[100]` be? `'dog'`? `'cat'`? `['dog', 'cat']`?

The same value can be repeated any number of times in a dictionary.

On the other hand, keys have to be unique. Imagine if your prices started like this:

    prices = {'apple': 2, 'apple': 3}


How much does an apple cost? We know it's `prices['apple']`, but is that `2` or `3`?

Clearly there should only be one price, so duplicate keys aren't allowed.


Anyway, this is a normal shop where things have one price.

This normal shop has normal customers with normal shopping lists like `['apple', 'box', 'cat']`.

And even though your customers have calculators in their pockets, they still expect you to add up all the prices
yourself and tell them how much this will all cost, because that's what normal shops do.

So let's write a function that does that. Complete the function below, particularly the line `price = ...`


    __copyable__


    def total_cost(cart, prices):
        result = 0
        for item in cart:
            price = ...
            result += price
        return result

    assert_equal(
        total_cost(
            ['apple', 'box', 'cat'],
            {'apple': 2, 'box': 5, 'cat': 100, 'dog': 100},
            ),
        107,
    )
        """ 

        def solution(self):
            def total_cost(cart: List[str], prices: Dict[str, int]):
                result = 0
                for item in cart:
                    price = prices[item]
                    result += price
                return result

            return total_cost

        def generate_inputs():
            k1 = generate_string()
            k2 = generate_string()
            return {'cart': [k1, k2],
                    'prices': {k1 : random.randrange(100), k2 : random.randrange(100)}}

        tests = [
            ((['apple', 'box', 'cat'],  {'apple': 2, 'box': 5, 'cat': 100, 'dog': 120}), 107),
            ((['apple', 'box', 'dog'],  {'apple': 2, 'box': 5, 'cat': 100, 'dog': 120}), 127)
        ]

        hints = """
        Remember that prices is a dictionary.
        To access a value in a dictionary, you need a key.
        The keys for prices are the items in the cart.
        """

    class shopping_cart4(ExerciseStep):
        """
Perfect! You publish your website and start dreaming about how rich you're going to be.

But soon you get a complaint from a customer who wants to buy 5 million dogs...and 2 boxes to put them in.

Your website allows buying the same items several times, e.g. `total_cost(['box', 'box'], {...})` works,
but they have to add each item one at a time, and for some reason this customer doesn't want to click
'Add to Cart' 5 million times. People are so lazy!

Here's the new code for you to fix:

    __copyable__


    def total_cost(cart, quantities, prices):
        result = 0
        for item in cart:
            price = ...
            quantity = ...
            result += price * quantity
        return result

    assert_equal(
        total_cost(
            ['dog', 'box'],
            {'dog': 5000000, 'box': 2},
            {'apple': 2, 'box': 5, 'cat': 100, 'dog': 100},
        ),
        500000010,
    )

We've added another parameter called `quantities` to `total_cost`.
Now `cart` is still a list of strings, but it doesn't have any duplicates.
`quantities` is a dictionary where the keys are the items in `cart` and the corresponding values are the quantity
of that item that the customer wants to buy.

        """
        def solution(self):
            def total_cost(cart, quantities, prices):
                result = 0
                for item in cart:
                    price = prices[item]
                    quantity = quantities[item]
                    result += price * quantity
                return result
            return total_cost

        def generate_inputs():
            k1 = generate_string()
            k2 = generate_string()
            return {"cart" : [k1, k2],
                    "quantities" : {k1 : random.randrange(100), k2 : random.randrange(100)},
                    "prices" : {k1 : random.randrange(100), k2 : random.randrange(100)}}

        tests = [
            (
                {"cart" : ['dog', 'box'],
                 "quantities" : {'dog': 5000000, 'box': 2},
                 "prices" : {'apple': 2, 'box': 5, 'cat': 100, 'dog': 100}},
                500000010
             )
        ]

        hints = """
        Remember that the keys for prices and quantities are the same.
        Access the two dictionaries using item as the key.
        """

    class shopping_cart5(VerbatimStep):
        """



Not bad! But you may have noticed that it looks a bit awkward. Why do we have to specify `'dog'` and `'box'` in both the `cart` and the `quantities`?

On the next page we'll look at how to loop directly over the keys of a dictionary,
so we can get rid of the `cart` argument.


But first, let's practice what we've learned a bit more.

[Earlier in the course](#IntroducingElif) we looked at converting one strand of DNA
into a new strand with matching nucleotides:

    __copyable__
    __program_indented__
        """

        def program(self):
            def substitute(string):
                result = ''
                for char in string:
                    if char == 'A':
                        char = 'T'
                    elif char == 'T':
                        char = 'A'
                    elif char == 'G':
                        char = 'C'
                    elif char == 'C':
                        char = 'G'
                    result += char
                return result

            original = 'AGTAGCGTCCTTAGTTACAGGATGGCTTAT'
            expected = 'TCATCGCAGGAATCAATGTCCTACCGAATA'
            assert_equal(substitute(original), expected)


    class dna_part2(ExerciseStep):
        """
Now we can use dictionaries to make this code both shorter and more general so it can be used for other purposes.

Your job is to add another argument to the `substitute` function: a dictionary called `d`.

The keys of `d` represent characters
in the first argument `string` that should be replaced by the corresponding values of `d`. For example, `'A': 'T'`
means that `A` should be replaced by `T`.
        """

        def solution(self):
            def substitute(string, d):
                result = ""
                for letter in string:
                    result += d[letter]
                return result

            return substitute

        def generate_inputs():
            k = generate_string()
            d = {}
            for ch in k:
                d[ch] = generate_string(1)
            return {"string" : k, "d" : d}

        hints = """
        Remember that the key for the dictionary is the character in the string.
        The value from the dictionary is the replacement for the key.
        """

        tests = [
            (
                {"string" : "AGTAGCGTCCTTAGTTACAGGATGGCTTAT", "d" : {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}},
                "TCATCGCAGGAATCAATGTCCTACCGAATA"
            )
        ]


    class cryptography(VerbatimStep):
        """
Nice! Here's an example of how this function can also be used to encrypt and decrypt secret messages:

    __copyable__
    __program_indented__
        """

        def program(self):
            plaintext = 'helloworld'
            encrypted = 'qpeefifmez'
            letters = {'h': 'q', 'e': 'p', 'l': 'e', 'o': 'f', 'w': 'i', 'r': 'm', 'd': 'z'}
            reverse = {'q': 'h', 'p': 'e', 'e': 'l', 'f': 'o', 'i': 'w', 'm': 'r', 'z': 'd'}
            assert_equal(substitute(plaintext, letters), encrypted)
            assert_equal(substitute(encrypted, reverse), plaintext)


    final_text = """
The same function works in both directions, we just need to pass it different dictionaries.

The two dictionaries are almost the same, we just swap around the key and value in each pair.
So to encrypt, we replace `e` with `p`, and to decrypt we change `p` back to `e`.

Note that `'e'` is both a key and a value in `letters`.

Looking up `letters['e']` means that we're asking about `'e'` as a *key*, so it gives `'p'`.
Remember, we can't use `letters` to ask which key is associated with `'e'` as a *value*.
But in this case we can use the other dictionary for that: `reverse['e']` gives `'l'`,
and `letters['l']` gives `'e'` again.

Soon you'll write a function to create a dictionary like `reverse` automatically,
i.e. `reverse = swap_keys_values(letters)`."""

class DictionaryKeysAndValues(Page):
    class introducing_keys(Step):
        """
Copy this code into the editor, then change `print(quantities)` to `print(quantities.keys())`, and run the whole program.

    __copyable__

    quantities = {'apple': 1, 'cat': 10}
    print(quantities)


        """

        program = """
        quantities = {'apple': 1, 'cat': 10}
        print(quantities.keys())
        """

        def check(self):
            return "dict_keys([" in self.result


    class keys_are_iterable(VerbatimStep):
        """
The `.keys()` method of `dict` does basically what you'd expect. You can iterate over the value it returns
just like you'd iterate over a list:

    __copyable__
    __program_indented__
        """

        def program(self):
            quantities = {'apple': 1, 'cat': 10}
            for key in quantities.keys():
                print(key)

    class keys_are_iterable2(VerbatimStep):
        """
Actually, you don't even need `.keys()`. Iterating directly over a dictionary automatically iterates over its keys.
Sometimes it's nice to write `.keys()` to make your code more readable, but you don't have to.
Run this code.

    __program_indented__
        """

        def program(self):
            quantities = {'apple': 1, 'cat': 10}
            for key in quantities:
                print(key)


        #def check(self):
        #    return "apple\ncat" in self.result

    class cleanup_shopping_cart(ExerciseStep):
        """
Now you can use this to modify our function on the previous page to remove the `cart` argument:

    __copyable__
    __no_auto_translate__

    def total_cost(quantities, prices):
        result = 0
        for item in ...:
            price = prices[item]
            quantity = quantities[item]
            result += price * quantity
        return result

    assert_equal(
        total_cost(
            {'dog': 5000000, 'box': 2},
            {'apple': 2, 'box': 5, 'cat': 100, 'dog': 100},
        ),
        500000010,
    )
        """

        def solution(self):
            def total_cost(quantities: Dict[str, int], prices: Dict[str, int]):
                result = 0
                for item in quantities:
                    price = prices[item]
                    quantity = quantities[item]
                    result += price * quantity
                return result

            return total_cost

        hints = """
        You don't need .keys() to iterate over the keys to a dictionary.
        Try iterating over the dictionary 'quantities' itself.
        """

        # Custom generate inputs is required because cart and prices must have the same keys.
        def generate_inputs():
            k1 = generate_string()
            k2 = generate_string()
            return {'quantities': {k1 : random.randrange(100), k2 : random.randrange(100)},
                    'prices': {k1 : random.randrange(100), k2 : random.randrange(100), generate_string() : random.randrange(100)}}

        tests = [
          (
                ({'apple' : 3, 'carrot' : 4}, {'apple' : 10, 'carrot' : 20}),
                110
           )
        ]

    class english_to_french(ExerciseStep):
        """
That looks nice! We've fully solved the problem of adding up the total cost.

Coming back to our first example: write a function
which prints out each word in an English-to-French dictionary and its translation, labeling them with their languages.
Here's your starting code:

    __copyable__
    def print_words(french):
        ...

    print_words({'apple': 'pomme', 'box': 'boite'})


For example, the last line of code above should print:

    __no_auto_translate__
    English: apple
    French: pomme
    ---
    English: box
    French: boite
    ---
        """

        hints = """
        Iterate over the dictionary.
        Remember that the english words are the keys.
        """


        def solution(self):
            def print_words(french:Dict[str, str]):
                for word in french:
                    print("English: " + word)
                    print("French: " + french[word])
                    print("---")

            return print_words

        tests = (
            (({'apple': 'pomme', 'box': 'boite'},), """English: apple
French: pomme
---
English: box
French: boite
---
            """),
            (({'house': 'maison', 'car': 'voiture'},), """English: house
French: maison
---
English: car
French: voiture
---
            """),
            )


    class english_to_german(ExerciseStep):
        """
Great! Now let's add a German dictionary as well:

    __copyable__

    def print_words(french, german):
        ...

    print_words(
        {'apple': 'pomme', 'box': 'boite'},
        {'apple': 'apfel', 'box': 'kasten'},
    )

That should print:

    English: apple
    French: pomme
    German: apfel
    ---
    English: box
    French: boite
    German: kasten
    ---
        """

        hints = """
The dictionaries will be the same length.
The keys are the same across both dictionaries.
        """

        def solution(self):
            def print_words(french:Dict[str, str], german:Dict[str, str]):
                for word in french:
                    print("English: " + word)
                    print("French: " + french[word])
                    print("German: " + german[word])
                    print("---")

            return print_words

        # Custom generate_dicts is required here because French and German dicts must have same English word as the key.
        def generate_inputs():
            k1 = generate_string()
            k2 = generate_string()
            return {'french': {k1 : generate_string(), k2 : generate_string()},
                    'german': {k1 : generate_string(), k2 : generate_string()}}


        tests = (
            (({'apple' : 'pomme', 'box' : 'boite'}, {'apple' : 'apfel', 'box' : 'kasten'},), """English: apple
French: pomme
German: apfel
---
English: box
French: boite
German: kasten
---
            """),
        )

    class nested_dictionaries(VerbatimStep):
        """
Beautiful! There's a pattern emerging here. The two languages could be merged into one big nested dictionary:

    __copyable__
    __program_indented__
        """

        program = """
        def print_words(words):
            for word in words:
                languages = words[word]

                print(f"English: {word}")
                print(f"French: {languages['French']}")
                print(f"German: {languages['German']}")
                print(f"---")


        print_words({
            'apple': {
                'French': 'pomme',
                'German': 'apfel',
            },
            'box': {
                'French': 'boite',
                'German': 'kasten',
            },
        })
        """

    final_text = """
    Congratulations! You've completed the dictionaries chapters.

    As you have seen, dictionaries are a powerful tool for organizing and accessing data.
    """
