<p align="center">
  <img src="backend/main/static/logo/bordered2.png" width="300px" height="300px" alt="logo">
</p>

<h1 align="center"><code>futurecoder</code></h1>

This is a free platform/course for people to teach themselves programming in Python, especially complete beginners at programming.
It is carefully designed to reduce frustration and guide the user while still ensuring that they learn how to solve problems.
The goal is for as many people as possible to learn programming.

You can try it out here: https://futurecoder.io/

Currently this is a work in progress. While most of the groundwork is in place, there is a lot to do to make this a complete course ready for users. **All kinds of help are needed and greatly appreciated - please consider [contributing](how_to_contribute.md)!**

Alternatively, [come have a chat on slack](https://join.slack.com/t/futurecoder/shared_invite/zt-irqxk6og-tS2RqTp679MQAlUCmmnAZw).

## Features

<table>
  <tr>
    <td colspan="2">
The course is a fully interactive 'book' which requires the user to run code in the provided editor or shell to
advance:
    </td>
  </tr>
    <tr>
    <td colspan="2">

![full](images/full.png)
    </td>
  </tr>
  <tr>
    <td>
This requires a mixture of solving problems or simply typing and running provided code. In the latter case, the
user is often kept engaged by being asked to predict the output in a simple multiple choice question:
    </td>
    <td>
The code at each step is checked automatically. If
needed, the student can get small hints to gradually guide them to the solution:
    </td>
  </tr>
  <tr>
    <td>
    
![predict_output](images/predict_output.png)
    </td>
    <td>
    
![hints](images/hints.png)
    </td>
  </tr>
  <tr>
    <td>
If they're still really stuck, they can reveal the solution bit by bit:
</td>
<td>

Or in some cases solve a *Parsons problem* instead, where they have to put a shuffled solution in the correct
order:
</td>
  </tr>
  <tr>
    <td>
    
![solution](images/solution.png)
</td>
<td>

![parsons](images/parsons.png)
</td>
  </tr>
  <tr>

<td>
Tracebacks are more helpful than usual, with several enhancements:

- Highlighting the exact operation that failed, not just the line, using [executing](https://github.com/alexmojaki/executing)
- Tables of local variables and simple expressions evaluated by [pure_eval](https://github.com/alexmojaki/pure_eval)
- Suggestions for fixes provided by [DidYouMean](https://github.com/SylvainDe/DidYouMean-Python)
- Beginner friendly explanations provided by [friendly-traceback](https://github.com/aroberge/friendly-traceback) (shown when hovering over the little `i` icon)
- Showing multiline statements in full thanks to [stack_data](https://github.com/alexmojaki/stack_data) without showing unnecessary extra lines

</td>
<td>
Common mistakes can be caught and pointed out to the student. This includes specific checks in some steps as well as linting tailored for beginners.
</td>
  </tr>
  <tr>

<td>

![traceback](images/traceback.png)
</td>
<td>

![executing](images/messages.png)
</td>
  </tr>
  <tr>
    <td>
    
Several debuggers are provided, including [snoop](https://github.com/alexmojaki/snoop)...
    </td>
    <td>
    
[...birdseye...](https://github.com/alexmojaki/birdseye)
    </td>
  </tr>
    <tr>
    <td>
    
![snoop](images/snoop.png)
    </td>
    <td>
    
![birdseye](images/birdseye.png)
    </td>
  </tr>
  <tr>
    <td colspan="2">
    
...and [Python Tutor](http://pythontutor.com/)
    </td>
  </tr>
  <tr>
    <td colspan="2">
    
![pythontutor](images/pythontutor.png)
    </td>
  </tr>
</table>

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
6. You should be redirected to http://localhost:3000/toc/ and see the Table of Contents.

## Controls

To explore the course more freely:

1. Click the hamburger menu icon in the top left.
2. Click Settings.
3. Turn Developer mode on.
4. This should give you two red buttons floating at the bottom of the screen. They change the currently active step, so you can move forward without having to complete exercises or backwards to test a step again.
