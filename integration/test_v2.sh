#!/usr/bin/env bash

cd /workspace
BUNDLE_CURRENT_PREFIX=$(pwd)/v2_bundle/dependencies source v2_bundle/dependencies/setup.sh
BUNDLE_CURRENT_PREFIX=$(pwd)/v2_bundle/workspace source v2_bundle/workspace/setup.sh
./test-bundle.sh