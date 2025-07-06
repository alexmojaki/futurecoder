# How to contribute

This page explains how to help build the futurecoder platform by writing code or course material.

**If you'd like to donate money, please do so at [open collective](https://opencollective.com/futurecoder).**

**For translating futurecoder to languages other than English, [see this guide](https://github.com/alexmojaki/futurecoder/wiki/How-to-write-translations-for-futurecoder).**

For starters, try using the platform to see what it's like. From the [table of contents](https://futurecoder.io/course/#toc) you can jump to any page and start immediately. No account needed. If you want to try all the debuggers, pick a page close to the end of the course where everything is enabled. See the [Controls](README.md#controls) section for instructions on enabling developer mode, this will allow you to skip or replay steps in a page to allow exploring more freely and quickly.

Please [open an issue](https://github.com/alexmojaki/futurecoder/issues/new) about anything that's confusing, could be done better, or doesn't work. All suggestions and feedback are welcome. Tell me what interests you!

Consider adding your thoughts and ideas to [issues labeled 'discussion'](https://github.com/alexmojaki/futurecoder/issues?q=is%3Aissue+is%3Aopen+label%3Adiscussion). Or [come have a chat about anything on discord](https://discord.gg/KwWvQCPBjW).

The easiest way to contribute concretely is to write learning material for the course and participate in related discussions. This doesn't require any expertise beyond knowing how Python works. See [Helping with course content](#helping-with-course-content) for more information.

Beyond that, there's plenty of coding work to do on the platform in Python and JavaScript. See the [list of issues](https://github.com/alexmojaki/futurecoder/issues) for some ideas, or open a new one if you want. The main priority is to choose something that interests you. If nothing really does, pick something from the ["good first issue" label](https://github.com/alexmojaki/futurecoder/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) - these are easier and will help you become familiar with the project. See [Developing](#developing) for some technical guidance.

## Helping with course content

Take a look at [the issues labeled "course material"](https://github.com/alexmojaki/futurecoder/issues?q=is%3Aissue+is%3Aopen+label%3A%22course+material%22). These include discussions that need opinions/ideas and small tweaks that need to be made to existing content.

If you want to write fresh content, see [this issue](https://github.com/alexmojaki/futurecoder/issues/165) for the central discussion.

Before writing anything, it's a good idea to go through some of the course to get a feel for the style. Reading all the hints on a few exercises would also help. See the [developer mode instructions](https://github.com/alexmojaki/futurecoder#controls) to quickly move back and forth between steps.

It can be helpful to read through existing textbooks and such to find inspiration for material. Make sure you have permission to copy their ideas (even if you rephrase it into different words) or that it's permissively licensed. If you're not sure, ask them. I don't want anyone to accuse us of plagiarism.

If you want to contribute a solid bit of course with actual text, code, and exercises, open a new issue with a proposal draft just in markdown. Actually implementing course content in Python is trickier so I handle those details. If you're really curious, there's partial documentation [here](https://github.com/alexmojaki/futurecoder/wiki/How-course-content-works).

If you have some partial ideas you'd like to talk about but don't feel ready to open an issue, [come chat on discord](https://discord.gg/KwWvQCPBjW).

## Developing

### Testing

Run `pytest tests` with the poetry virtualenv active. 

#### `test_steps`

The full test suite is quite slow, particularly `test_frontend`. When you are only writing course content, it's enough to run `pytest -k test_steps`.

This test runs through the course, submitting the solution/program for each step (and each of its message steps) and ensuring that the response is as expected. It then records all the requests and responses. By default, this record is compared to `test_transcript.json` for equality.

If you make some changes to the course, the tests will likely fail the comparison to `test_transcript.json`. Run the test again with the environment variable `FIX_TESTS=1` to update the file. Then check that the git diff looks sensible.

### System overview

- **Python runs in the browser with [Pyodide](https://pyodide.org/)**. There are no backend servers.
  - This runs in a web worker (`Worker.js`) in the background so it doesn't interfere with the UI.
  - `SharedArrayBuffer` is used for some features (`input()` and `KeyboardInterrupt`) which comes with certain restrictions, including not working on Safari.
  - The entire `core` folder as well as several libraries are packaged into a single archive which the worker downloads (`load.py`) and extracts into Pyodide's virtual filesystem.
  - The script `scripts/generate_static_files.py` creates the above archive and some other files and puts them under `frontend/src` to be packaged by React.
  - When a user runs code, `Worker.js` calls the Python function `check_entry` in `checker.py`.
    - After the code finishes running, it checks the `Page` and `Step` that the user is currently on, and calls the `Step.check` method.
    - In most cases this is a `VerbatimStep` - the user is supposed to enter exactly the code in the text, using the AST to check for equality.
    - Next most common is an `ExerciseStep` where a function has to pass tests and produce the same output as a given solution.
    - The result of `Step.check` determines if the user succeeded and advances to the next step. It may also return a message to show the user, e.g. if they made a common mistake.
- **React JS** provides the course UI.
  - It's mostly just a standard Create-React-App, very slightly customised by craco.
  - The UI communicates with the web worker using Comlink (`RunCode.js`).
  - State is managed by Redux (`store.js`) with some custom utilities (`frontendlib`).
- **Firebase** handles:
  - Authentication: signup, login, and anonymous accounts
  - Realtime Database stores user data: progress on each page and last page visited
  - Hosting for the main site, although since it's just static files so it can be hosted anywhere quite easily. 
