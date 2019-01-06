#!/usr/bin/env sh

# You must set BUNDLE_CURRENT_PREFIX before sourcing this file
export PATH="$BUNDLE_CURRENT_PREFIX/usr/sbin:$BUNDLE_CURRENT_PREFIX/usr/bin:$BUNDLE_CURRENT_PREFIX/usr/local/bin:$BUNDLE_CURRENT_PREFIX/sbin:$BUNDLE_CURRENT_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$BUNDLE_CURRENT_PREFIX/lib:$BUNDLE_CURRENT_PREFIX/usr/lib:$BUNDLE_CURRENT_PREFIX/lib/x86_64-linux-gnu:$BUNDLE_CURRENT_PREFIX/usr/lib/x86_64-linux-gnu:$BUNDLE_CURRENT_PREFIX/usr/lib/x86_64-linux-gnu/mesa:$LD_LIBRARY_PATH:$BUNDLE_CURRENT_PREFIX/lib/arm-linux-gnueabihf:$BUNDLE_CURRENT_PREFIX/usr/lib/arm-linux-gnueabihf"

export LC_ALL=C.UTF-8

if [ -f $BUNDLE_CURRENT_PREFIX/opt/ros/kinetic/setup.sh ]; then
  _CATKIN_SETUP_DIR=$BUNDLE_CURRENT_PREFIX/opt/ros/kinetic . $BUNDLE_CURRENT_PREFIX/opt/ros/kinetic/setup.sh
elif [ -f $BUNDLE_CURRENT_PREFIX/opt/ros/melodic/setup.sh ]; then
  _CATKIN_SETUP_DIR=$BUNDLE_CURRENT_PREFIX/opt/ros/melodic . $BUNDLE_CURRENT_PREFIX/opt/ros/melodic/setup.sh
fi
