#!/usr/bin/env bash

apt-get update && apt-get install -y python3-pip python3-apt

pip3 install -U colcon-common-extensions

echo "yaml https://s3-us-west-2.amazonaws.com/rosdep/base.yaml" > /etc/ros/rosdep/sources.list.d/19-aws-sdk.list

rosdep update
rosdep install --from-paths src --ignore-src -r -y