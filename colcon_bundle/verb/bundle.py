# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from collections import OrderedDict
import os
from typing import Dict

from colcon_bundle.installer import add_installer_arguments, \
    BundleInstallerExtensionPoint
from colcon_bundle.verb._archive_generators import generate_archive_v1, \
    generate_archive_v2
from colcon_bundle.verb._dependency_utilities import \
    package_dependencies_changed
from colcon_bundle.verb._installer_manager import InstallerManager
from colcon_bundle.verb._path_context import PathContext
from colcon_core.argument_parser.destination_collector import \
    DestinationCollectorDecorator
from colcon_core.command import CommandContext
from colcon_core.event_handler import add_event_handler_arguments
from colcon_core.executor import add_executor_arguments, execute_jobs, Job
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.package_selection import \
    add_arguments as add_package_arguments, get_packages
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import add_task_arguments, get_task_extension, \
    TaskContext
from colcon_core.verb import check_and_mark_install_layout, \
    update_object, VerbExtensionPoint

from . import logger


class BundlePackageArguments:
    """Arguments to bundle a specific package."""

    def __init__(self, pkg: PackageDescriptor,
                 installers: Dict[str, BundleInstallerExtensionPoint],
                 args, *,
                 additional_destinations=None):
        """
        Construct the BundlePackageArguments.

        :param PackageDescriptor pkg: The package descriptor
        :param args: The parsed command line arguments
        :param list additional_destinations: The destinations of additional
          arguments
        """
        super().__init__()
        self.build_base = os.path.abspath(
            os.path.join(os.getcwd(), args.build_base, pkg.name))
        self.install_base = os.path.abspath(
            os.path.join(os.getcwd(), args.install_base))
        if not args.merge_install:
            self.install_base = os.path.join(self.install_base, pkg.name)
        self.bundle_base = os.path.abspath(
            os.path.join(os.getcwd(), args.bundle_base))
        self.installers = installers

        # set additional arguments from the command line or package metadata
        for dest in (additional_destinations or []):
            if hasattr(args, dest):
                update_object(
                    self, dest, getattr(args, dest),
                    pkg.name, 'bundle', 'command line')
            if dest in pkg.metadata:
                update_object(
                    self, dest, pkg.metadata[dest],
                    pkg.name, 'bundle', 'package metadata')


class BundleVerb(VerbExtensionPoint):
    """Bundle a package and all of its dependencies."""

    def __init__(self):  # noqa: D107
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')
        self._path_contex = None
        self._installer_manager = None

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument('--build-base', default='build',
                            help='The base path for all build directories ('
                                 'default: build)')
        parser.add_argument('--install-base', default='install',
                            help='The base path for all install prefixes ('
                                 'default: install)')
        parser.add_argument('--merge-install', action='store_true',
                            help='Merge all install prefixes into a single '
                                 'location')
        parser.add_argument('--bundle-base', default='bundle',
                            help='The base path for all bundle prefixes ('
                                 'default: bundle)')
        parser.add_argument(
            '--include-sources', action='store_true',
            help='Include a sources tarball for all packages installed into '
                 'the bundle via apt')
        parser.add_argument(
            '--bundle-version', default=2, type=int,
            help='Version of bundle to generate')
        parser.add_argument(
            '-U', '--upgrade', action='store_true',
            help='Upgrade all dependencies in the bundle to their latest '
                 'versions'
        )

        add_executor_arguments(parser)
        add_event_handler_arguments(parser)
        add_package_arguments(parser)

        decorated_parser = DestinationCollectorDecorator(parser)
        add_task_arguments(decorated_parser, 'colcon_bundle.task.bundle', )
        self.task_argument_destinations = decorated_parser.get_destinations()
        add_installer_arguments(decorated_parser)

    def main(self, *, context: CommandContext):  # noqa: D102
        print('Bundling workspace...')
        upgrade_deps_graph = context.args.upgrade
        install_base = os.path.abspath(context.args.install_base)
        merge_install = context.args.merge_install
        bundle_base = os.path.abspath(context.args.bundle_base)
        bundle_version = context.args.bundle_version

        if not os.path.exists(install_base):
            raise RuntimeError(
                'You must build your workspace before bundling it.')

        check_and_mark_install_layout(
            install_base,
            merge_install=merge_install)

        self._path_contex = PathContext(install_base,
                                        bundle_base,
                                        bundle_version)
        self._installer_manager = InstallerManager(self._path_contex)

        dependencies_changed = self._manage_dependencies(
            context,
            self._path_contex,
            upgrade_deps_graph)

        if context.args.bundle_version == 2:
            generate_archive_v2(self._path_contex,
                                [self._path_contex.installer_metadata_path()],
                                dependencies_changed)
        else:
            generate_archive_v1(self._path_contex)

        return 0

    def _manage_dependencies(self, context,
                             path_context,
                             upgrade_deps_graph):
        destinations = self.task_argument_destinations
        decorators = get_packages(context.args,
                                  additional_argument_names=destinations,
                                  recursive_categories=('run',))
        if len(decorators) == 0:
            estr = 'We did not find any packages to add to the '\
                   'bundle. This might be because you are not '\
                   'in the right directory, or your workspace is '\
                   'not setup correctly for colcon. Please see '\
                   'https://github.com/colcon/colcon-ros-bundle/issues/13' \
                   'for some possible suggestions. If you are still having ' \
                   'trouble please post to our' \
                   'issues: https://github.com/colcon/colcon-bundle/issues '\
                   'and we will be happy to help.'
            raise RuntimeError(estr)

        self._installer_manager.setup_installers(context)

        print('Checking if dependency tarball exists...')
        logger.info('Checking if dependency tarball exists...')

        jobs = self._get_jobs(context.args,
                              self._installer_manager.installers,
                              decorators)
        rc = execute_jobs(context, jobs)
        if rc != 0:
            return rc

        direct_dependencies_changed = package_dependencies_changed(
            path_context, decorators)
        installer_parameters_changed = \
            self._installer_manager.cache_invalid()

        if not os.path.exists(path_context.dependencies_overlay_path()):
            self._installer_manager.run_installers(
                include_sources=context.args.include_sources)
            return True
        elif upgrade_deps_graph:
            print('Checking if dependency graph has changed since last '
                  'bundle...')
            logger.info('Checking if dependency graph has changed since last'
                        ' bundle...')
            if self._installer_manager.run_installers(
                    include_sources=context.args.include_sources):
                print('All dependencies in dependency graph not changed, '
                      'skipping dependencies update...')
                logger.info('All dependencies in dependency graph not changed,'
                            ' skipping dependencies update...')
                return False
        else:
            print('Checking if local dependencies have changed since last'
                  ' bundle...')
            logger.info(
                'Checking if local dependencies have changed since last'
                ' bundle...')
            if not direct_dependencies_changed and \
                    not installer_parameters_changed:
                print('Local dependencies not changed, skipping dependencies'
                      ' update...')
                logger.info(
                    'Local dependencies not changed, skipping dependencies'
                    ' update...')
                return False
            self._installer_manager.run_installers(
                include_sources=context.args.include_sources)
        return True

    def _get_jobs(self, args, installers, decorators):
        jobs = OrderedDict()
        workspace_package_names = [decorator.descriptor.name for decorator in
                                   decorators]
        logger.info(
            'Including {} in bundle...'.format(workspace_package_names))
        for decorator in decorators:
            if not decorator.selected:
                continue

            pkg = decorator.descriptor
            extension = get_task_extension(
                'colcon_bundle.task.bundle', pkg.type)
            if not extension:
                logger.warn(
                    'No task extension to bundle a {pkg.type} package'
                    .format_map(locals()))
                continue

            recursive_dependencies = OrderedDict()
            for dep_name in decorator.recursive_dependencies:
                dep_path = args.install_base
                if not args.merge_install:
                    dep_path = os.path.join(dep_path, dep_name)
                recursive_dependencies[dep_name] = dep_path

            dest = self.task_argument_destinations.values()
            package_args = BundlePackageArguments(
                pkg, installers, args, additional_destinations=dest)
            ordered_package_args = ', '.join(
                [('%s: %s' % (repr(k), repr(package_args.__dict__[k]))) for k
                 in sorted(package_args.__dict__.keys())])
            logger.debug(
                'Bundling package {pkg.name} with the following arguments: '
                '{{{ordered_package_args}}}'.format_map(locals()))
            task_context = TaskContext(pkg=pkg, args=package_args,
                                       dependencies=recursive_dependencies)

            task_context.installers = installers

            job = Job(
                identifier=pkg.name,
                dependencies=set(recursive_dependencies.keys()),
                task=extension,
                task_context=task_context)

            jobs[pkg.name] = job
        return jobs
