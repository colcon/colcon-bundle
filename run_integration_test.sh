#!/usr/bin/env bash

set -ex

# Clean up
rm -rf integration/v1_bundle
rm -rf integration/v2_bundle
rm -rf integration/v1.tar.gz
rm -rf integration/v2.tar

# Build bundles
docker build -t test-container .
# Copy bundles into local directory
docker run -v=$(pwd):/workspace test-container /workspace/integration/copy-bundles.sh

cd integration

# Extract bundles
rm -rf ./v2_bundle
mkdir ./v2_bundle

mkdir ./v2_bundle/dependencies
tar -xOf ./v2.tar dependencies.tar.gz | tar -xzf - --directory ./v2_bundle/dependencies

mkdir ./v2_bundle/workspace
tar -xOf ./v2.tar workspace.tar.gz | tar -xzf - --directory ./v2_bundle/workspace

rm -rf ./v1_bundle
mkdir ./v1_bundle

tar -xzOf ./v1.tar.gz bundle.tar | tar -xf - --directory ./v1_bundle

# Run tests
docker run -it -v $(pwd):/workspace ubuntu:xenial /workspace/test_v1.sh
docker run -it -v $(pwd):/workspace ubuntu:xenial /workspace/test_v2.sh
