# `futurecoder`

This is a platform/course for complete beginners to teach themselves programming, specifically in Python. Currently it's very much a work in progress - please consider [contributing](#contributing)!

You can try a demo here: https://futurecoder.herokuapp.com/

## Features

The course is a fully interactive 'book' which requires the user to run code in the provided editor or shell to advance:

![full](images/full.png)

The code at each step is checked automatically. Common mistakes can be caught and pointed out to the student. If needed, the student can get small hints to gradually guide them to the solution:

![hints](images/hints.png)

If they're still really stuck, they can reveal the solution bit by bit:

![solution](images/solution.png)

Tracebacks are more helpful than usual, highlighting the exact operation which failed and ensuring that the right amount of context is visible for multiline statements:

![traceback](images/traceback.png) 

Several debuggers are provided, including [snoop](https://github.com/alexmojaki/snoop):

![snoop](images/snoop.png)

[birdseye](https://github.com/alexmojaki/birdseye):

![birdseye](images/birdseye.png)

and [Python Tutor](http://pythontutor.com/):

![pythontutor](images/pythontutor.png)

## Contributing

While most of the groundwork is in place, there is a lot to do to make this a complete course ready for users. All kinds of help are needed and greatly appreciated.

For starters, try using the platform to see what it's like. You can go straight to the [demo site](https://futurecoder.herokuapp.com/) and quickly sign up for an account. See the [Controls](#controls) section below if you're not sure how to use it. Please give feedback about anything that's confusing, could be done better, or doesn't work.

In the event that the demo site gets more attention than it can handle, try [running the code locally with the instructions below](#running-locally).

The easiest way to contribute concretely is to write learning material for the course. This doesn't require any expertise beyond knowing how Python works. See [this issue](https://github.com/alexmojaki/futurecoder/issues/23) for some guidance and join the conversation!

Beyond that, there's plenty of coding work to do on the platform, including frontend, backend, and devops work. See the [list of issues](https://github.com/alexmojaki/futurecoder/issues) for some ideas.

## Running locally

1. Fork the repository, and clone your fork.
2. If you want to run the system using Docker, which may be easier and will more closely resemble the production environment:
    1. Ensure you have docker and docker-compose installed.
    2. Create an empty file called `.env` in the repo root.
    3. Run `docker-compose up`.
    4. Skip the following two steps, everything should be running now.
3. In the `backend` folder:
    1. Ensure the `python` command points to Python 3.8.
    2. Run `./setup.sh`. This will:
        1. Install `poetry` if needed.
        2. Create a virtualenv and install Python dependencies.
        3. Create a sqlite database, run migrations, and create a user.
    3. Activate the virtualenv with `poetry shell`.
    4. Run the backend development server with `./manage.py runserver`.
4. In the `frontend` folder:
    1. Ensure you have recent versions of `node` and `npm`.
    2. Run `npm install` to download dependencies.
    3. Run `npm start` to start the frontend development server.
5. Go to http://localhost:3000/accounts/login/ and login with the email "admin@example.com" and the password "admin".
6. You should be redirected to http://localhost:3000/course/ and see the start of the course: "Introducing The Shell".

## Controls

The course consists of *pages* and each page consists of *steps*. Each step requires that the user runs some code that satisfies the requirements of that step. Once they succeed, they are shown the next step. Once they complete all the steps in a page, they are shown the "Next page" button to move forward. They can click "Previous" if they want to review completed pages, but it doesn't affect their progress - any code they submit is still evaluated against the current step, and refreshing the page returns to the last page. Hopefully these basics (without the formal details) should become intuitively clear to the user as they try to use the site.

To explore the course more freely:

1. Click the hamburger menu icon in the top left.
2. Click Settings.
3. Turn Developer mode on.
4. This should give you two red buttons floating at the bottom of the screen. They change the currently active step, so you can move forward without having to complete exercises or backwards to test a step again.

At the beginning of the course only the shell is available to encourage quick exploration. After a few pages an editor is introduced to allow running full programs.

The course provides three debuggers to specially run code: snoop, PythonTutor, and birdseye. Each should only become available starting from a specific page which introduces that tool. No such page has been written yet for birdseye, so for now it's immediately available when the editor is introduced.

## System overview

The UI is written in React. It communicates with the web server using the `rpc` function, e.g. `rpc("run_code", {code, source}, onSuccess)`. This eventually reaches a method in the `API` class, e.g. `def run_code(self, code, source):`.

Running code specifically sends a request from the web server to the workers master server. This forwards the request to a process associated with that user's ID, starting a new process if necessary. Every user has their own process, which holds the state of the shell or the currently running program (which may be awaiting `input()`). The processes are isolated from each other and everything else, they can easily be terminated, and they have limitations on CPU time usage and file access.

After the code finishes running, it checks the `Page` and `Step` that the user is currently on, and calls the `Step.check` method. In most cases this is a `VerbatimStep` - the user is supposed to enter exactly the code in the text, using the AST to check for equality. Next most common is an `ExerciseStep` where a function has to pass tests and produce the same output as a given solution. The result of `Step.check` determines if the user succeeded and advances to the next step. It may also return a message to show the user, e.g. if they made a common mistake.
