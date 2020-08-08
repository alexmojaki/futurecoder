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

#### Implementing `check`.

When the user runs code, the code is passed to a worker which executes it. The worker then checks the code, output, and local variables in the `Step.check` instance method. The methods leading up to this are `Page.check_step` and `Step.check_with_messages`.

The `check` method almost always returns a boolean: `True` if the user entered the correct code and may advance, otherwise `False`. In rare cases it may return a dict `{"message": "<some message for the user>"}`, although you should usually use a `MessageStep` for this.

In most cases you want to inherit from `VerbatimStep` or `ExerciseStep`, which implement `check` for you but have additional requirements. If you want to implement `check` yourself, here are the attributes you can use from `self`:

- `input`: the code the user entered as a string.
- `tree`: the AST parsed from `input`. This is what you should use most often, especially with the helper functions `main.text.search_ast`, `astcheck.is_ast_like`, and `ast.walk`. The best place to learn about the Python AST is https://greentreesnakes.readthedocs.io/.
- `result`: the output of the user's program. This is a string containing both stdout and stderr. It's therefore a good way to check if a particular exception was raised.
- `code_source`: a string equal to either `"shell"`, `"editor"`, `"snoop"`, or `"birdseye"` indicating how the user ran the code. This is useful when you want to force the user to run code a certain way, e.g. to see a debugger in action or encourage exploration in the shell.
- `console.locals` is a dict of the variables created by the program.
