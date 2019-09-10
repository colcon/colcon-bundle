# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from colcon_bundle.task import logger
from colcon_core.dependency_descriptor import DependencyDescriptor
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint


class PythonBundleTask(TaskExtensionPoint):
    """Bundles python packages in the workspace."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        pass

    async def bundle(self):  # noqa: D102
        args = self.context.args
        verbose = False
        logger.info(
            'Bundling python package in "{self.context.pkg.path}" with build '
            'type "python"'.format_map(locals()))

        for dependency in self.context.pkg.dependencies['run']:
            if not isinstance(dependency, DependencyDescriptor):
                continue

            if dependency.name in self.context.dependencies:
                logger.info(
                    'Skipping {dependency} dependency of {self.context.pkg} '
                    'because it is in the workspace'.format_map(locals()))
                continue

            # Currently, only the first five of these mappings are supported
            # by colcon-core. The others are added for completeness with
            # PEP 440.
            symbol_mapping = {
                'version_eq': '==',
                'version_lte': '<=',
                'version_gte': '>=',
                'version_gt': '>',
                'version_lt': '<',
                'version_neq': '!=',
                'version_aeq': '===',
                'version_compatible': '~=',
            }

            pip = args.installers['pip3']
            versioned = False
            for comparator, version in dependency.metadata.items():
                if symbol_mapping.get(comparator) is not None:
                    versioned = True
                    pip.add_to_install_list(
                        dependency.name + symbol_mapping[comparator] + version
                    )
            if not versioned:
                pip.add_to_install_list(
                    dependency.name
                )

            # TODO: The Pip managers should be doing this
            apt = args.installers['apt']
            apt.add_to_install_list('libpython3-dev')
            apt.add_to_install_list('python3-pip')
