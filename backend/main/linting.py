import ast

from pyflakes import checker
from pyflakes.messages import UnusedVariable

MESSAGES = {
    UnusedVariable: """
**Unused variable `{0}`**

You defined a variable `{0}` but never used it. Did you forget to use it?
Maybe you used the wrong variable in its place? If you don't need it, just remove it entirely.
    """
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
        if type(message) in MESSAGES:
            message_format = MESSAGES[type(message)]
            yield message_format.format(*message.message_args)
