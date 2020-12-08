#!/usr/bin/env bash

# cd /workspace
echo 'dep'
source v2_bundle/dependencies/setup.bash
echo 'ws'
source v2_bundle/workspace/setup.bash
./test-bundle.sh
