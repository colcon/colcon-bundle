#!/usr/bin/env bash

apt-get update && apt-get install -y python3-pip python3-apt

# Get the latest version of pip before installing dependencies,	
# the version from apt can be very out of date (v8.0 on xenial)	
# The latest version of pip doesn't support Python3.5 as of v21,	
# but pip 8 doesn't understand the metadata that states this, so we must first	
# make an intermediate upgrade to pip 20, which does understand that information	
python3 -m pip install --upgrade pip==20.*	
python3 -m pip install --upgrade pip

pip3 install --upgrade pip setuptools

pip3 install -U colcon-common-extensions

echo "yaml https://s3-us-west-2.amazonaws.com/rosdep/base.yaml" > /etc/ros/rosdep/sources.list.d/19-aws-sdk.list

rosdep update
rosdep install --from-paths src --ignore-src -r -y 