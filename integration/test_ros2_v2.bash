#!/usr/bin/env bash

cd /workspace
source ./v2_bundle/dependencies/setup.bash
AMENT_TRACE_SETUP_FILES=true  source ./v2_bundle/workspace/setup.bash

run_py_module_tests

ros2 run test_py_package run_py_package_tests

# Disabled until https://github.com/colcon/colcon-ros/issues/67 is resolved
ros2 run test_cpp_package main_exe
