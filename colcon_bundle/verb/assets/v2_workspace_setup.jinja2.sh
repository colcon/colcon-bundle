#!/usr/bin/env {{ shell }}

# If using sh environment, please set BUNDLE_CURRENT_PREFIX before sourcing this script
if [ "{{ shell }}" = "bash" ]; then
	DIR="$( cd "$( dirname "$BASH_SOURCE" )" && pwd)"
else
	DIR="$BUNDLE_CURRENT_PREFIX"
fi


if [ -f "$DIR/opt/built_workspace/setup.{{ shell }}" ]; then
	COLCON_CURRENT_PREFIX=$DIR/opt/built_workspace . $DIR/opt/built_workspace/setup.{{ shell }}
fi
