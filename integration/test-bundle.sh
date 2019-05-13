#!/usr/bin/env bash

set -ex

# test cmake

hello

# test-nodes
rosrun test-nodes helloworld
rosrun test-nodes helloworld_dynamic

# test-catkin-cmake

helloworld_cmake

# test-pip-install

rosrun test-pip-install test-pip-install.py

# test-py-module

python3 -c "import test_py_module.run_annoy; test_py_module.run_annoy.test()"