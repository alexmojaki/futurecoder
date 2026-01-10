#!/bin/bash

set -eux

# Run tests in CI, i.e. GitHub Actions

export DISPLAY=:99
chromedriver --url-base=/wd/hub &
npm install -g 'firebase-tools@<15.0.0'
firebase emulators:exec "poetry run pytest tests"
