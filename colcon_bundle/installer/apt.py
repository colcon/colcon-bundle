# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import glob
import json
import os
import subprocess

from colcon_bundle.installer import BundleInstallerExtensionPoint
from colcon_bundle.verb import logger
from colcon_bundle.verb.utilities import get_ubuntu_distribution_version
from colcon_core.plugin_system import satisfies_version


class PackageNotInCacheException(Exception):
    """The requested package was not found in the cache."""

    def __init__(self, package_name):  # noqa: D107
        self.package_name = package_name


class AptBundleInstallerExtension(BundleInstallerExtensionPoint):
    """Extension to support apt package manager."""

    def __init__(self):  # noqa: D107
        self._cache = None
        self._cache_dir = None
        self.context = None
        self.include_sources = False
        self.allow_insecure = False
        self.sources_path = None
        self.metadata = {}
        satisfies_version(
            BundleInstallerExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def __del__(self):  # noqa: D105
        if self._cache is not None:
            self._cache.close()

    def add_arguments(self, *, parser):  # noqa: D102
        assets_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets')
        blacklist_path = os.path.join(
            assets_directory, 'apt_package_blacklist.txt')
        sources_list_path = os.path.join(assets_directory,
                                         'xenial.sources.list')

        if get_ubuntu_distribution_version() == 'bionic':
            sources_list_path = os.path.join(assets_directory,
                                             'bionic.sources.list')
        elif get_ubuntu_distribution_version() == 'focal':
            sources_list_path = os.path.join(assets_directory,
                                             'focal.sources.list')

        parser.add_argument(
            '--apt-package-blacklist', default=blacklist_path,
            help='A file with newline separated names of packages that should'
                 'not be installed into the bundle')

        parser.add_argument(
            '--apt-sources-list', default=sources_list_path,
            help='Path to the apt sources list that should be used for package'
                 'installation in the bundle.')
        parser.add_argument(
            '--apt-allow-insecure', action='store_true',
            help='Sets Acquire::AllowInsecureRepositories and  '
                 'Acquire::AllowDowngradeToInsecureRepositories to True. See '
                 'apt-secure(8) manpage for more information.'
        )

    def should_load(self):  # noqa: D102
        """Determine if this plugin should load."""
        try:
            get_ubuntu_distribution_version()
        except ValueError:
            # Not on ubuntu, shouldn't load
            return False

        try:
            import apt  # noqa: F401
        except ImportError:
            raise RuntimeError("""
            Please install python3-apt in order to bundle your application

            You can do this by executing `apt-get install python3-apt`.

            If you are using a venv you will need to re-create it with the
            '--system-site-packages' option in order to have access to the
            library.
            """)
        return True

    def initialize(self, context):  # noqa: D102
        self.context = context
        self._cache_dir = context.cache_path
        self.include_sources = self.context.args.include_sources
        self.allow_insecure = self.context.args.apt_allow_insecure
        self.sources_path = os.path.join(self._cache_dir, 'sources')
        self.setup()

    def setup(self):  # noqa: D102
        # Importing apt here allows us to run
        # unit tests on OSX
        import apt

        # Get config values before creating cache, as the cache changes
        # the global config values when initialized.
        trusted = apt.apt_pkg.config.find_file('Dir::Etc::Trusted')
        trustedparts = apt.apt_pkg.config.find_file('Dir::Etc::TrustedParts')

        # Create cache after getting config values, the cache changes
        # global config values.
        self._cache = apt.Cache(rootdir=self._cache_dir,
                                progress=apt.progress.text.OpProgress())

        # Always get config values before creating the cache.
        apt.apt_pkg.config.set('APT::Install-Recommends', 'False')
        apt.apt_pkg.config.set('Dir::Etc::Trusted', trusted)
        apt.apt_pkg.config.set('Dir::Etc::TrustedParts', trustedparts)
        apt.apt_pkg.config.set('Acquire::BrokenProxy', 'true')
        apt.apt_pkg.config.set('Acquire::http::Pipeline-Depth', '0')
        apt.apt_pkg.config.set('Acquire::http::No-Cache', 'true')
        apt.apt_pkg.config.set('Acquire::http::Retries', '3')

        if self.allow_insecure:
            apt.apt_pkg.config.set(
                'Acquire::AllowInsecureRepositories', 'True')
            apt.apt_pkg.config.set(
                'Acquire::AllowDowngradeToInsecureRepositories', 'True')

        apt.apt_pkg.config.clear('APT::Update::Post-Invoke-Success')

        sources_list_file = os.path.join(self._cache_dir, 'etc', 'apt',
                                         'sources.list')
        os.makedirs(os.path.dirname(sources_list_file), exist_ok=True)

        with open(sources_list_file, 'w') as f:
            with open(self.context.args.apt_sources_list, 'r') as sources:
                f.write(sources.read())

        if self.include_sources:
            os.makedirs(self.sources_path, exist_ok=True)

        # We need to open and close the cache before calling update because
        # of a bug
        # if we don't do this then the update fails to pull anything from the
        # remote repos
        self._cache.open()
        self._cache.close()

        # Update the cache to the latest, we might not want to do this if the
        # cache already exists?
        try:
            self._cache.update()
        except apt.cache.FetchFailedException as e:
            logger.error('Could not fetch from repositories: {}'.format(e))
            raise RuntimeError('Failed to fetch from repositories. Did '
                               'you set your keys correctly?')
        self._cache.open()

        # Workaround for pip-requirements not installing python-pip
        self.add_to_install_list('python3-pip')

        # Currently not available in Focal
        if get_ubuntu_distribution_version() != 'focal':
            self.add_to_install_list('python-pip')

    def _separate_version_information(self, package_name):
        if '=' not in package_name:
            return package_name, ''
        return package_name.split('=', maxsplit=1)

    def is_package_available(self, package_name):  # noqa: D102
        package_key, _ = self._separate_version_information(package_name)
        return self._cache[package_key] is not None

    def add_to_install_list(self, name, metadata=None):  # noqa: D102
        logger.info('Adding {name} to install list'.format(name=name))
        package_key, version = self._separate_version_information(name)
        if not self.is_package_available(package_key):
            logger.error('Package {package_key} is not in the package'
                         'cache.'.format(package_key=package_key))
            raise PackageNotInCacheException(name)

        logger.info('Found these versions of {package_key}'
                    .format(package_key=package_key))
        logger.info(self._cache[package_key].versions)

        package = self._cache[package_key]
        # This will fallback to the latest version available
        # if the specified version does not exist.
        candidate = package.versions.get(version, package.candidate)
        package.candidate = candidate
        package.mark_install(auto_fix=False, from_user=False)

    def remove_from_install_list(self, name, metadata=None):  # noqa: D102
        name, _ = self._separate_version_information(name)
        package = self._cache[name]
        package.mark_delete(auto_fix=False)

    def _fetch_packages(self):  # noqa: D102
        from apt.cache import FetchFailedException
        from apt.package import FetchError
        packages = []
        source_fetch_failures = []
        for package in self._cache:
            if package.marked_install:
                if self.include_sources:
                    package_version = package.versions[0]
                    try:
                        package_version.fetch_source(
                            destdir=self.sources_path, unpack=False)
                    except ValueError:
                        source_fetch_failures.append(package.name)
                        logger.error('No sources available for {}'.format(
                            package.name
                        ))
                    except FetchFailedException as e:
                        source_fetch_failures.append(package.name)
                        logger.error('Failed to fetch sources for {}'.format(
                            package.name))
                        logger.error(e)
                    except FetchError as e:
                        source_fetch_failures.append(package.name)
                        logger.error('Failed to fetch sources for {}'.format(
                            package.name
                        ))
                        logger.error(e)
                packages.append(package.name)
        logger.info('Fetching packages: {packages}'.format_map(locals()))
        self._cache.fetch_archives()

        if len(source_fetch_failures) > 0:
            self.metadata['missing_sources'] = source_fetch_failures

    def install(self):  # noqa: D102
        # There are certain packages we don't want to install because they
        # come with the
        # base distribution of the OS. We remove them from the install list
        # here.
        with open(self.context.args.apt_package_blacklist, 'rt') as blacklist:
            blacklisted_packages = [line.rstrip('\n') for line in blacklist]

        for package_name in blacklisted_packages:
            try:
                self.remove_from_install_list(package_name)
            except KeyError:
                pass

        # Check for differences
        installed_cache_path = os.path.join(self._cache_dir, 'installed.json')
        if os.path.isfile(installed_cache_path):
            with open(installed_cache_path, 'r') as f:
                installed = set(json.loads(f.read()))
        else:
            installed = set()

        to_install = {package for package in self._cache
                      if package.marked_install}
        intersection = installed.intersection(to_install)
        if len(intersection) == len(to_install) and len(intersection) == len(
                installed):
            return False
        else:
            logger.info('The install list of the bundle has changed...')

        self._fetch_packages()

        deb_cache = os.path.join(
            self._cache_dir, 'var', 'cache', 'apt', 'archives')
        pkgs_abs_path = glob.glob(os.path.join(deb_cache, '*.deb'))
        print('Extracting apt packages...')
        for pkg in pkgs_abs_path:
            if os.path.basename(pkg) not in installed:
                try:
                    logger.info('Installing {package}'.format(package=pkg))
                    subprocess.check_call(
                        ['dpkg-deb', '--extract', pkg,
                         self.context.prefix_path])
                    installed.add(os.path.basename(pkg))
                except subprocess.CalledProcessError:
                    raise RuntimeError()

        with open(installed_cache_path, 'w') as f:
            f.write(json.dumps(list(installed)))

        installed_packages_metadata = []
        for package in self._cache:
            if package.marked_install:
                installed_packages_metadata.append(
                    {
                        'name': package.shortname,
                        'version': package.candidate.version
                    }
                )
        self.metadata['installed_packages'] = installed_packages_metadata

        return self.metadata
