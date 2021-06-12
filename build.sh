#!/bin/bash

set -eux

rm -rf dist || true
mkdir -p dist/course/

export PYTHONPATH=.
source $HOME/.poetry/env

BIRDSEYE=`poetry run python -c '
import birdseye
from pathlib import Path
print(Path(birdseye.__file__).parent)
'`
cp -r $BIRDSEYE/static/ dist/course/birdseye/

poetry run python core/generate_static_files.py

cd frontend
npm run build
cd ..

cp -r frontend/build/* dist/course/

sass homepage/static/css
cp -r homepage/* dist/
