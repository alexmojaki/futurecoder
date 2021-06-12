#!/bin/bash

set -eux

./setup.sh
source $HOME/.poetry/env

cd frontend
npm ci
cd ..

npm install -g sass

./build.sh
