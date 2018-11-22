# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess

from colcon_bundle.installer import BundleInstallerExtensionPoint
from colcon_bundle.verb import logger


class BasePipInstallerExtensionPoint(BundleInstallerExtensionPoint):
    """Base class for pip2/3 installers"""

    __slots__ = (
        'context',
        '_packages',
        '_cache_path',
        '_python_path',
        '_pip_args'
    )

    PRIORITY = 10

    def __init__(self):  # noqa: D107
        self.context = None
        self._packages = []
        self._cache_path = None
        self._python_path = None
        self._pip_args = None

    def initialize(self, context):  # noqa: D102
        self.context = context
        self._cache_path = context.cache_path

    def add_to_install_list(self, name, *, metadata=None):
        """
        Mark the python package for installation.

        :param name: Name of the python package to install. This supports
        PEP440 compliant version specifiers.
        :return: None
        """
        self._packages.append(name)

    def remove_from_install_list(self, name, *, metadata=None):  # noqa: D102
        self._packages.remove(name)

    def install(self):  # noqa: D102
        if len(self._packages) == 0:
            logger.info('No pip dependencies to install.')
            return {'message': 'No dependencies installed...'}

        logger.info('Installing pip3 dependencies...')
        python_pip_args = [self._python_path, '-m', 'pip']
        pip_install_args = python_pip_args + ['install']
        subprocess.check_call(pip_install_args + ['-U', 'pip', 'setuptools'])

        requirements = os.path.join(self._cache_path, 'requirements')
        with open(requirements, 'w') as req:
            for name in self._packages:
                req.write(name.strip() + '\n')

        pip_args = []
        pip_args += pip_install_args
        pip_args += (self._pip_args or [])
        pip_args += ['--ignore-installed', '-r', requirements]
        subprocess.check_call(pip_args)

        pip_freeze_args = python_pip_args + ['freeze']

        freeze_output = subprocess.check_output(
            pip_freeze_args, universal_newlines=True)

        installed = list(map(
            self.split_package_version,
            filter(lambda s: s != '', freeze_output.split('\n'))))
        metadata = {'installed_packages': installed}

        # https://pip.pypa.io/en/stable/reference/pip_download/
        if self.context.args.include_sources:
            sources_path = os.path.join(self._cache_path, 'sources')
            download_args = python_pip_args + [
                'download', '--no-binary', ':all',
                '-d', sources_path, '-r', requirements]
            subprocess.check_call(download_args)
        return metadata

    @staticmethod
    def split_package_version(package_version):
        """Splits package==3.2.3 pip freeze output."""
        print(package_version)
        split_string = package_version.split('==')
        print(split_string)
        return {'name': split_string[0], 'version': split_string[1]}
