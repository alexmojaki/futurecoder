#!/usr/bin/env bash
set -ex

#nginx

# We probably don't want this to be automatic but it makes life a lot easier
# For setting up the cloud
python manage.py migrate
python manage.py init_db

# Prevent outdated from making http requests
echo '["0.2.0", "2099-01-01 00:00:00"]' > /tmp/outdated_cache_outdated 
echo '["0.8.3", "2099-01-01 00:00:00"]' > /tmp/outdated_cache_birdseye

gunicorn --bind 127.0.0.1:5000 main.workers.master:app --access-logfile - --error-log - --threads 10 --worker-class gthread &

gunicorn -c gunicorn_config.py book.wsgi:application --bind 0.0.0.0:${PORT:-3000}
