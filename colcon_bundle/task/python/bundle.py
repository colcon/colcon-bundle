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

            if 'version_eq' in dependency.metadata:
                pip = args.installers['pip3']
                pip.add_to_install_list(
                    dependency.name + '==' + dependency.metadata['version_eq'])
            else:
                logger.warning('Currently only support version locked '
                               'packages. Skipping: {dependency}'
                               .format(dependency=dependency))
                continue

            # TODO: The Pip managers should be doing this
            apt = args.installers['apt']
            apt.add_to_install_list('libpython3-dev')
            apt.add_to_install_list('python3-pip')
