# Development

To setup my workspace I generally pull down:

* `colcon-core` (https://github.com/colcon/colcon-core.git)
* `colcon-ros` (https://github.com/colcon/colcon-ros.git)
* `colcon-bundle` (https://github.com/colcon/colcon-bundle)
* `colcon-ros-bundle` (https://github.com/colcon/colcon-ros-bundle)

There are many more colcon packages, it can be useful to pull them down to look at how different extensions and other
functionality is implemented.

## Developing on OSX

I run these packages inside of docker containers since I'm running OSX and this only supports Ubuntu currently.

Build Container: `docker run -it -v $(pwd):/workspace ros:kinetic-ros-base /bin/bash`

Run Container: `docker run -it -v $(pwd):/workspace ubuntu:xenial /bin/bash`

I generally `cd` into my workspace which has the package folders and then start the container. This docker command
 mounts `pwd` to`/workspace`. Once in the container I `cd /workspace` and then execute:

1. `apt-get update`
1. `apt-get install -y python3-pip python3-apt`
1. `pip3 install --upgrade pip`
1. `export PATH=/usr/local/bin/pip3:$PATH`
1. `/usr/local/bin/pip3 install --editable ./colcon-bundle`
1. `/usr/local/bin/pip3 install --editable ./colcon-ros-bundle`

Inside of a ROS1 workspace execute the following:

1. `rosdep install --from-paths src --ignore-src -r -y`
1. `colcon build`
1. `colcon bundle`

## Testing

### Unit

To run tests execute `pytest` in the root directory. Install dependencies using `pip3 install -r requirements_devel.txt`.
You might need to `apt-get install enchant` to install the spellchecker.

To view stdout from a test while running `pytest` use the `-s` flag.

See `.travis.yml` for more information about what runs in the full test suite.

### Integration

If you have docker installed you can run tests by executing `run_integration_test.sh`. Take a look at our `travis.yml`
for more insight on what tests run and the environment they run in. Currently we test the following:

PyPI Dependencies:
* Kinetic - Xenial - Bundle V1 & V2
* Melodic - Bionic - Bundle V1 & V2

GitHub Master Branch Dependencies:
* Kinetic - Xenial - Bundle V1 & V2
* Melodic - Bionic - Bundle V1 & V2

We also have a backwards compatibility test that installs everything from PyPI, executes, and then installs
the local version of `colcon-bundle` to re-bundle.