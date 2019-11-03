# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from colcon_bundle.installer.base_pip_installer import \
    BasePipInstallerExtensionPoint


class Pip3BundleInstallerExtensionPoint(BasePipInstallerExtensionPoint):
    """Python 3 pip installer."""

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--pip3-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to CMake projects. '
                 'Arguments matching other options in colcon must be prefixed '
                 'by a space,\ne.g. --pip3-args " --help"')
        parser.add_argument(
            '--pip3-requirements', type=str, default=None,
            help='Path to a requirements.txt. All packages in the file'
                 'will be installed into Python3 in the bundle')

    def initialize(self, context):  # noqa: D102
        super().initialize(context)
        self._python_path = os.path.join(
            self.context.prefix_path, 'usr', 'bin', 'python3')
        self._pip_args = self.context.args.pip3_args
        self.additional_requirements = self.context.args.pip3_requirements
