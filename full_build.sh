#!/bin/bash

set -eux

poetry --version || curl -sSL https://install.python-poetry.org | python3 -
source $HOME/.poetry/env
poetry install

cd frontend
npm ci
cd ..

npm install -g sass

./build.sh
