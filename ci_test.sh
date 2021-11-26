#!/bin/bash

set -eux

export DISPLAY=:99
chromedriver --url-base=/wd/hub &
npm install -g firebase-tools
source $HOME/.poetry/env
export REACT_APP_USE_FIREBASE_EMULATORS=1
firebase emulators:exec "poetry run pytest tests"
