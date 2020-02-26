# `python_init`

This is a platform/course for complete beginners to teach themselves programming, specifically in Python. Currently it's very much a WIP.

## Getting started

1. Clone the repository.
2. In the `backend` folder:
    1. Ensure the `python` command points to Python 3.8.
    2. Run `./setup.sh`. This will:
        1. Install `poetry` if needed.
        2. Create a virtualenv and install Python dependencies.
        3. Create a sqlite database, run migrations, and create a user.
    3. Activate the virtualenv with `poetry shell`.
    4. Run the backend development server with `./manage.py runserver`.
3. In the `frontend` folder:
    1. Ensure you have recent versions of `node` and `npm`.
    2. Run `npm install` to download dependencies.
    3. Run `npm start` to start the frontend development server.
4. Go to http://localhost:3000/accounts/login/ and login with the username "admin" and the password "admin".
5. You should be redirected to http://localhost:3000/ and see the start of the course: "Introducing The Shell".
