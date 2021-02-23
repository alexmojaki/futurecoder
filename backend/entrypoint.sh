#!/usr/bin/env bash

set -eux

rm -f /usr/lib/python3/dist-packages/.wh*

# We probably don't want this to be automatic but it makes life a lot easier
# For setting up the cloud
python manage.py migrate
python manage.py init_db

# If no MASTER_URL is set, start a server in this container,
# which the web server will contact by default
if [ -z ${MASTER_URL+x} ]; then
  ./master_server.sh &
fi

gunicorn -c gunicorn_config_web.py book.wsgi:application --bind 0.0.0.0:${PORT:-3000}
