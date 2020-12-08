#!/usr/bin/env bash

# Find location of file
DIR="$( cd "$( dirname "$BASH_SOURCE" )" && pwd)"

if [ -f $DIR/opt/built_workspace/setup.bash ]; then

	COLCON_CURRENT_PREFIX=$DIR/opt/built_workspace . $DIR/opt/built_workspace/setup.bash
else
	COLCON_CURRENT_PREFIX=$DIR/opt/built_workspace . $DIR/opt/built_workspace/setup.sh
fi