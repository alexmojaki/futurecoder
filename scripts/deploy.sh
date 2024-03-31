#!/bin/bash

set -eux

# Make sure git is clean
[ -z "$(git status --porcelain)" ]

# Should contain e.g:
# export REACT_APP_SENTRY_DSN=https://...
source ./scripts/.env

./scripts/build.sh

# e.g. release-en-2022-10-23T22.14.50
TAG=release-${FUTURECODER_LANGUAGE}-$(date +'%Y-%m-%dT%H.%M.%S')

mkdir -p deploy_dist
cp -r dist/ deploy_dist/$TAG/

# Combine all stored releases of this language into one folder, with newer files overwriting older ones.
# This is so that files cached by the service worker looking for older files still find them,
# i.e. we don't want older files (with different filenames) to be removed from hosting, at least not too soon.
COMBINED=deploy_dist/release-${FUTURECODER_LANGUAGE}
rm -rf $COMBINED || true
mkdir -p $COMBINED
for dir in ${COMBINED}-*; do
    cp -r $dir/* $COMBINED/
done

if [ "$FUTURECODER_LANGUAGE" = "en" ]; then
    PROJECT=futurecoder-io
else
    PROJECT=futurecoder-${FUTURECODER_LANGUAGE}
fi

firebase --project $PROJECT deploy --only hosting --public $COMBINED

git tag $TAG
git push origin HEAD --tags
