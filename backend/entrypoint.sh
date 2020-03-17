#!/usr/bin/env bash
set -ex

#nginx

#rabbitmq-server -detached

# We probably don't want this to be automatic but it makes life a lot easier
# For setting up the cloud
python manage.py migrate
python manage.py init_db

#python -m main.worker &

gunicorn -c gunicorn_config.py book.wsgi:application --bind 0.0.0.0:$PORT
