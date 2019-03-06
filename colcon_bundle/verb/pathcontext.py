import os


class PathContext:
    """Provides path configuration for bundle."""

    def __init__(self, bundle_base, install_base):
        """
        Constructor.

        :param bundle_base: Directory to place the output of the bundle
        :param install_base: Directory with built artifacts from the workspace
        """
        self._bundle_base = bundle_base
        self._install_base = install_base

    def bundle_base(self):  # noqa: D400
        """:return: Directory to place the output of the bundle"""
        return self._bundle_base

    def install_base(self):  # noqa: D400
        """:return: Directory with built artifacts from the workspace"""
        return self._install_base

    def staging_path(self):  # noqa: D400
        """:return: Directory where all dependencies have been installed"""
        return os.path.join(self._bundle_base, 'bundle_staging')

    def dependencies_tar_gz_path(self):  # noqa: D400
        """:return: File path for dependencies tarball"""
        return os.path.join(self._bundle_base, 'dependencies.tar.gz')

    def installer_metadata_path(self):  # noqa: D400
        """:return: File path for installer metadata"""
        return os.path.join(self._bundle_base, 'installer_metadata.json')

    def sources_tar_gz_path(self):  # noqa: D400
        """:return: File path for sources files tarball"""
        return os.path.join(self._bundle_base, 'sources.tar.gz')

    def installer_cache_path(self):  # noqa: D400
        """:return: Directory with installer artifacts from the installation"""
        return os.path.join(self._bundle_base, 'installer_cache')

    # For archive generation v1
    def bundle_tar_path(self):  # noqa: D400
        """:return: File path for bundle tarball for archive v1"""
        return os.path.join(self._bundle_base, 'bundle.tar')

    def metadata_tar_path(self):  # noqa: D400
        """:return: File path for metadata tarball for archive v1"""
        return os.path.join(self._bundle_base, 'metadata.tar')

    def archive_tar_gz_path(self):  # noqa: D400
        """:return: File path for final output of the bundle for archive v1"""
        return os.path.join(self._bundle_base, 'output.tar.gz')

    def version_file_path(self):  # noqa: D400
        """:return: File path for version file for archive v1"""
        return os.path.join(self._bundle_base, 'version')

    # For archive generation v2
    def workspace_staging_path(self):  # noqa: D400
        """:return: Directory where all workspace files locates"""
        return os.path.join(self._bundle_base, 'workspace_staging')

    def archive_tar_path(self):  # noqa: D400
        """:return: File path for final output of the bundle for archive v2"""
        return os.path.join(self._bundle_base, 'output.tar')

    def workspace_tar_gz_path(self):  # noqa: D400
        """:return: File path for workspace tarball"""
        return os.path.join(self._bundle_base, 'workspace.tar.gz')

    def dependency_hash_path(self):  # noqa: D400
        """:return: File path for direct dependency hash"""
        return os.path.join(self._bundle_base, 'dependency_hash.json')

    def dependency_hash_cache_path(self):  # noqa: D400
        """:return: File path for direct dependency hash cache"""
        return os.path.join(self._bundle_base, 'dependency_hash_cache.json')
