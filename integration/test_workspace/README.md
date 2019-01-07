# Bundle Testing Package

This package is used as an integration test for colcon bundle.

# Build Environment

I usually am testing against a local version of colcon so I run
this first command in a directory that has access to this test
workspace and to the colcon source directories

`docker run -it -v $(pwd):/workspace ros:kinetic bash`

Once inside the docker container run:

1. `cd /workspace`
1. `./install-dependencies.sh`

Now everything you need except colcon-core and colcon-bundle are installed 
inside the container. Now navigate to your colcon sources under `/workspace` 
and run `pip install -e` on the colcon extension directories. 

You are now ready to run `colcon build` and `colcon bundle` on the workspace
contained in this package.

# Test Environment

Once you have followed the build environment steps and have built and bundled
this workspace execute the following from this directory:

`docker run -it -v $(pwd):/workspace ubuntu:xenial bash`

Once inside the container:

1. `cd /workspace/bundle/bundle_staging`
1. `export BUNDLE_CURRENT_PREFIX=$(pwd)`
1. `cd /workspace`
1. `./test-bundle.sh`

If any errors are thrown then the test is a falure, otherwise you should see
output with pass messages.

## What do each of the packages test?

test-cmake: Tests installation of dependencies of packages using the cmake 
buildtool dependency by depending on aws-sdk

test-nodes: Tests a package using the catkin build tool. Verifies dependencies get installed.

test-pip-install: Tests installation of pip dependencies in a catkin package

test-py-module: Tests setup.py python package handling