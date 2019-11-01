import json
import os
import tarfile

from colcon_bundle.installer import BundleInstallerContext, \
    get_bundle_installer_extensions
from colcon_bundle.verb import logger
from colcon_bundle.verb._path_context import PathContext
from colcon_bundle.verb.utilities import rewrite_catkin_package_path, \
    update_shebang, update_symlinks
from colcon_core.command import CommandContext


class InstallerManager:
    """Manages the functionality of registered installer extension_points."""

    def __init__(self, path_context: PathContext):  # noqa: D107
        self._path_context = path_context
        self.prefix_path = os.path.abspath(
            self._path_context.dependencies_staging_path())
        self.installer_cache_dirs = {}
        self.installers = None

    def setup_installers(self, context: CommandContext):
        """
        Initialize all of the installer extension points.

        This will initialize all
        installer extension points registered under
        'colcon_bundle.installer'

        :param context: Context from the calling verb
        """
        cache_path = self._path_context.installer_cache_path()

        self.installers = get_bundle_installer_extensions()

        for name, installer in self.installers.items():
            installer_cache_dir = os.path.join(cache_path, name)
            self.installer_cache_dirs[name] = installer_cache_dir
            os.makedirs(installer_cache_dir, exist_ok=True)
            context = BundleInstallerContext(
                args=context.args,
                cache_path=installer_cache_dir,
                prefix_path=self.prefix_path)
            installer.initialize(context)

    def cache_invalid(self):
        """
        Check each installer to see if its arguments/parameters changed.

        :return: true if any of the installer parameters have
        changed this implies that run_installers() should
        be invoked again.
        """
        changed = False
        for name, installer in self.installers.items():
            changed = changed or installer.cache_invalid()
        return changed

    def run_installers(self, *, include_sources=False):
        """
        Invoke all installers to install packages into the bundle.

        :param include_sources: creates a sources tarball
        for all packages being installed that have sources
        available
        :return: true if all packages installed in the
        bundle are the same as the previous run
        """
        print('Collecting dependency information...')
        logger.info('Collecting dependency information...')

        print('Fetching and installing dependencies...')
        logger.info('Fetching and installing dependencies...')
        installer_metadata = {}
        for name, installer in self.installers.items():
            installer_metadata[name] = installer.install()

        installer_metadata_string = json.dumps(installer_metadata,
                                               sort_keys=True)

        installer_metadata_path = self._path_context.installer_metadata_path()
        dependency_match = False
        if os.path.exists(installer_metadata_path):
            with open(installer_metadata_path, 'r') as f:
                previous_metadata = f.read()
                if previous_metadata == installer_metadata_string:
                    dependency_match = True

        with open(installer_metadata_path, 'w') as f:
            f.write(installer_metadata_string)

        if include_sources:
            sources_tar_gz_path = self._path_context.sources_tar_gz_path()
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

        update_symlinks(self.prefix_path)
        # TODO: Update pkgconfig files?
        update_shebang(self.prefix_path)
        # TODO: Move this to colcon-ros-bundle
        rewrite_catkin_package_path(self.prefix_path)

        return dependency_match
