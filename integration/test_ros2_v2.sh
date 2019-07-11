#!/usr/bin/env bash

cd /workspace
BUNDLE_CURRENT_PREFIX=$(pwd)/v2_bundle/dependencies source v2_bundle/dependencies/setup.sh
AMENT_TRACE_SETUP_FILES=true  BUNDLE_CURRENT_PREFIX=$(pwd)/v2_bundle/workspace source v2_bundle/workspace/setup.sh

run_py_module_tests

ros2 run test_py_package run_py_package_tests

# Disabled until https://github.com/colcon/colcon-ros/issues/67 is resolved
# ros2 run test_cpp_package main_exe