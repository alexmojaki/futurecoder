[Environment]::SetEnvironmentVariable("SET_LIMITS", "false", "User")
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
poetry install
poetry run python manage.py migrate
poetry run python manage.py init_db
