#!/bin/bash

set -eux

rm -rf dist || true
mkdir -p dist/course/

source $HOME/.poetry/env

poetry run python -m translations.generate_po_file
poetry run python -m core.generate_static_files

cd frontend
CI=false npm run build
cd ..

cp -r frontend/build/* dist/course/

sass homepage/static/css
cp -r homepage/* dist/
