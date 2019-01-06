#!/usr/bin/env bash

cd /workspace
BUNDLE_CURRENT_PREFIX=$(pwd)/v1_bundle source ./v1_bundle/setup.sh
./test-bundle.sh