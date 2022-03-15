#!/bin/bash

set -eux

rm -rf dist || true
mkdir -p dist/course/

if [[ -z "${SKIP_TRANSLATIONS:-}" ]]; then
    poetry run python -m translations.generate_po_file
    poetry run python -m core.generate_static_files
else
    # If SKIP_TRANSLATIONS is set, set a default language for this build
    if [[ -z "${FUTURECODER_LANGUAGE:-}" ]]; then
        export FUTURECODER_LANGUAGE="en"
    fi
fi


cd frontend
NODE_ENV=production REACT_APP_LANGUAGE=$FUTURECODER_LANGUAGE CI=false npm run build
cd ..

cp -r frontend/course/* dist/course/

npx -y --package=sass -- sass homepage/static/css
cp -r homepage/* dist/
