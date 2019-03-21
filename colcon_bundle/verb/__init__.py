# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

from colcon_core.logging import colcon_logger

logger = colcon_logger.getChild(__name__)


class PostBundleActionExtensionPoint:
    """
    Provides a hook for executing actions after bundling is complete.

    This extension point should be tied to a
    package type, one instance of this extension will
    be executed per package type built into the bundle.
    """

    def execute(self, path):
        """
        Execute any necessary actions after bundle creation.

        :param path: Path to the root of the bundle
        :return: None
        """
        raise RuntimeError('This should be implemented by a subclass')


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


def check_and_mark_bundle_version(bundle_base, *, this_bundle_version):
    """
    Check the bundle version marker file for the previous bundle version.

    The marker filename is `.bundle_version`.

    :param str bundle_base: The bundle directory
    :param str this_bundle_version: The version of the bundle to be built
    :raises RuntimeError: if the bundle version does not match the passed
    in bundle version
    """
    marker_path = Path(bundle_base) / '.bundle_version'
    if marker_path.parent.is_dir():
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
    else:
        os.makedirs(bundle_base, exist_ok=True)

    marker_path.write_text(str(this_bundle_version) + '\n')
