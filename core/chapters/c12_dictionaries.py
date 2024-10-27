# flake8: NOQA E501
import ast
import random
from collections import Counter
from typing import List, Dict

from core import translation as t
from core.exercises import assert_equal
from core.exercises import generate_string, generate_dict
from core.text import (
    ExerciseStep,
    Page,
    Step,
    VerbatimStep,
)


# Similar to word_must_be_hello
class french_must_be_dict(VerbatimStep):
    expected_code_source = "shell"

    @staticmethod
    def french():
        return t.get_code_bit('french')

    @staticmethod
    def dict_value():
        return ast.literal_eval(t.translate_code("{'apple': 'pomme', 'box': 'boite'}"))

    @classmethod
    def pre_run(cls, runner):
        runner.console.locals[cls.french()] = cls.dict_value()

    class special_messages:
        class bad_french_value:
            """
            Oops, you need to set `french = {'apple': 'pomme', 'box': 'boite'}` before we can continue.
            """
            program = 'french = {}'

    def check(self):
        if self.console.locals.get(self.french()) != self.dict_value():
            return self.special_messages.bad_french_value

        return super().check()


class IntroducingDictionaries(Page):
    class first_dict(VerbatimStep):
        """
We've seen several types: `str`, `int`, `float`, `bool`, and `list`.
Only one of these types can contain multiple values: `list`.
Now we're going to learn about another container type: `dict`, short for ***dictionary***.

Think of the familiar kind of dictionary where you look up a word to find its definition or a translation in another language.
Dictionaries in Python are similar, but more general. You look up a *key* (e.g. a word) to get the associated *value* (e.g. a definition or translation).

For example, here's a little dictionary translating English words to French:

    __program_indented__

Run the line above in the shell.
        """

        expected_code_source = "shell"

        # noinspection PyUnusedLocal
        def program(self):
            french = {'apple': 'pomme', 'box': 'boite'}

    class dict_access(french_must_be_dict):
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

    class dict_access2(french_must_be_dict):
        """
That doesn't work because the position of items in a dictionary usually doesn't matter.
You don't usually care what's the 2nd or 5th or 100th word of the dictionary,
you just want to find a specific word like 'apple'. So try that instead:

__program_indented__
        """

        program = "french['apple']"

    class dict_access3(french_must_be_dict):
        """
That's better!

Now run a similar line in the shell to look up the translation for `'box'`.
        """

        program_in_text = False

        requirements = (
            "Run the same code as the previous step (`french['apple']`) in the shell, "
            "but replace `'apple'` with `'box'`."
        )

        program = "french['box']"

    class dict_access4(french_must_be_dict):
        """
And now you know both Python and French!

Now let's translate from French to English:

__program_indented__
        """

        program = "french['pomme']"

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
    title = "Using Dictionaries in Practice"

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

        @classmethod
        def generate_inputs(cls):
            prices = generate_dict(str, int)
            cart = random.choices(list(prices), k=random.randrange(3, 20))
            return dict(prices=prices, cart=cart)

        tests = [
            ((['apple', 'box', 'cat'], {'apple': 2, 'box': 5, 'cat': 100, 'dog': 120}), 107),
            ((['apple', 'box', 'dog'], {'apple': 2, 'box': 5, 'cat': 100, 'dog': 120}), 127)
        ]

        hints = """
        Remember that `prices` is a dictionary.
        To access a value in a dictionary, you need a key.
        The keys for `prices` are the items in the `cart`.
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

        @classmethod
        def generate_inputs(cls):
            result = UsingDictionaries.shopping_cart1.generate_inputs()
            result['quantities'] = dict(Counter(result['cart']))
            result['cart'] = list(set(result['cart']))
            return result

        tests = [
            (
                {"cart": ['dog', 'box'],
                 "quantities": {'dog': 5000000, 'box': 2},
                 "prices": {'apple': 2, 'box': 5, 'cat': 100, 'dog': 100}},
                500000010
            )
        ]

        hints = """
        Remember that the keys for `prices` and `quantities` are the same.
        This is very similar to the previous exercise, we're just practicing.
        `price` should be a value from `prices`, and similarly for `quantity`.
        What key should be used to obtain each value?
        """

    class dna_part1(VerbatimStep):
        """
Not bad! But you may have noticed that it looks a bit awkward. Why do we have to specify `'dog'` and `'box'` in both the `cart` and the `quantities`?
On the next page we'll look at how to loop directly over the keys of a dictionary,
so we can get rid of the `cart` argument.

But first, let's practice what we've learned a bit more.

[Earlier in the course](#IntroducingElif) we looked at converting one strand of DNA
into a new strand with matching nucleotides.
Here's a version of that code using a function. It substitutes each letter in the input `string`
with a different one.

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
means that `'A'` should be replaced by `'T'`:

    __copyable__
    def substitute(string, d):
        ...

    original = 'AGTAGCGTCCTTAGTTACAGGATGGCTTAT'
    expected = 'TCATCGCAGGAATCAATGTCCTACCGAATA'
    assert_equal(substitute(original, {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}), expected)

This version of `substitute` should work for any arguments where all the characters in `string` are keys in `d`.
No more `if` statements needed!
        """

        def solution(self):
            def substitute(string, d):
                result = ""
                for letter in string:
                    result += d[letter]
                return result

            return substitute

        @classmethod
        def generate_inputs(cls):
            k = generate_string()
            d = {}
            for ch in k:
                d[ch] = generate_string(1)
            return {"string": k, "d": d}

        hints = """
        This is still very similar to the previous exercises, but with strings instead of numbers.
        You just have to think about the keys and values of `d`.
        You need to obtain the correct values to build up a string to return.
        You can basically replace the whole `if/elif` chain with a single line.
        That line simply needs to use `d` to get the correct value.
        Remember that the keys of `d` are the characters in `string`.
        """

        tests = [
            (
                {"string": "AGTAGCGTCCTTAGTTACAGGATGGCTTAT", "d": {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}},
                "TCATCGCAGGAATCAATGTCCTACCGAATA"
            )
        ]

    final_text = """
Nice! Here's an example of how this function can also be used to encrypt and decrypt secret messages:

    __copyable__
    __no_auto_translate__
    def substitute(string, d):
        result = ""
        for letter in string:
            result += d[letter]
        return result

    plaintext = 'helloworld'
    encrypted = 'qpeefifmez'
    letters = {'h': 'q', 'e': 'p', 'l': 'e', 'o': 'f', 'w': 'i', 'r': 'm', 'd': 'z'}
    reverse = {'q': 'h', 'p': 'e', 'e': 'l', 'f': 'o', 'i': 'w', 'm': 'r', 'z': 'd'}
    assert_equal(substitute(plaintext, letters), encrypted)
    assert_equal(substitute(encrypted, reverse), plaintext)

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
    title = "Iterating over Dictionary Keys"

    class introducing_keys(Step):
        """
Copy this code into the editor:

    __copyable__
    quantities = {'apple': 1, 'cat': 10}
    print(quantities)

Then change `print(quantities)` to `print(quantities.keys())`, and run the whole program.
        """

        requirements = "Run `print(quantities.keys())` where `quantities` is a dictionary."

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
Remove the `.keys()` and run the code again.
        """

        program_in_text = False
        requirements = (
            "Run the same code as the previous step, but without `.keys()` after `quantities`, "
            "so the middle line is `for key in quantities:`"
        )

        def program(self):
            quantities = {'apple': 1, 'cat': 10}
            for key in quantities:
                print(key)

    class cleanup_shopping_cart(ExerciseStep):
        """
Now you can use this to modify our function on the previous page to remove the `cart` argument:

    __copyable__
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
        Remember that we previously had `for item in cart` in the function, but `cart` is no longer an argument.
        Now `quantities` is the only argument that defines what the customer is buying.
        You need to iterate over the keys of `quantities` instead. Remember that 'iterate' here means 'loop over' with a `for` loop.
        You can use `.keys()`, but you don't have to.
        """

        @classmethod
        def generate_inputs(cls):
            result = UsingDictionaries.shopping_cart4.generate_inputs()
            del result["cart"]
            return result

        tests = [
            (
                ({'apple': 3, 'carrot': 4}, {'apple': 10, 'carrot': 20, 'banana': 30}),
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

    English: apple
    French: pomme
    ---
    English: box
    French: boite
    ---
        """

        hints = """
        You will need to iterate (loop) over the dictionary.
        You need to print both the key (English word) and the value (French word) of each dictionary entry.
        You can get the value using the key in the same way as always.
        """

        def solution(self):
            def print_words(french: Dict[str, str]):
                for word in french:
                    print("English: " + word)
                    print("French: " + french[word])
                    print("---")

            return print_words

        translated_tests = True

        tests = (
            (({'apple': 'pomme', 'box': 'boite'},), """\
English: apple
French: pomme
---
English: box
French: boite
---
            """),
            (({'house': 'maison', 'car': 'voiture'},), """\
English: house
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

The two dictionaries will always have the same keys, just different values.
        """

        hints = """
        This is still very similar to the previous exercise, nothing special yet.
        You can reuse your previous solution, just add another argument and a tiny bit of code inside.
        You now have to print one dictionary key and two dictionary values.
        """

        def solution(self):
            def print_words(french: Dict[str, str], german: Dict[str, str]):
                for word in french:
                    print("English: " + word)
                    print("French: " + french[word])
                    print("German: " + german[word])
                    print("---")

            return print_words

        @classmethod
        def generate_inputs(cls):
            french = generate_dict(str, str)
            german = {k: generate_string() for k in french}
            return {"french": french, "german": german}

        translated_tests = True

        tests = (
            (({'apple': 'pomme', 'box': 'boite'}, {'apple': 'apfel', 'box': 'kasten'},), """\
English: apple
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

        def program(self):
            def print_words(words):
                for word in words:
                    translations = words[word]

                    print(f"English: {word}")
                    for language in translations:
                        print(f"{language}: {translations[language]}")
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

    final_text = """
    Congratulations! You've reached the end of the course so far. More is on the way!
    """
