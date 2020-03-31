#!/usr/bin/env bash

set -eux

# Prevent outdated from making http requests
echo '["0.2.0", "2099-01-01 00:00:00"]' >/tmp/outdated_cache_outdated
echo '["0.8.3", "2099-01-01 00:00:00"]' >/tmp/outdated_cache_birdseye

gunicorn -c gunicorn_config_worker.py main.workers.master:app
