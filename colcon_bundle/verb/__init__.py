# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

from colcon_core.logging import colcon_logger

logger = colcon_logger.getChild(__name__)


def check_and_mark_bundle_tool(bundle_base, *, this_build_tool='colcon'):
    """
    Check the marker file for the previous bundle tool, otherwise create it.

    The marker filename is `.bundled_by`.

    :param str bundle_base: The bundle directory
    :param str this_build_tool: The name of this build tool
    :raises RuntimeError: if the marker file contains the name of a different
      build tool
    """
    marker_path = Path(bundle_base) / '.bundled_by'
    if marker_path.parent.is_dir():
        if marker_path.is_file():
            previous_build_tool = marker_path.read_text().rstrip()
            if previous_build_tool == this_build_tool:
                return
            raise RuntimeError(
                'The bundle directory "{bundle_base}" was created by '
                '"{previous_build_tool}". Please remove the bundle directory '
                'or pick a different one.'.format_map(locals()))
    else:
        os.makedirs(bundle_base, exist_ok=True)

    marker_path.write_text(this_build_tool + '\n')


def check_and_mark_bundle_version(bundle_base: str, *,
                                  this_bundle_version: int,
                                  previously_bundled: bool):
    """
    Check the bundle version marker file for the previous bundle version.

    The marker filename is `.bundle_version`.

    :param str bundle_base: The bundle directory
    :param str this_bundle_version: The version of the bundle to be built
    :param bool previously_bundled: true if the user has previously used
    this workspace to build a bundle
    :raises RuntimeError: if the bundle version does not match the passed
    in bundle version
    """
    marker_path = Path(bundle_base) / '.bundle_version'
    if previously_bundled:
        previous_bundle_version = 1
        if marker_path.is_file():
            previous_bundle_version = int(marker_path.read_text().rstrip())
        if previous_bundle_version == this_bundle_version:
            marker_path.write_text(str(this_bundle_version) + '\n')
            return
        raise RuntimeError(
            'The bundle directory "{bundle_base}" was used to create a '
            'version {previous_bundle_version} bundle. Please remove the '
            'bundle directory or pick a different one. If you would prefer '
            'to use the old version use the --bundle-version argument. '
            'Bundle version 2 has multiple improvements to bundling speed'
            'and other optimizations, it is highly '
            'recommended.'.format_map(locals()))
    marker_path.write_text(str(this_bundle_version) + '\n')


def get_and_mark_bundle_cache_version(bundle_base: str, *,
                                      previously_bundled: bool) -> int:
    """
    Check and return the bundle cache version.

    The marker filename is `.bundle_cache_version`.

    :param str bundle_base: The bundle directory
    :param bool previously_bundled: true if the user has previously used
    this workspace to build a bundle
    :returns: the cache layout version to use
    """
    marker_path = Path(bundle_base) / '.bundle_cache_version'
    bundle_cache_version = 2
    if previously_bundled:
        bundle_cache_version = 1
        if marker_path.is_file():
            bundle_cache_version = \
                int(marker_path.read_text().rstrip())
    marker_path.write_text(str(bundle_cache_version) + '\n')
    return bundle_cache_version
