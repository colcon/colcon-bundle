# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess

from colcon_bundle.installer import BundleInstallerExtensionPoint
from colcon_bundle.verb import logger


class Pip3BundleInstallerExtensionPoint(BundleInstallerExtensionPoint):
    """Python 3 pip installer."""

    __slots__ = (
        'context',
        '_packages',
        '_cache_path'
    )

    PRIORITY = 10

    def __init__(self):  # noqa: D107
        self.context = None
        self._packages = []
        self._cache_path = None

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--pip3-argument', default='build',
            help='The base path for all build directories (default: build)')

    def initialize(self, context):  # noqa: D102
        self.context = context
        self._cache_path = context.cache_path

    def add_to_install_list(self, name, metadata=None):
        """
        Mark the python package for installation.

        :param name: Name of the python package to install. This supports
        PEP440 compliant version specifiers.
        :return: None
        """
        self._packages.append(name)

    def remove_from_install_list(self, name, metadata=None):  # noqa: D102
        self._packages.remove(name)

    def install(self):  # noqa: D102
        if len(self._packages) == 0:
            logger.info('No pip dependencies to install.')
            return {'message': 'No dependencies installed...'}

        logger.info('Installing pip3 dependencies...')
        python_path = os.path.join(self.context.prefix_path, 'usr', 'bin',
                                   'python3')
        subprocess.check_call(
            [python_path, '-m', 'pip', 'install', '-U', 'pip', 'setuptools'])

        requirements = os.path.join(self._cache_path, 'requirements')
        with open(requirements, 'w') as req:
            for name in self._packages:
                req.write(name.strip() + '\n')

        subprocess.check_call(
            [python_path, '-m', 'pip', 'install', '--ignore-installed',
             '-r', requirements])

        return {'requirements': self._packages}
