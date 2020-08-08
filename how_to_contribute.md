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
