#!/usr/bin/env bash

set -ex

# test-nodes
rosrun test-nodes helloworld
rosrun test-nodes helloworld_dynamic

# test-cmake

helloworld_cmake

# test-pip-install

rosrun test-pip-install test-pip-install.py

# test-py-module

python3 -c "import test_py_module.run_annoy; test_py_module.run_annoy.test()"