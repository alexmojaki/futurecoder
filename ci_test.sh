#!/bin/bash

set -eux

export DISPLAY=:99
chromedriver --url-base=/wd/hub &
npm install -g firebase-tools
firebase emulators:exec "poetry run pytest tests"
