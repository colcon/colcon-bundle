# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import glob
import json
import os
import subprocess

from colcon_bundle.installer import BundleInstallerExtensionPoint
from colcon_bundle.verb import logger
from colcon_core.plugin_system import satisfies_version


class AptBundleInstallerExtension(BundleInstallerExtensionPoint):
    """Extension to support apt package manager."""

    def __init__(self):  # noqa: D107
        self._cache = None
        self._cache_dir = None
        self.context = None
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

        parser.add_argument(
            '--apt-package-blacklist', default=blacklist_path,
            help='A file with newline separated names of packages that should'
                 'not be installed into the bundle')

    def should_load(self):  # noqa: D102
        try:
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(
                    ['apt-get', '--help'], stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
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
        import apt
        self.context = context
        self._cache_dir = context.cache_path
        self._cache = apt.Cache(
            rootdir=self._cache_dir, progress=apt.progress.text.OpProgress())
        self.setup()

    def setup(self):  # noqa: D102
        import apt

        apt.apt_pkg.config.set('APT::Install-Recommends', 'False')
        apt.apt_pkg.config.set('Dir::Etc::Trusted',
                               apt.apt_pkg.config.find_file(
                                   'Dir::Etc::Trusted'))
        apt.apt_pkg.config.set('Dir::Etc::TrustedParts',
                               apt.apt_pkg.config.find_file(
                                   'Dir::Etc::TrustedParts'))
        apt.apt_pkg.config.clear('APT::Update::Post-Invoke-Success')

        # Should we grab the sources from the system?
        sources_list_file = os.path.join(self._cache_dir, 'etc', 'apt',
                                         'sources.list')
        asset_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets')
        bundled_sources_list = os.path.join(asset_path, 'sources.list')
        os.makedirs(os.path.dirname(sources_list_file), exist_ok=True)
        # TODO Make this a plugin
        with open(sources_list_file, 'w') as f:
            with open(bundled_sources_list, 'r') as sources:
                f.write(sources.read())

        # We need to open and close the cache before calling update because
        # of a bug
        # if we don't do this then the update fails to pull anything from the
        # remote repos
        self._cache.open()
        self._cache.close()

        # Update the cache to the latest, we might not want to do this if the
        # cache already exists?
        self._cache.update()
        self._cache.open()

    def is_package_available(self, package_name):  # noqa: D102
        return self._cache[package_name] is not None

    def add_to_install_list(self, name, metadata=None):  # noqa: D102
        logger.info(
            'Marking {name} for installation'.format_map(locals()))
        logger.info(self._cache[name].versions)
        self._cache[name].mark_install(auto_fix=False, from_user=False)

    def remove_from_install_list(self, name, metadata=None):  # noqa: D102
        package = self._cache[name]
        package.mark_delete(auto_fix=False)

    def _fetch_packages(self):  # noqa: D102
        packages = []
        for package in self._cache:
            if package.marked_install:
                packages.append(package.name)
        logger.info('Fetching packages: {packages}'.format_map(locals()))
        self._cache.fetch_archives()

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

        return list(installed)
