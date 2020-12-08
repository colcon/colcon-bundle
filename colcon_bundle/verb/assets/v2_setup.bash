#!/usr/bin/env bash

export PATH="usr/sbin:usr/bin:usr/local/bin:sbin:bin:$PATH"
export LD_LIBRARY_PATH="lib:usr/lib:lib/x86_64-linux-gnu:usr/lib/x86_64-linux-gnu:usr/lib/x86_64-linux-gnu/mesa:$LD_LIBRARY_PATH:lib/arm-linux-gnueabihf:usr/lib/arm-linux-gnueabihf:$LD_LIBRARY_PATH:lib/aarch64-linux-gnu:usr/lib/aarch64-linux-gnu"

DIR="$( cd "$( dirname "$BASH_SOURCE" )" && pwd)"

export LC_ALL=C.UTF-8

if [ -f $DIR/opt/ros/kinetic/setup.sh ]; then
	if [ -f $DIR/opt/ros/kinetic/setup.bash ]; then
  		_CATKIN_SETUP_DIR=$DIR/opt/ros/kinetic . $DIR/opt/ros/kinetic/setup.bash
  	else
  		_CATKIN_SETUP_DIR=$DIR/opt/ros/kinetic . $DIR/opt/ros/kinetic/setup.sh
  	fi

elif [ -f $DIR/opt/ros/melodic/setup.sh ]; then
	if [ -f $DIR/opt/ros/melodic/setup.bash ]; then

  		_CATKIN_SETUP_DIR=$DIR/opt/ros/melodic . $DIR/opt/ros/melodic/setup.bash
  	else
  		_CATKIN_SETUP_DIR=$DIR/opt/ros/melodic . $DIR/opt/ros/melodic/setup.sh
  	fi

elif [ -f $DIR/opt/ros/dashing/setup.sh ]; then
	if [ -f $DIR/opt/ros/dashing/setup.bash ]; then
  		AMENT_CURRENT_PREFIX=$DIR/opt/ros/dashing . $DIR/opt/ros/dashing/setup.bash
  	else
  		AMENT_CURRENT_PREFIX=$DIR/opt/ros/dashing . $DIR/opt/ros/dashing/setup.sh
  	fi
fi
