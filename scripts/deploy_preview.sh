#!/bin/bash

set -eux

# Should contain e.g:
# export REACT_APP_SENTRY_DSN=https://...
source ./scripts/.env

CHANNEL_NAME=$1

./scripts/build.sh

if [ "$FUTURECODER_LANGUAGE" = "en" ]; then
    PROJECT=futurecoder-io
elif [ "$FUTURECODER_LANGUAGE" = "es" ]; then
    PROJECT=futurecoder-es-latam
else
    PROJECT=futurecoder-${FUTURECODER_LANGUAGE}
fi

firebase --project $PROJECT hosting:channel:deploy $CHANNEL_NAME --expires 28d
