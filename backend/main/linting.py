import ast
from pyflakes import checker
from pyflakes.messages import UnusedImport, UnusedVariable, IsLiteral, RedefinedWhileUnused, ImportShadowedByLoopVar, \
    ImportStarUsed, ImportStarUsage, ImportStarNotPermitted, DuplicateArgument, MultiValueRepeatedKeyLiteral

MESSAGES = {
    UnusedImport: """
**Unused import `{0}`**
You imported a module `{0}` but never used it. Did you forget to use it?
Maybe you used the wrong import in its place? If you don't need it, just remove it entirely.
    """,
    UnusedVariable: """
**Unused variable `{0}`**
You defined a variable `{0}` but never used it. Did you forget to use it?
Maybe you used the wrong variable in its place? If you don't need it, just remove it entirely.
    """,
    IsLiteral: """
**Is literal**
You used the is/is not statement for comparison. You should have rather used the `==` / `!=` statements,
which are used to compare constant literals (str, bytes, int, float, tuple)- referring to equality. 
The is/is not statement checks if objects refer to the same instance (address in memory).
    """,

    RedefinedWhileUnused: """
**Redefined `{0}` while unused on line `{1}`**
This error occurs when a function, class or method is redefined.
The function `{0}` has not been called however it has been redefined on line `{1}`
Make sure that all functions have different names if they are different. Also remember to call the function.
    """,
    ImportShadowedByLoopVar: """
**Import `{0}` from line '{1}` shadowed by loop variable**
The name of the loop variable `{0}` should be changed in line`{1}` as it redefines the `{0}` module.
Choose a different loop variable to avoid this error.
""",
    ImportStarUsed: """

**Import made using * **
This * import is used to import everything from a designated module under the current 
module, allowing the use of various objects from the imported module- without having to prefix them with the module's 
name. Refrain from using this type of import statement and rather explicitly import a few statements that you may 
require instead.  
""",
    ImportStarUsage: """

**Import made using * **
This * import is used to import everything from a designated module under the current 
module, allowing the use of various objects from the imported module- without having to prefix them with the module's 
name. Refrain from using this type of import statement and rather explicitly import a few statements that you may 
require instead.   
""",
    ImportStarNotPermitted: """

**Import made using * **
This * import is used to import everything from a designated module under the current 
module, allowing the use of various objects from the imported module- without having to prefix them with the module's 
name. Refrain from using this type of import statement and rather explicitly import a few statements that you may 
require instead.
""",

    DuplicateArgument: """

**Duplicate argument `{0}` in function definition'**
Two or more parameters in a function definition have the same name.
All names in the function definition should be distinct. Change one of the names so that all parameters are unique.
""",

    MultiValueRepeatedKeyLiteral: """

**Dictionary key `{0}` repeated with different values**
A dictionary cannot have multiple entries for the same key. 
Check your code again and change the repeated key to something unique.
""",

}


def lint(code):
    # Wrap the whole module in a function
    # so that pyflakes thinks global variables are local variables
    # and reports when they are unused
    function_tree = ast.parse(code)
    ch = checker.Checker(function_tree, builtins=["assert_equal"])
    ch.messages.sort(key=lambda m: m.lineno)
    for message in ch.messages:
        if type(message) in MESSAGES:  # type(message) is the key component of dictionary
            message_format = MESSAGES[type(message)]  # message_format is the value component of the dictionary
            yield message_format.format(*message.message_args)

# to do at later stage: ReturnWithArgsInsideGenerator, AssertTuple
