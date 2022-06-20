#!/bin/bash

set -eux

### Collect all files to deploy to the folder 'dist'

# Delete any past files and create a fresh folder
rm -rf dist || true
mkdir -p dist/course/

# Generate various files with Python scripts, placing many of them inside the frontend folder

poetry run python -m scripts.generate_static_files

# Build the react app in the frontend folder, 'compiling' JS and CSS, and copy the result into the dist folder
cd frontend
REACT_APP_PRECACHE=1 REACT_APP_LANGUAGE=$FUTURECODER_LANGUAGE CI=false npm run build
cd ..
cp -r frontend/course/* dist/course/

# Build the CSS in the homepage folder and copy the result into the dist folder
npx -y --package=sass -- sass homepage/static/css
cp -r homepage/* dist/

# If there's a translated homepage index.html for this language, copy it into dist, replacing the English one
translated_index=translations/locales/${FUTURECODER_LANGUAGE}/index.html
if [ -f $translated_index ]; then
    cp $translated_index dist
fi
