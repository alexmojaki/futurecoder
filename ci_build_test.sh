#!/bin/bash

set -eux

./full_build.sh
export DISPLAY=:99
chromedriver --url-base=/wd/hub &
npm install -g firebase-tools
source $HOME/.poetry/env
firebase emulators:exec "poetry run pytest tests"
