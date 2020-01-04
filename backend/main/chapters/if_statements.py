from main.text import Page, step


class IntroducingIfStatements(Page):
    @step("""
Now we're going to learn how to tell the computer to make decisions and only run code
under certain conditions. For this we will need a new type of value. You've seen
numbers and strings, now meet *booleans*. There are only two boolean values:
`True` and `False`. Try this program:

__program_indented__
    """, program="""
condition = True
print(condition)
condition = False
print(condition)
""")
    def introducing_booleans(self):
        return self.matches_program()

    @step("""
Booleans are meant to be used inside *if statements* (sometimes also called *conditionals*).

Here is a simple example for you to run:

__program_indented__
    """, program="""
if True:
    print('This gets printed')

if False:
    print('This does not')
""")
    def first_if_statements(self):
        return self.matches_program()

    @step("""
Note how the code inside the first `if` statement ran, but not the second.

In general, an `if` statement looks like this:

    if <condition>:
        <body>

where `<condition>` is any expression which evaluates to a boolean and `<body>` is an **indented** list
of one or more statements. The structure is quite similar to a `for` loop. Note the colon (`:`) which
is essential.

When the computer sees `if <condition>:`, it checks if `<condition>` is `True`. If it is, it runs the body.
If not, it skips it and continues to the rest of the program.

Here's a more interesting example for you to run:

__program_indented__
    """, program="""
sentence = 'Hello World'
excited = True
if excited:
    sentence += '!'
print(sentence)
    """)
    def excited_example(self):
        return self.matches_program()

    @step("""
(Remember that `sentence += '!'` means `sentence = sentence + '!'`)

Change `excited = True` to `excited = False` and run the program again to see what the difference is.
""", expected_program="""
sentence = 'Hello World'
excited = False
if excited:
    sentence += '!'
print(sentence)
    """)
    def excited_false_example(self):
        return self.matches_program()

    final_text = """TODO"""
