#!/bin/bash

set -eux

# Should contain e.g:
# export REACT_APP_SENTRY_DSN=https://...
source ./scripts/.env

CHANNEL_NAME=$1

./scripts/build.sh

firebase --project futurecoder-io hosting:channel:deploy $CHANNEL_NAME --expires 28d
