# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from collections import OrderedDict
import hashlib
import json
import os
from pathlib import Path
import tarfile

from colcon_bundle.installer import add_installer_arguments, \
    BundleInstallerContext, get_bundle_installer_extensions
from colcon_bundle.verb._archive_generators import generate_archive_v1, \
    generate_archive_v2
from colcon_bundle.verb.pathcontext import PathContext
from colcon_bundle.verb.utilities import rewrite_catkin_package_path, \
    update_shebang, update_symlinks
from colcon_core.argument_parser.destination_collector import \
    DestinationCollectorDecorator
from colcon_core.event_handler import add_event_handler_arguments
from colcon_core.executor import add_executor_arguments, execute_jobs, Job
from colcon_core.package_identification.ignore import IGNORE_MARKER
from colcon_core.package_selection import \
    add_arguments as add_package_arguments, get_packages
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import add_task_arguments, get_task_extension, \
    TaskContext
from colcon_core.verb import check_and_mark_install_layout, update_object,\
    VerbExtensionPoint

from . import check_and_mark_bundle_tool, logger


class BundlePackageArguments:
    """Arguments to bundle a specific package."""

    def __init__(self, pkg, installers, args, *,
                 additional_destinations=None):
        """
        Constructor.

        :param pkg: The package descriptor
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
            '--bundle-version', default=1, type=int,
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

    def main(self, *, context):  # noqa: D102
        print('Bundling workspace...')
        upgrade_deps_graph = context.args.upgrade
        install_base = os.path.abspath(context.args.install_base)
        bundle_base = os.path.abspath(context.args.bundle_base)

        if not os.path.exists(install_base):
            raise RuntimeError(
                'You must build your workspace before bundling it.')
        path_context = PathContext(bundle_base, install_base)

        dependencies_changed = self._manage_dependencies(
            context, path_context, upgrade_deps_graph)

        if context.args.bundle_version == 2:
            generate_archive_v2(path_context,
                                [path_context.installer_metadata_path()],
                                dependencies_changed)
        else:
            generate_archive_v1(path_context)

        return 0

    def _manage_dependencies(self, context,
                             path_context,
                             upgrade_deps_graph):

        bundle_base = path_context.bundle_base()
        check_and_mark_install_layout(
            path_context.install_base(),
            merge_install=context.args.merge_install)
        self._create_path(bundle_base)
        check_and_mark_bundle_tool(bundle_base)

        destinations = self.task_argument_destinations
        decorators = get_packages(context.args,
                                  additional_argument_names=destinations,
                                  recursive_categories=('run',))

        installers = self._setup_installers(context, path_context)

        print('Checking if dependency tarball exists...')
        logger.info('Checking if dependency tarball exists...')

        if not os.path.exists(path_context.dependencies_tar_gz_path()):
            self._check_package_dependency_update(path_context, decorators)
            self._check_installer_dependency_update(
                context, decorators, installers, path_context)
        elif upgrade_deps_graph:
            self._check_package_dependency_update(path_context, decorators)
            print('Checking if dependency graph has changed since last '
                  'bundle...')
            logger.info('Checking if dependency graph has changed since last'
                        ' bundle...')
            if self._check_installer_dependency_update(
                    context, decorators, installers, path_context):
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
            if self._check_package_dependency_update(path_context, decorators):
                print('Local dependencies not changed, skipping dependencies'
                      ' update...')
                logger.info(
                    'Local dependencies not changed, skipping dependencies'
                    ' update...')
                return False
            self._check_installer_dependency_update(
                context, decorators, installers, path_context)

        if context.args.include_sources:
            sources_tar_gz_path = path_context.sources_tar_gz_path()
            with tarfile.open(
                    sources_tar_gz_path, 'w:gz', compresslevel=5) as archive:
                for name, directory in self.installer_cache_dirs.items():
                    sources_path = os.path.join(directory, 'sources')
                    if not os.path.exists(sources_path):
                        continue
                    for filename in os.listdir(sources_path):
                        file_path = os.path.join(sources_path, filename)
                        archive.add(
                            file_path,
                            arcname=os.path.join(
                                name, os.path.basename(file_path)))

        staging_path = path_context.staging_path()
        update_symlinks(staging_path)
        # TODO: Update pkgconfig files?
        update_shebang(staging_path)
        # TODO: Move this to colcon-ros-bundle
        rewrite_catkin_package_path(staging_path)

        return True

    def _setup_installers(self, context, path_context):
        cache_path = path_context.installer_cache_path()
        prefix_path = os.path.abspath(path_context.staging_path())

        installers = get_bundle_installer_extensions()
        self.installer_cache_dirs = {}
        for name, installer in installers.items():
            installer_cache_dir = os.path.join(cache_path, name)
            self.installer_cache_dirs[name] = installer_cache_dir
            os.makedirs(installer_cache_dir, exist_ok=True)
            context = BundleInstallerContext(
                args=context.args,
                cache_path=installer_cache_dir,
                prefix_path=prefix_path)
            installer.initialize(context)
        return installers

    def _create_path(self, path):
        path = Path(os.path.abspath(path))
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        ignore_marker = path / IGNORE_MARKER
        if not ignore_marker.exists():
            with ignore_marker.open('w'):
                pass

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

    def _check_package_dependency_update(self, path_context, decorators):

        dependency_hash = {}

        for decorator in decorators:
            if not decorator.selected:
                continue
            pkg = decorator.descriptor
            dependency_list = sorted(dependency.name for dependency in
                                     pkg.dependencies['run'])
            dependency_hash[pkg.name] = hashlib.sha256(
                ' '.join(dependency_list).encode('utf-8')).hexdigest()

        current_hash_string = json.dumps(dependency_hash, sort_keys=True)
        logger.debug('Hash for current dependencies: '
                     '{current_hash_string}'.format_map(locals()))

        dependency_hash_path = path_context.dependency_hash_path()
        dependency_hash_cache_path = path_context.dependency_hash_cache_path()

        dependency_match = False
        if os.path.exists(dependency_hash_path):
            with open(dependency_hash_path, 'r') as f:
                previous_hash_string = f.read()
                if previous_hash_string == current_hash_string:
                    dependency_match = True

        with open(dependency_hash_cache_path, 'w') as f:
            f.write(current_hash_string)

        return dependency_match

    def _check_installer_dependency_update(
            self, context, decorators, installers, path_context):
        print('Collecting dependency information...')
        logger.info('Collecting dependency information...')
        jobs = self._get_jobs(context.args, installers, decorators)
        rc = execute_jobs(context, jobs)
        if rc != 0:
            return rc

        print('Fetching and installing dependencies...')
        logger.info('Fetching and installing dependencies...')
        installer_metadata = {}
        for name, installer in installers.items():
            installer_metadata[name] = installer.install()

        installer_metadata_string = json.dumps(installer_metadata,
                                               sort_keys=True)

        installer_metadata_path = path_context.installer_metadata_path()
        dependency_match = False
        if os.path.exists(installer_metadata_path):
            with open(installer_metadata_path, 'r') as f:
                previous_metadata = f.read()
                if previous_metadata == installer_metadata_string:
                    dependency_match = True

        with open(installer_metadata_path, 'w') as f:
            f.write(installer_metadata_string)

        return dependency_match
