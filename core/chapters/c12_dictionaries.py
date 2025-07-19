# flake8: NOQA E501
import ast
import random
from collections import Counter
from copy import deepcopy
from typing import Dict, List

from core import translation as t
from core.exercises import assert_equal
from core.exercises import generate_string, generate_dict
from core.text import Page, VerbatimStep, ExerciseStep, Step
from core.utils import returns_stdout, wrap_solution


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
    # TODO


class CreatingKeyValuePairs(Page):
    title = "Creating Key-Value Pairs"

    class list_append_reminder(VerbatimStep):
        """
        Now we'll learn how to add key-value pairs to a dictionary,
        e.g. so that we can keep track of what the customer is buying.
        Before looking at dictionaries, let's remind ourselves how to add items to a list. Run this program:

            __copyable__
            __program_indented__
        """

        def program(self):
            cart = []
            cart.append('dog')
            cart.append('box')
            print(cart)

        predicted_output_choices = [
            "[]",
            "['dog']",
            "['box']",
            "['dog', 'box']",
            "['box', 'dog']",
            "['dog', 'dog']",
            "['box', 'box']",
        ]

    class list_assign_reminder(VerbatimStep):
        """
        Pretty simple. We can also change the value at an index, replacing it with a different one:

            __copyable__
            __program_indented__
        """

        def program(self):
            cart = ['dog', 'cat']
            cart[1] = 'box'
            print(cart)

        predicted_output_choices = [
            "['box']",
            "['dog', 'cat']",
            "['box', 'dog']",
            "['box', 'cat']",
            "['dog', 'box']",
            "['cat', 'box']",
            "['box', 'dog', 'cat']",
            "['dog', 'box', 'cat']",
            "['dog', 'cat', 'box']",
        ]

    class list_assign_invalid(VerbatimStep):
        """
        What if we used that idea to create our list in the first place?
        We know we want a list where `cart[0]` is `'dog'` and `cart[1]` is `'box'`, so let's just say that:

            __copyable__
            __program_indented__
        """

        def program(self):
            cart = []
            cart[0] = 'dog'
            cart[1] = 'box'
            print(cart)

        predicted_output_choices = [
            "[]",
            "['dog']",
            "['box']",
            "['dog', 'box']",
            "['box', 'dog']",
            "['dog', 'dog']",
            "['box', 'box']",
        ]

        correct_output = "Error"

    class dict_assignment_valid(VerbatimStep):
        """
        Sorry, that's not allowed. For lists, subscript assignment only works for existing valid indices.
        But that's not true for dictionaries! Try this:

            __program_indented__

        Note that `{}` means an empty dictionary, i.e. a dictionary with no key-value pairs.
        This is similar to `[]` meaning an empty list or `""` meaning an empty string.
        """
        predicted_output_choices = [
            "{'dog': 500, 'box': 2}",
            "{'dog': 2, 'box': 500}",
            "{2: 'dog', 500: 'box'}",
            "{500: 'dog', 2: 'box'}",
        ]

        def program(self):
            quantities = {}
            quantities['dog'] = 500
            quantities['box'] = 2
            print(quantities)

    class buy_quantity_exercise(ExerciseStep):
        """
        That's exactly what we need. Whether the customer says they want 500 or 5 million dogs,
        we can just put that information directly into our dictionary. So as an exercise, let's make a generic version of that.
        Write a function `buy_quantity(quantities, item, quantity)` which adds a new key-value pair to the `quantities` dictionary.
        Here's some starting code:

            __copyable__
            def buy_quantity(quantities, item, quantity):
                ...

            def test():
                quantities = {}
                buy_quantity(quantities, 'dog', 500)
                assert_equal(quantities, {'dog': 500})
                buy_quantity(quantities, 'box', 2)
                assert_equal(quantities, {'dog': 500, 'box': 2})

            test()

        Note that `buy_quantity` should *modify* the dictionary that's passed in, and doesn't need to `return` or `print` anything.
        You can assume that `item` isn't already in `quantities`.
        """
        requirements = "Your function should modify the `quantities` argument. It doesn't need to `return` or `print` anything."

        hints = """
        TODO
        """

        no_returns_stdout = True  # because the solution doesn't return anything, returning stdout would be assumed

        def solution(self):
            def buy_quantity(quantities: Dict[str, int], item: str, quantity: int):
                quantities[item] = quantity
            return buy_quantity

        @classmethod
        def wrap_solution(cls, func):
            @wrap_solution(func)
            def wrapper(**kwargs):
                quantities_name = t.get_code_bit("quantities")
                quantities = kwargs[quantities_name] = deepcopy(kwargs[quantities_name])

                func(**kwargs)
                return quantities
            return wrapper

        @classmethod
        def generate_inputs(cls):
            result = super().generate_inputs()
            result["quantities"].pop(result["item"], None)  # ensure item is not already in quantities
            return result

        tests = [
            (
                dict(
                    quantities={},
                    item='dog',
                    quantity=500
                ),
                {'dog': 500}
            ),
            (
                dict(
                    quantities={'dog': 500},
                    item='box',
                    quantity=2
                ),
                {'dog': 500, 'box': 2}
            ),
            (
                dict(
                    quantities={'apple': 3, 'banana': 5},
                    item='orange',
                    quantity=10
                ),
                {'apple': 3, 'banana': 5, 'orange': 10}
            ),
            (
                dict(
                    quantities={},
                    item='cat',
                    quantity=1
                ),
                {'cat': 1}
            ),
        ]

    class buy_quantity_input_test(VerbatimStep):
        """
        Well done! Try it out interactively:

            __copyable__
            __program_indented__

        Note the `int(input())` part, because `input()` returns a string, and `quantity` should be an integer
        (a whole number). This'll break if you enter something that isn't a number, but that's OK for now.
        """

        stdin_input = ["apple", "3", "banana", "5", "cat", "2"]

        def program(self):
            def buy_quantity(quantities, item, quantity):
                quantities[item] = quantity

            def test():
                quantities = {}
                for _ in range(3):
                    print('What would you like to buy?')
                    item = input()

                    print('How many?')
                    quantity = int(input())

                    buy_quantity(quantities, item, quantity)

                    print("OK, here's your cart so far:")
                    print(quantities)

            test()

    class total_cost_per_item_exercise(ExerciseStep):
        """
        Thanks for shopping with us! Let's see how much you just spent on each item.

        Earlier we defined a function `total_cost(quantities, prices)` which returned a single number
        with a grand total of all the items in the cart. Now let's make a function `total_cost_per_item(quantities, prices)`
        which returns a new dictionary with the total cost for each item:

            __copyable__
            def total_cost_per_item(quantities, prices):
                totals = {}
                for item in quantities:
                    ___ = quantities[item] * prices[item]
                return totals

            assert_equal(
                total_cost_per_item({'apple': 2}, {'apple': 3, 'box': 5}),
                {'apple': 6},
            )

            assert_equal(
                total_cost_per_item({'dog': 500, 'box': 2}, {'dog': 100, 'box': 5}),
                {'dog': 50000, 'box': 10},
            )
        """
        hints = """
        You need to iterate through the items in the `quantities` dictionary.
        For each `item`, calculate the total cost for that item (quantity * price).
        Store this calculated cost in the `totals` dictionary.
        The key for the `totals` dictionary should be the `item` name.
        Use the dictionary assignment syntax: `totals[item] = calculated_cost`.
        Make sure this assignment happens *inside* the loop.
        The function should return the `totals` dictionary after the loop finishes.
        """

        def solution(self):
            def total_cost_per_item(quantities: Dict[str, int], prices: Dict[str, int]):
                totals = {}
                for item in quantities:
                    totals[item] = quantities[item] * prices[item]
                return totals
            return total_cost_per_item

        tests = [
            (({'apple': 2}, {'apple': 3, 'box': 5}), {'apple': 6}),
            (({'dog': 500, 'box': 2}, {'dog': 100, 'box': 5}), {'dog': 50000, 'box': 10}),
            (({'pen': 5, 'pencil': 10}, {'pen': 1, 'pencil': 0.5, 'eraser': 2}), {'pen': 5, 'pencil': 5.0}),
            (({}, {'apple': 1}), {}),
        ]

        @classmethod
        def generate_inputs(cls):
            prices = generate_dict(str, int)
            quantities = {k: random.randint(1, 10) for k in prices if random.choice([True, False])}
            return {"quantities": quantities, "prices": prices}

    class make_english_to_german_exercise(ExerciseStep):
        """
        Perfect! This is like having a nice receipt full of useful information.

        Let's come back to the example of using dictionaries for translation. Suppose we have one dictionary
        for translating from English to French, and another for translating from French to German.
        Let's use that to create a dictionary that translates from English to German:

            __copyable__
            def make_english_to_german(english_to_french, french_to_german):
                ...

            assert_equal(
                make_english_to_german(
                    {'apple': 'pomme', 'box': 'boite'},
                    {'pomme': 'apfel', 'boite': 'kasten'},
                ),
                {'apple': 'apfel', 'box': 'kasten'},
            )
        """
        parsons_solution = True

        hints = """
        You need to create a new empty dictionary, let's call it `english_to_german`.
        Iterate through the keys (English words) of the `english_to_french` dictionary.
        Inside the loop, for each `english` word:
          1. Find the corresponding French word using `english_to_french`.
          2. Use that French word as a key to find the German word in `french_to_german`.
          3. Add the `english` word as a key and the `german` word as the value to your new `english_to_german` dictionary.
        After the loop, return the `english_to_german` dictionary.
        """

        def solution(self):
            def make_english_to_german(english_to_french: Dict[str, str], french_to_german: Dict[str, str]):
                english_to_german = {}
                for english in english_to_french:
                    french = english_to_french[english]
                    german = french_to_german[french]
                    english_to_german[english] = german
                return english_to_german
            return make_english_to_german

        tests = [
            (({'apple': 'pomme', 'box': 'boite'}, {'pomme': 'apfel', 'boite': 'kasten'}),
             {'apple': 'apfel', 'box': 'kasten'}),
            (({'one': 'un', 'two': 'deux', 'three': 'trois'}, {'un': 'eins', 'deux': 'zwei', 'trois': 'drei'}),
             {'one': 'eins', 'two': 'zwei', 'three': 'drei'}),
            (({}, {}), {}),
        ]

        @classmethod
        def generate_inputs(cls):
            english_to_french = generate_dict(str, str)
            french_to_german = {v: generate_string() for v in english_to_french.values()}
            return {"english_to_french": english_to_french, "french_to_german": french_to_german}

    class swap_keys_values_exercise(ExerciseStep):
        """
        Great job!

        Of course, language isn't so simple, and there are many ways that using a dictionary like this could go wrong.
        So...let's do something even worse! Write a function which takes a dictionary and swaps the keys and values,
        so `a: b` becomes `b: a`.

            __copyable__
            def swap_keys_values(d):
                ...

            assert_equal(
                swap_keys_values({'apple': 'pomme', 'box': 'boite'}),
                {'pomme': 'apple', 'boite': 'box'},
            )
        """
        hints = """
        Create a new empty dictionary to store the result.
        Iterate through the keys of the input dictionary `d`.
        Inside the loop, for each `key`:
          1. Get the corresponding `value` from `d`.
          2. Add an entry to the new dictionary where the *key* is the original `value` and the *value* is the original `key`.
        Return the new dictionary after the loop.
        """

        def solution(self):
            def swap_keys_values(d: Dict[str, str]):
                new_dict = {}
                for key in d:
                    value = d[key]
                    new_dict[value] = key
                return new_dict
            return swap_keys_values

        tests = [
            (({'apple': 'pomme', 'box': 'boite'},), {'pomme': 'apple', 'boite': 'box'}),
            (({'a': 1, 'b': 2},), {1: 'a', 2: 'b'}),
            (({10: 'x', 20: 'y'},), {'x': 10, 'y': 20}),
            (({},), {}),
        ]

    final_text = """
Magnificent!

Jokes aside, it's important to remember how exactly this can go wrong. Just like multiple items in the store
can have the same price, multiple words in English can have the same translation in French. If the original dictionary
has duplicate *values*, what happens when you try to swap keys and values? Since dictionary keys must be unique,
some data will be lost.

But there are many situations where you can be sure that the values in a dictionary *are* unique and that this
'inversion' makes sense. For example, we saw this code [earlier in the chapter](#UsingDictionaries):

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

Now we can construct the `reverse` dictionary automatically:

    reverse = swap_keys_values(letters)

For this to work, we just have to make sure that all the values in `letters` are unique.
Otherwise it would be impossible to decrypt messages properly. If both `'h'` and `'j'` got replaced with `'q'`
during encryption, there would be no way to know whether `'qpeef'` means `'hello'` or `'jello'`!
"""


class CopyingDictionaries(Page):
    title = "Copying Dictionaries"

    class shared_references(VerbatimStep):
        """
        Remember how assigning one list variable to another (`list2 = list1`) made both names point to the *same* list? Dictionaries work the same way because they are also *mutable* (can be changed).

        Predict what the following code will print, then run it to see:

            __copyable__
            __program_indented__
        """
        def program(self):
            d1 = {'a': 1, 'b': 2}
            d2 = d1

            print("d1 before:", d1)
            print("d2 before:", d2)
            print("Are they the same object?", d1 is d2)

            d2['c'] = 3 # Modify via d2

            print("d1 after:", d1) # Is d1 affected?
            print("d2 after:", d2)

        predicted_output_choices = [
            # Incorrect prediction (d1 unaffected)
            """d1 before: {'a': 1, 'b': 2}
d2 before: {'a': 1, 'b': 2}
Are they the same object? True
d1 after: {'a': 1, 'b': 2}
d2 after: {'a': 1, 'b': 2, 'c': 3}""",

            # Correct prediction
            """d1 before: {'a': 1, 'b': 2}
d2 before: {'a': 1, 'b': 2}
Are they the same object? True
d1 after: {'a': 1, 'b': 2, 'c': 3}
d2 after: {'a': 1, 'b': 2, 'c': 3}""",

            # Incorrect prediction (is False)
            """d1 before: {'a': 1, 'b': 2}
d2 before: {'a': 1, 'b': 2}
Are they the same object? False
d1 after: {'a': 1, 'b': 2}
d2 after: {'a': 1, 'b': 2, 'c': 3}""",
        ]

    class making_copies(VerbatimStep):
        """
        Because `d1` and `d2` referred to the exact same dictionary object (`d1 is d2` was `True`), changing it via `d2` also changed what `d1` saw.

        To get a *separate* dictionary with the same contents, use the `.copy()` method.

        Predict how using `.copy()` changes the outcome, then run this code:

            __copyable__
            __program_indented__
        """
        def program(self):
            d1 = {'a': 1, 'b': 2}
            d2 = d1.copy() # Create a separate copy

            print("d1 before:", d1)
            print("d2 before:", d2)
            print("Are they the same object?", d1 is d2)

            d2['c'] = 3 # Modify the copy

            print("d1 after:", d1) # Is d1 affected now?
            print("d2 after:", d2)

        predicted_output_choices = [
            # Incorrect prediction (is True)
            """d1 before: {'a': 1, 'b': 2}
d2 before: {'a': 1, 'b': 2}
Are they the same object? True
d1 after: {'a': 1, 'b': 2, 'c': 3}
d2 after: {'a': 1, 'b': 2, 'c': 3}""",

            # Incorrect prediction (d1 affected)
            """d1 before: {'a': 1, 'b': 2}
d2 before: {'a': 1, 'b': 2}
Are they the same object? False
d1 after: {'a': 1, 'b': 2, 'c': 3}
d2 after: {'a': 1, 'b': 2, 'c': 3}""",

            # Correct prediction
            """d1 before: {'a': 1, 'b': 2}
d2 before: {'a': 1, 'b': 2}
Are they the same object? False
d1 after: {'a': 1, 'b': 2}
d2 after: {'a': 1, 'b': 2, 'c': 3}""",
        ]

    class positive_stock_exercise(ExerciseStep):
        """
        Making an exact copy is useful, but often we want a *modified* copy. Let's practice creating a new dictionary based on an old one.

        Write a function `positive_stock(stock)` that takes a dictionary `stock` (mapping item names to integer quantities) and returns a *new* dictionary containing only the items from the original `stock` where the quantity is strictly greater than 0. The original `stock` dictionary should not be changed.

            __copyable__
            def positive_stock(stock):
                # Your code here
                ...

            assert_equal(
                positive_stock({'apple': 10, 'banana': 0, 'pear': 5, 'orange': 0}),
                {'apple': 10, 'pear': 5}
            )
            assert_equal(
                positive_stock({'pen': 0, 'pencil': 0}),
                {}
            )
            assert_equal(
                positive_stock({'book': 1, 'paper': 5}),
                {'book': 1, 'paper': 5}
            )
        """
        hints = """
        Start by creating a new empty dictionary, e.g., `result = {}`.
        Loop through the keys of the input `stock` dictionary.
        Inside the loop, get the `quantity` for the current `item` using `stock[item]`.
        Use an `if` statement to check if `quantity > 0`.
        If the quantity is positive, add the `item` and its `quantity` to your `result` dictionary using `result[item] = quantity`.
        After the loop finishes, return the `result` dictionary.
        Make sure you don't modify the original `stock` dictionary passed into the function. Creating a new `result` dictionary ensures this.
        """

        def solution(self):
            def positive_stock(stock: Dict[str, int]):
                result = {}
                for item in stock:
                    quantity = stock[item]
                    if quantity > 0:
                        result[item] = quantity
                return result
            return positive_stock

        tests = [
            (({'apple': 10, 'banana': 0, 'pear': 5, 'orange': 0},), {'apple': 10, 'pear': 5}),
            (({'pen': 0, 'pencil': 0},), {}),
            (({'book': 1, 'paper': 5},), {'book': 1, 'paper': 5}),
            (({},), {}),  # Empty input
            (({'gadget': -5, 'widget': 3},), {'widget': 3}),  # Negative values
        ]

        @classmethod
        def generate_inputs(cls):
            # Generate a dictionary with some zero/negative and positive values
            stock = {}
            num_items = random.randint(3, 8)
            for _ in range(num_items):
                item = generate_string(random.randint(3, 6))
                # Ensure some variety in quantities
                if random.random() < 0.4:
                    quantity = 0
                elif random.random() < 0.2:
                     quantity = random.randint(-5, -1)
                else:
                    quantity = random.randint(1, 20)
                stock[item] = quantity
            # Ensure at least one positive if dict not empty
            if stock and all(q <= 0 for q in stock.values()):
                 stock[generate_string(4)] = random.randint(1, 10)
            return {"stock": stock}

    class add_item_exercise(ExerciseStep):
        """
        Let's practice combining copying and modifying. Imagine we want to represent adding one unit of an item to our stock count.

        Write a function `add_item(item, quantities)` that takes an item name (`item`) and a dictionary `quantities`. You can assume the `item` *already exists* as a key in the `quantities` dictionary.

        The function should return a *new* dictionary which is a copy of `quantities`, but with the value associated with `item` increased by 1. The original `quantities` dictionary should not be changed.

            __copyable__
            def add_item(item, quantities):
                # Your code here
                ...

            stock = {'apple': 5, 'banana': 2}
            new_stock = add_item('apple', stock)
            assert_equal(stock, {'apple': 5, 'banana': 2}) # Original unchanged
            assert_equal(new_stock, {'apple': 6, 'banana': 2}) # Copy has incremented value

            new_stock_2 = add_item('banana', new_stock)
            assert_equal(new_stock, {'apple': 6, 'banana': 2}) # Previous copy unchanged
            assert_equal(new_stock_2, {'apple': 6, 'banana': 3}) # New copy incremented
        """
        hints = """
        First, create a *copy* of the input `quantities` dictionary using the `.copy()` method. Store this in a new variable, e.g., `new_quantities`.
        Since we assume `item` is already a key, you don't need to check for its existence in this exercise.
        Find the current quantity of the `item` in the `new_quantities` copy using `new_quantities[item]`.
        Calculate the new quantity by adding 1 to the current quantity.
        Update the value for `item` in the `new_quantities` copy with this new quantity using assignment: `new_quantities[item] = ...`.
        Return the `new_quantities` dictionary.
        """

        def solution(self):
            def add_item(item: str, quantities: Dict[str, int]):
                new_quantities = quantities.copy()
                new_quantities[item] = new_quantities[item] + 1
                return new_quantities
            return add_item

        tests = [
            (('apple', {'apple': 5, 'banana': 2}), {'apple': 6, 'banana': 2}),
            (('banana', {'apple': 6, 'banana': 2}), {'apple': 6, 'banana': 3}),
            (('pen', {'pen': 1}), {'pen': 2}),
            (('a', {'a': 0, 'b': 99}), {'a': 1, 'b': 99}),
        ]

        @classmethod
        def generate_inputs(cls):
            quantities = generate_dict(str, int)
            # Ensure the dictionary is not empty
            if not quantities:
                quantities[generate_string(4)] = random.randint(0, 10)
            # Pick an existing item to increment
            item = random.choice(list(quantities.keys()))
            return {"item": item, "quantities": quantities}

        final_text = """
        Well done! Notice that the line where you increment the value:

            new_quantities[item] = new_quantities[item] + 1

        can also be written more concisely using the `+=` operator, just like with numbers:

            new_quantities[item] += 1

        This does the same thing: it reads the current value, adds 1, and assigns the result back.
        """

    final_text = """
    Great! You now know why copying dictionaries is important (because they are mutable) and how to do it using `.copy()`. You've also practiced creating modified copies, which is a common and safe way to work with data without accidentally changing things elsewhere in your program.

    Next, we'll see how to check if a key exists *before* trying to use it, to avoid errors.
    """
