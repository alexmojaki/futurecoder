#!/bin/bash

set -eux

./setup.sh

cd frontend
npm ci
cd ..

npm install -g sass

./build.sh
