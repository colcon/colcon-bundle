import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, Mock

from colcon_bundle.verb._path_context import PathContext


class TestPathContext(TestCase):
    def setUp(self):
        self.install_base = tempfile.mkdtemp()
        self.bundle_base = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.install_base)
        shutil.rmtree(self.bundle_base)

    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_version')
    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_tool')
    @patch('colcon_bundle.verb._path_context.get_and_mark_bundle_cache_version')
    def test_v2_cache(self, cache_version, *_):
        cache_version.return_value = 2
        context = PathContext(self.install_base, self.bundle_base, 2)
        assert context.bundle_base() == self.bundle_base
        assert context.install_base() == self.install_base

        self._assert_under_cache_subpath(context.dependency_hash_path())
        self._assert_under_cache_subpath(context.installer_cache_path())
        self._assert_under_cache_subpath(context.dependency_hash_cache_path())
        self._assert_under_cache_subpath(context.dependencies_overlay_path())
        self._assert_under_cache_subpath(context.bundle_tar_path())
        self._assert_under_cache_subpath(context.installer_metadata_path())
        self._assert_under_cache_subpath(context.metadata_tar_path())
        self._assert_under_cache_subpath(context.dependencies_staging_path())
        self._assert_under_cache_subpath(context.version_file_path())
        self._assert_under_cache_subpath(context.workspace_staging_path())
        self._assert_under_cache_subpath(context.workspace_overlay_path())

        self._assert_not_under_cache_subpath(context.bundle_v1_output_path())
        self._assert_not_under_cache_subpath(context.bundle_v2_output_path())
        self._assert_not_under_cache_subpath(context.sources_tar_gz_path())

    def _assert_under_cache_subpath(self, path: str):
        p = Path(path)
        self.assertEqual(p.relative_to(self.bundle_base).parts[0], 'cache')

    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_version')
    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_tool')
    @patch('colcon_bundle.verb._path_context.get_and_mark_bundle_cache_version')
    def test_v1_no_cache(self, cache_version, *_):
        cache_version.return_value = 1
        context = PathContext(self.install_base, self.bundle_base, 2)
        assert context.bundle_base() == self.bundle_base
        assert context.install_base() == self.install_base

        self._assert_not_under_cache_subpath(context.dependency_hash_path())
        self._assert_not_under_cache_subpath(context.installer_cache_path())
        self._assert_not_under_cache_subpath(context.dependency_hash_cache_path())
        self._assert_not_under_cache_subpath(context.dependencies_overlay_path())
        self._assert_not_under_cache_subpath(context.bundle_tar_path())
        self._assert_not_under_cache_subpath(context.installer_metadata_path())
        self._assert_not_under_cache_subpath(context.metadata_tar_path())
        self._assert_not_under_cache_subpath(context.dependencies_staging_path())
        self._assert_not_under_cache_subpath(context.version_file_path())
        self._assert_not_under_cache_subpath(context.workspace_staging_path())
        self._assert_not_under_cache_subpath(context.workspace_overlay_path())

        self._assert_not_under_cache_subpath(context.bundle_v1_output_path())
        self._assert_not_under_cache_subpath(context.bundle_v2_output_path())
        self._assert_not_under_cache_subpath(context.sources_tar_gz_path())

    def _assert_not_under_cache_subpath(self, path: str):
        p = Path(path)
        self.assertNotEqual(p.relative_to(self.bundle_base).parts[0], 'cache')

    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_version')
    @patch('colcon_bundle.verb._path_context.get_and_mark_bundle_cache_version')
    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_tool')
    def test_initalize_bundle_base_does_not_exist(self, bundle_tool, cache_version, bundle_version):
        shutil.rmtree(self.bundle_base)
        PathContext(self.install_base, self.bundle_base, 2)
        bundle_version.assert_called_with(self.bundle_base,
                                          this_bundle_version=2,
                                          previously_bundled=False)
        cache_version.assert_called_with(self.bundle_base,
                                         previously_bundled=False)
        bundle_tool.assert_called_with(self.bundle_base)

    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_version')
    @patch('colcon_bundle.verb._path_context.get_and_mark_bundle_cache_version')
    @patch('colcon_bundle.verb._path_context.check_and_mark_bundle_tool')
    def test_initalize_bundle_base_does_exist(self, bundle_tool, cache_version, bundle_version):
        PathContext(self.install_base, self.bundle_base, 2)
        bundle_version.assert_called_with(self.bundle_base,
                                          this_bundle_version=2,
                                          previously_bundled=True)
        cache_version.assert_called_with(self.bundle_base,
                                         previously_bundled=True)
        bundle_tool.assert_called_with(self.bundle_base)