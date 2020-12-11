#!/usr/bin/env {{ shell }}

# If using sh environment, please set DIR before sourcing this script
if [ "{{ shell }}" = "bash" ]; then
	DIR="$( cd "$( dirname "$BASH_SOURCE" )" && pwd)"
else
	DIR="$BUNDLE_CURRENT_PREFIX"
fi

export PATH="$DIR/usr/sbin:$DIR/usr/bin:$DIR/usr/local/bin:$DIR/sbin:$DIR/bin:$PATH"
export LD_LIBRARY_PATH="$DIR/lib:$DIR/usr/lib:$DIR/lib/x86_64-linux-gnu:$DIR/usr/lib/x86_64-linux-gnu:$DIR/usr/lib/x86_64-linux-gnu/mesa:$LD_LIBRARY_PATH:$DIR/lib/arm-linux-gnueabihf:$DIR/usr/lib/arm-linux-gnueabihf:$LD_LIBRARY_PATH:$DIR/lib/aarch64-linux-gnu:$DIR/usr/lib/aarch64-linux-gnu"

export LC_ALL=C.UTF-8

if [ -f "$DIR/opt/ros/kinetic/setup.{{ shell }}" ]; then
  _CATKIN_SETUP_DIR=$DIR/opt/ros/kinetic . $DIR/opt/ros/kinetic/setup.{{ shell }}
elif [ -f "$DIR/opt/ros/melodic/setup.{{ shell }}" ]; then
  _CATKIN_SETUP_DIR=$DIR/opt/ros/melodic . $DIR/opt/ros/melodic/setup.{{ shell }}
elif [ -f "$DIR/opt/ros/noetic/setup.{{ shell }}" ]; then
  _CATKIN_SETUP_DIR=$DIR/opt/ros/noetic . $DIR/opt/ros/noetic/setup.{{ shell }}
elif [ -f "$DIR/opt/ros/dashing/setup.{{ shell }}" ]; then
  AMENT_CURRENT_PREFIX=$DIR/opt/ros/dashing . $DIR/opt/ros/dashing/setup.{{ shell }}
elif [ -f "$DIR/opt/ros/foxy/setup.{{ shell }}" ]; then
  AMENT_CURRENT_PREFIX=$DIR/opt/ros/foxy . $DIR/opt/ros/foxy/setup.{{ shell }}
fi
