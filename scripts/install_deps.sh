#!/bin/bash

set -eux

# Install Python dependencies
poetry --version || curl -sSL https://install.python-poetry.org | python3 -
poetry install

# Install JS dependencies
cd frontend
npm ci
cd ..
