import os
from pathlib import Path
import shutil

from colcon_bundle.verb import check_and_mark_bundle_tool, \
    check_and_mark_bundle_version, \
    get_and_mark_bundle_cache_version
from colcon_core.package_identification.ignore import IGNORE_MARKER


class PathContext:
    """
    Provides path configuration for bundle.

    This class allows us to change the layout of
    the bundle cache for new workspaces while maintaining
    compatibility with existing cache layouts. All paths
    should be referenced through PathContext.
    """

    def __init__(self,
                 install_base: str,
                 bundle_base: str,
                 bundle_version: int):
        """
        Set up the bundle directory for use with the bundle version.

        :param install_base: Directory with built artifacts from the workspace
        :param bundle_base: Directory to place the output of the bundle
        :param bundle_version: Bundle version that should be created (passed
        from user arguments)
        """
        previously_bundled = False
        if Path(bundle_base).is_dir():
            previously_bundled = True
        else:
            self._create_path(bundle_base)

        check_and_mark_bundle_version(bundle_base,
                                      this_bundle_version=bundle_version,
                                      previously_bundled=previously_bundled)
        cache_version = get_and_mark_bundle_cache_version(
            bundle_base,
            previously_bundled=previously_bundled)
        check_and_mark_bundle_tool(bundle_base)

        self._bundle_base = bundle_base
        self._bundle_cache = self._bundle_base
        if cache_version == 2:
            self._bundle_cache = os.path.join(self._bundle_base, 'cache')
            if os.path.exists(self.cache_valid_path()):
                os.remove(self.cache_valid_path())
            elif os.path.exists(self._bundle_cache):
                print('Cache is not valid. Clearing cache...')
                shutil.rmtree(self._bundle_cache)
            os.makedirs(self._bundle_cache, exist_ok=True)
        self._install_base = install_base

    def _create_path(self, path):
        path = Path(os.path.abspath(path))
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        ignore_marker = path / IGNORE_MARKER
        if not os.path.lexists(str(ignore_marker)):
            with ignore_marker.open('w'):
                pass

    def bundle_base(self):  # noqa: D400
        """:return: Directory to place the output of the bundle"""
        return self._bundle_base

    def install_base(self):  # noqa: D400
        """:return: Directory with built artifacts from the workspace"""
        return self._install_base

    def dependencies_staging_path(self):  # noqa: D400
        """:return: Directory where all dependencies have been installed"""
        return os.path.join(self._bundle_cache, 'bundle_staging')

    def dependencies_overlay_path(self):  # noqa: D400
        """:return: File path for dependencies tarball"""
        return os.path.join(self._bundle_cache, 'dependencies.tar.gz')

    def installer_metadata_path(self):  # noqa: D400
        """:return: File path for installer metadata"""
        return os.path.join(self._bundle_cache, 'installer_metadata.json')

    def installer_cache_path(self):  # noqa: D400
        """:return: Directory with installer artifacts from the installation"""
        return os.path.join(self._bundle_cache, 'installer_cache')

    # For archive generation v1
    def bundle_tar_path(self):  # noqa: D400
        """:return: File path for bundle tarball for archive v1"""
        return os.path.join(self._bundle_cache, 'bundle.tar')

    def metadata_tar_path(self):  # noqa: D400
        """:return: File path for metadata tarball for archive v1"""
        return os.path.join(self._bundle_cache, 'metadata.tar')

    def version_file_path(self):  # noqa: D400
        """:return: File path for version file for archive v1"""
        return os.path.join(self._bundle_cache, 'version')

    # For archive generation v2
    def workspace_staging_path(self):  # noqa: D400
        """:return: Directory where all workspace files locates"""
        return os.path.join(self._bundle_cache, 'workspace_staging')

    def workspace_overlay_path(self):  # noqa: D400
        """:return: File path for workspace tarball"""
        return os.path.join(self._bundle_cache, 'workspace.tar.gz')

    def dependency_hash_path(self):  # noqa: D400
        """:return: File path for direct dependency hash"""
        return os.path.join(self._bundle_cache, 'dependency_hash.json')

    def dependency_hash_cache_path(self):  # noqa: D400
        """:return: File path for direct dependency hash cache"""
        return os.path.join(self._bundle_cache, 'dependency_hash_cache.json')

    # Customer visible outputs
    def bundle_v1_output_path(self):  # noqa: D400
        """:return: File path for final output of the bundle for archive v1"""
        return os.path.join(self._bundle_base, 'output.tar.gz')

    def bundle_v2_output_path(self):  # noqa: D400
        """:return: File path for final output of the bundle for archive v2"""
        return os.path.join(self._bundle_base, 'output.tar')

    def sources_tar_gz_path(self):  # noqa: D400
        """:return: File path for sources files tarball"""
        return os.path.join(self._bundle_base, 'sources.tar.gz')

    def cache_valid_path(self):  # noqa: D400
        """:return: File path for cache valid file."""
        return os.path.join(self._bundle_cache, '.valid')
