#!/bin/bash

set -eux

poetry --version || curl -sSL https://install.python-poetry.org | python3 -
poetry install

cd frontend
npm ci
cd ..

npm install -g sass

./build.sh
