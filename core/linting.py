import ast

from pyflakes import checker
from pyflakes.messages import UnusedImport, UnusedVariable, IsLiteral, RedefinedWhileUnused, ImportShadowedByLoopVar, \
    ImportStarNotPermitted, MultiValueRepeatedKeyLiteral

from core import translation as t

MESSAGES = {
    UnusedImport: """
**Unused import `{0}`**

You imported `{0}` but never used it. Did you forget to use it?
Maybe you used the wrong variable in its place? If you don't need the import, just remove it entirely.
    """,
    UnusedVariable: """
**Unused variable `{0}`**

You defined a variable `{0}` but never used it. Did you forget to use it?
Maybe you used the wrong variable in its place? If you don't need it, just remove it entirely.
    """,
    IsLiteral: """
**`is` comparison with literal**

You used the `is`/`is not` operator to compare with a literal (e.g. a string or number).
You should have rather used the `==` / `!=` operator.

The `is` operator checks if two expressions refer to the exact same object.
You rarely want to use them, certainly not for basic data types like strings and numbers.
In those cases they will seem to work sometimes (e.g. for small numbers) and mysteriously
fail on other occasions.
    """,

    RedefinedWhileUnused: """
**Redefined `{0}` without using it**

You defined `{0}` on line `{1}`, but before ever using it you redefined it,
overwriting the original definition.

In general your functions and classes should have different names.
Check that you use everything you define, e.g. that you called your functions.
    """,
    ImportShadowedByLoopVar: """
**Import `{0}` shadowed by loop variable**

The name of the loop variable `{0}` should be changed as it redefines the `{0}` module imported earlier.
Choose a different loop variable to avoid this error.
""",
    ImportStarNotPermitted: """
**Import made using `*` **

`from {0} import *` imports everything from the module `{0}` into the current namespace.
This creates a bunch of invisible unknown variables.
It makes it hard to read and understand code and see where things come from.

Avoid this kind of import and instead explicitly import exactly the names you need.
""",

    MultiValueRepeatedKeyLiteral: """
**Dictionary key `{0}` repeated with different values**

A dictionary cannot have multiple entries for the same key.
Check your code again and change the repeated key to something unique.
""",

}


def lint(tree):
    # Wrap the whole module in a function
    # so that pyflakes thinks global variables are local variables
    # and reports when they are unused
    function_tree = ast.parse("def f(): 0")
    function_tree.body[0].body = tree.body

    ch = checker.Checker(function_tree, builtins=["assert_equal"])
    ch.messages.sort(key=lambda m: m.lineno)
    for message in ch.messages:
        cls = type(message)
        if cls in MESSAGES:
            message_format = t.get(t.pyflakes_message(cls), MESSAGES[cls])
            yield message_format.format(*message.message_args)

# to do at later stage: ReturnWithArgsInsideGenerator, AssertTuple
