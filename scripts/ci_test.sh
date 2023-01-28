#!/bin/bash

set -eux

# Run tests in CI, i.e. GitHub Actions

npm install -g firebase-tools
firebase emulators:exec "poetry run pytest tests"
