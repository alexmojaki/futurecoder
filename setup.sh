#!/bin/bash

set -eux

poetry --version || curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
source $HOME/.poetry/env
poetry install
