# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import subprocess

from colcon_bundle.installer import BundleInstallerExtensionPoint
from colcon_bundle.verb import logger


class BasePipInstallerExtensionPoint(BundleInstallerExtensionPoint):
    """Base class for pip2/3 installers."""

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
        self.additional_requirements = None

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

    def cache_invalid(self):  # noqa: D102
        return self.additional_requirements is not None

    def install(self):  # noqa: D102
        if len(self._packages) == 0 and self.additional_requirements is None:
            logger.info('No dependencies to install for {}'.format(
                os.path.basename(self._python_path)
            ))
            return {'installed_packages': []}

        logger.info('Installing pip dependencies...')

        requirements_file = os.path.join(self._cache_path, 'requirements')
        metadata_file = os.path.join(self._cache_path, 'metadata')

        if self.additional_requirements is not None:
            logger.info('Installing additional Python requirements from'
                        '{req} into {path}'
                        .format(req=self.additional_requirements,
                                path=self._python_path))
            with open(self.additional_requirements) as req:
                for requirement in req.readlines():
                    self._packages.append(requirement)

        if os.path.exists(requirements_file) and os.path.exists(metadata_file):
            with open(requirements_file, 'r') as req:
                existing_requirements = list(map(str.strip, req.readlines()))
                if sorted(existing_requirements) == sorted(self._packages):
                    logger.info(
                        'No changes detected for {}'.format(self._python_path))
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        return metadata

        python_pip_args = [self._python_path, '-m', 'pip']
        pip_install_args = python_pip_args + ['install']
        subprocess.check_call(
            pip_install_args + ['-U', 'pip==20.*', 'setuptools==44.0.0'])
        subprocess.check_call(
            pip_install_args + ['-U', 'pip'])

        with open(requirements_file, 'w') as req:
            for name in self._packages:
                req.write(name.strip() + '\n')

        pip_args = []
        pip_args += pip_install_args
        pip_args += (self._pip_args or [])
        pip_args += ['--default-timeout=100']
        pip_args += ['--ignore-installed', '-r', requirements_file]
        subprocess.check_call(pip_args)

        # https://pip.pypa.io/en/stable/reference/pip_download/
        if self.context.args.include_sources:
            sources_path = os.path.join(self._cache_path, 'sources')
            download_args = python_pip_args + [
                'download', '--no-binary', ':all',
                '-d', sources_path, '-r', requirements_file]
            subprocess.check_call(download_args)

        metadata = self._generate_metadata(python_pip_args)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        return metadata

    def _generate_metadata(self, python_pip_args):
        pip_freeze_args = python_pip_args + ['freeze']

        freeze_output = subprocess.check_output(
            pip_freeze_args, universal_newlines=True)

        installed = list(map(
            self.split_package_version,
            filter(lambda s: s != '', freeze_output.split('\n'))))
        return {'installed_packages': installed}

    @staticmethod
    def split_package_version(package_version):
        """Split package==3.2.3 pip freeze output."""
        split_string = package_version.split('==')
        # TODO: This shouldn't be necessary if we fix #40 since we
        # should never install packages as editable
        if len(split_string) < 2 and '-e' in package_version:
            # Package is installed with --editable flag, and formatted
            # differently. Does not have a version number.
            # format: -e git+https://<repo>@<commit_hash>#egg=<package_name>.
            split_string = package_version.split('=')
            return {'name': split_string[1]}
        return {'name': split_string[0], 'version': split_string[1]}
