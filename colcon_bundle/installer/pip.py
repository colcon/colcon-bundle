# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from colcon_bundle.installer.base_pip_installer import \
    BasePipInstallerExtensionPoint


class PipBundleInstallerExtensionPoint(BasePipInstallerExtensionPoint):
    """Python 2 pip installer."""

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--pip-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to CMake projects. '
            'Arguments matching other options in colcon must be prefixed '
            'by a space,\ne.g. --pip-args " --help"')

    def initialize(self, context):  # noqa: D102
        super().initialize(context)
        self._python_path = os.path.join(
            self.context.prefix_path, 'usr', 'bin', 'python2')
        self._pip_args = self.context.args.pip_args
