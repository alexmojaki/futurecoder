# How to contribute

For starters, try using the platform to see what it's like. You can go straight to the [demo site](https://futurecoder.herokuapp.com/) and quickly sign up for an account. See the [Controls](README.md#controls) section for instructions on enabling developer mode, this will allow you to skip or replay steps in a page to allow exploring more freely and quickly.

Please [open an issue](https://github.com/alexmojaki/futurecoder/issues/new) about anything that's confusing, could be done better, or doesn't work. All suggestions and feedback are welcome. Tell me what interests you!

If the demo site isn't working, or you want to make and test changes, try [running the server locally](README.md#running-locally).

The easiest way to contribute concretely is to write learning material for the course and participate in related discussions. This doesn't require any expertise beyond knowing how Python works. See [Helping with course content](#helping-with-course-content) for more information.

Beyond that, there's plenty of coding work to do on the platform, including frontend, backend, and devops work. See the [list of issues](https://github.com/alexmojaki/futurecoder/issues) for some ideas, or open a new one if you want. The main priority is to choose something that interests you. If nothing really does, pick something from the ["good first issue" label](https://github.com/alexmojaki/futurecoder/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) - these are easier and will help you become familiar with the project.

## Testing

Run `./manage.py test` in the backend folder.

The tests run through the course, submitting the solution/program for each step (and each of its message steps) and ensuring that the response is as expected. It then records all the requests and responses. By default, this record is compared to `test_transcript.json` for equality.

If you make some changes to the course, the tests will likely fail the comparison to `test_transcript.json`. Run the tests again with the environment variable `FIX_TESTS=1` to update the file. Then check that the git diff looks sensible.

## System overview

The course UI is written in React. It communicates with the web server using the `rpc` function, e.g. `rpc("run_code", {code, source}, onSuccess)`. This eventually reaches a method in the `API` class, e.g. `def run_code(self, code, source):`.

Running code specifically sends a request from the web server to the workers master server. This forwards the request to a process associated with that user's ID, starting a new process if necessary. Every user has their own process, which holds the state of the shell or the currently running program (which may be awaiting `input()`). The processes are isolated from each other and everything else, they can easily be terminated, and they have limitations on CPU time usage and file access.

After the code finishes running, it checks the `Page` and `Step` that the user is currently on, and calls the `Step.check` method. In most cases this is a `VerbatimStep` - the user is supposed to enter exactly the code in the text, using the AST to check for equality. Next most common is an `ExerciseStep` where a function has to pass tests and produce the same output as a given solution. The result of `Step.check` determines if the user succeeded and advances to the next step. It may also return a message to show the user, e.g. if they made a common mistake.

## Helping with course content

Take a look at [the issues labeled "course material"](https://github.com/alexmojaki/futurecoder/issues?q=is%3Aissue+is%3Aopen+label%3A%22course+material%22). These include discussions that need opinions/ideas and small tweaks that need to be made to existing content.

If you want to write fresh content, see [this issue](https://github.com/alexmojaki/futurecoder/issues/23) for the central discussion and additional guidance. This is a good place to dump rough ideas and snippets.

If you want to contribute a solid bit of course with actual text, code, and exercises, open a new issue with a proposal draft just in markdown. Don't jump to implementing it in Python.

## How to implement course content in Python

### Chapters

To the user, a chapter is a group of pages in the table of contents. In the code, a chapter is a single Python file under `backend/main/chapters`. To add a new chapter, just add a new file and follow the naming pattern. The title of the chapter for the table of contents will be derived automatically from the filename.

### Pages

To the user, a page is a group of steps that can be viewed all at once. You can jump to any page in the table of contents, or use the Previous/Next buttons to go back and forth.

In code, a page is a class in a chapter file inheriting from `main.text.Page`. Pages have the following:

- A `slug`, which by default is just the class name. This is used in various places in the system to identify the page, e.g. it's stored in the database to identify which page a user last visited. If you blindly rename a page class you will break existing data. If you must do so, set the `slug` class attribute to the original class name.
- A `title`, which is what the user sees. By default this is derived from the class name. You can override it by setting the `title` class attribute, which can include markdown.
- Zero or more step classes declared inside, discussed below.
- A `final_text` attribute. This is required. This is like the final 'step', except it's not a step class, it's just a string containing markdown. This is the end of a page after a user has completed all the steps that require interaction. When the user sees the final text, they will see the 'Next' button below to go to the next page (if there is one).

### Steps

Steps are the building blocks of the course, and this is where things get interesting. A step is some text containing information and instructions or an exercise for the user plus logic to check that they have completed the step correctly. Users must complete steps (by running code) to advance through the course.

In code, a step is a class inheriting from `main.text.Step` declared inside a `Page` class. It has:

- `text`. This is a string containing markdown displayed to the user. Typically this is declared just in the docstring of the class, but you can set the `text` class attribute directly if needed.
- A `check` method which determines if the user submitted the right code, discussed more below.
- A `program`, which is a string containing Python code which would solve this step and allow the user to advance, i.e. it passes the `check` method. This has several uses:
    - It shows readers of the code what you expect users to enter for this step.
    - It's used to automatically test the `check` method.
    - It will be shown to the user if they request a solution after reading all hints.
    - It's what users have to enter in a `VerbatimStep`.
    - If the `text` contains `__program__` or `__program_indented__`, that will be replaced by the `program`.
 
   You can define `program` as a string or a method. A string is good if the program is really short or contains invalid syntax. A method is better in other cases so that editors can work with it nicely. It will be converted to a string automatically.
- `hints` (optional) is a list of markdown strings which the user can reveal one by one to gradually guide them to a solution. For brevity you can provide a single string which will be split by newlines.
- Zero or more `MessageStep` classes declared inside, detailed further down.

#### Generating steps automatically

The fastest way to get started implementing steps is to open `backend/main/generate_steps.py`, replace `input_text` a markdown draft, and run the script. This will generate a series of `VerbatimStep`s (see below) where each indented code block becomes the program for one step. This won't usually be exactly what you need, but it gets a lot of the boring boilerplate out of the way.

#### The `check` method

When the user runs code, the code is passed to a worker which executes it. The worker then checks the code, output, and local variables in the `Step.check` instance method. The methods leading up to this are `Page.check_step` and `Step.check_with_messages`.

The `check` method almost always returns a boolean: `True` if the user entered the correct code and may advance, otherwise `False`. In rare cases it may return a dict `{"message": "<some message for the user>"}`, although you should usually use a `MessageStep` for this.

In most cases you want to inherit from `VerbatimStep` or `ExerciseStep`, which implement `check` for you but have additional requirements. If you want to implement `check` yourself, here are the attributes you can use from `self`:

- `input`: the code the user entered as a string.
- `tree`: the AST parsed from `input`. This is what you should use most often, especially with the helper functions `main.text.search_ast`, `astcheck.is_ast_like`, and `ast.walk`. The best place to learn about the Python AST is https://greentreesnakes.readthedocs.io/.
- `result`: the output of the user's program. This is a string containing both stdout and stderr. It's therefore a good way to check if a particular exception was raised.
- `code_source`: a string equal to either `"shell"`, `"editor"`, `"snoop"`, `"pythontutor"`, or `"birdseye"` indicating how the user ran the code. This is useful when you want to force the user to run code a certain way, e.g. to see a debugger in action or encourage exploration in the shell.
- `console.locals` is a dict of the variables created by the program.

#### VerbatimStep

This is the simplest kind of step. The text should instruct the user to run specific code, and they have to enter that exact code to pass. 'Exact' means that the AST must match - there can be differences in whitespace, comments, and the type of quotes used, but the rest should be identical, including variable names. If the only difference is due to case sensitivity, then a message will be shown to the user about this.

The code that the user must enter is given by `program`, which can be a string or a method.

The text should contain the program so that the user can copy it. Rather than duplicating the program, write `__program__` or `__program_indented__` in the text and it will be automatically replaced by the program, indented in the latter case. For example, your class might look like this:

    class one_plus_two(VerbatimStep):
        """
        Run `__program__` in the shell.
        """
        
        program = "1 + 2"
    
Then the text will say "Run `1 + 2` in the shell." and the user will have to do exactly that to continue (although if the editor is visible they can use that too). Alternatively, if you want them to run some longer multiline code, it would look like this:

    class one_plus_two(VerbatimStep):
        """
        Run this:
        
            __program_indented__
        """
        
        def program(self):
            x = 1 + 2
            print(x)

Actually indenting `__program_indented__` is optional.

In some cases you don't want the full program in the text. For example if the full program was specified in the previous step and you don't want the text to repeat it, you can write "replace <some line> with <some other line>". Make sure these instructions are very clear, as the user will not have access to hints or the complete solution. Then set `program_in_text = False` in the class to indicate your intention, otherwise an error will be raised when `__program__` is not found in the text.

#### ExerciseStep

This is for when the student needs to solve a problem on their own, and statically analysing a submission won't do - you need to run the code with different inputs to verify that it's correct.

For example, a user will typically be given text like:

> Time for an exercise! Given a number `foo` and a string `bar`, e.g:
> 
>     foo = 5
>     bar = 'spam'
>
> Write a program which prints `bar` `foo` times, e.g:
>
>     spam
>     spam
>     spam
>     spam
>     spam

The first thing you need is a `solution` method. This is specified instead of `program`, which will be generated from `solution`. It should have function parameters corresponding to the inputs of the exercise. In this case, the `solution` method is:

```python
def solution(self, foo: int, bar: str):
    for _ in range(foo):
        print(bar)
```

The user must then start their program with variable definitions for `foo` and `bar`. They don't need to use the exact values in the example, just the names. These will be stripped from the program to produce a function which can take any inputs and thus be tested and compared to the solution. The user may try to write a program which always just prints `spam` 5 times, so we need to make sure they've written a properly generic program.

The next thing the `ExerciseStep` needs is `tests`. This is a list of inputs to pass to the solution and their corresponding expected outputs. The inputs can be a tuple of arguments, a dict of keyword arguments, or a single argument if the solution only takes one. The value of `tests` can be a list of pairs or a dict if the inputs are hashable.

`tests` can have any number of entries - you typically want 2 or 3. They're useful for readers of the code to see what the solution is meant to do. If the user's code produces the right output for their own inputs but doesn't pass one of the tests, they will be shown the inputs, expected output, and actual output from their code. Therefore you want your tests to be simple readable examples that are helpful to both developers and students, while also checking the program behaviour nicely. Here is an example:

```python
tests = {
    (5, "spam"): """\
spam
spam
spam
spam
spam
""",
    (3, "baz"): """\
baz
baz
baz
""",
}
```

`tests` will be immediately used to test `solution`, you'll get an error if they don't match.

The `tests` alone are not quite enough to prevent a user from cheating. Since they are always shown the inputs and outputs, they could just use `if` to hardcode the correct outputs. To really make sure, the exercise will also generate some random inputs. The step's `solution` will then generate the expected outputs, and the user submission must match those too. The method `generate_inputs` should return one random dict of keyword arguments to pass to the solution. The default implementation does this automatically based on the type annotations in `solution`, so often (such as in this case) you don't need to do it yourself.

Finally, remember to give some `hints`! These are very important for exercises.

#### MessageStep

A `MessageStep` class is declared inside a regular `Step` class. It checks for mistakes and other problems and gives a message to the user if needed.

`MessageStep` inherits from `Step` and lets you use the same framework. You can even inherit from both `MessageStep` and `ExerciseStep`. Like a normal `Step`, you need to provide text and a `check` method. If `check` returns `True`, the text may be shown to the user. You also need to provide `program` (or `solution` for an `ExerciseStep`) as an example of something that passes `check`.

The default use case is to point out a mistake that prevented the user from advancing. In this case, the message `check` method will only be called if the outer step `check` returned False. This way you don't have to worry about showing the user a message "here's why you failed" when they actually succeeded.

The other case is when they technically solved the problem as described but you don't want them to pass because they used some sneaky trick or otherwise missed the intended solution. In this case the message `check` will only be called if the outer step `check` returned True. To indicate this, set `after_success = True` in the message class.

Any `Step` class declared inside another `Step` class (so typically an inner `MessageStep`) will automatically inherit from the outer `Step` class. This makes it easy to reuse methods from the outer class in the inner class, for example you only need to define `generate_inputs` once. Of course this can also lead to some weird side effects, so be aware of it. This is part of the system that I feel iffy about for obvious reasons, so it may change.
