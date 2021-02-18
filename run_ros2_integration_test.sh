#!/usr/bin/env bash

set -ex

if [[ ${ROS_DISTRO} = "dashing" ]]
then
  UBUNTU_VERSION=bionic
elif [[ ${ROS_DISTRO} = "foxy" ]]
then
  UBUNTU_VERSION=focal
else
  echo "Invalid ROS2 ROS_DISTRO: ${ROS_DISTRO} "
  exit 1
fi

# Clean up
rm -rf integration/v2_bundle
rm -rf integration/v2.tar

docker build -f Dockerfile.${ROS_DISTRO} -t test-container .

# Copy bundles into local directory
docker run -v="$(pwd)":/workspace test-container bash -c "sudo cp v2/output.tar /workspace/integration/v2.tar"

cd integration

# Extract bundles
rm -rf ./v2_bundle
mkdir ./v2_bundle

mkdir ./v2_bundle/dependencies
tar -xOf ./v2.tar dependencies.tar.gz | tar -xzf - --directory ./v2_bundle/dependencies

mkdir ./v2_bundle/workspace
tar -xOf ./v2.tar workspace.tar.gz | tar -xzf - --directory ./v2_bundle/workspace

# Run tests
docker run -v "$(pwd)":/workspace ubuntu:${UBUNTU_VERSION} /workspace/test_ros2_v2.sh
docker run -v "$(pwd)":/workspace ubuntu:${UBUNTU_VERSION} /workspace/test_ros2_v2.bash

