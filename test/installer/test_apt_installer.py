import os
import shutil
import sys
from tempfile import mkdtemp, mkstemp
from unittest import mock

import unittest
from unittest.mock import patch, Mock

from colcon_bundle.installer.apt import AptBundleInstallerExtension
from colcon_bundle.installer import BundleInstallerContext


class AptInstallerTests(unittest.TestCase):
    @patch('colcon_bundle.installer.apt.get_ubuntu_distribution_version')
    def test_should_load_not_on_ubuntu(self, get_version):
        apt = AptBundleInstallerExtension()
        get_version.side_effect = ValueError()
        assert apt.should_load() == False

    @patch('colcon_bundle.installer.apt.get_ubuntu_distribution_version')
    def test_should_load_on_ubuntu(self, _):
        with patch.dict("sys.modules", apt=mock.MagicMock()):
            apt = AptBundleInstallerExtension()
            assert apt.should_load() == True

    @patch('colcon_bundle.installer.apt.get_ubuntu_distribution_version')
    def test_should_load_on_ubuntu_no_python3_apt(self, _):
        with patch.dict("sys.modules", apt=None):
            apt = AptBundleInstallerExtension()
            with self.assertRaises(RuntimeError): apt.should_load()

    def test_apt_add_to_install_list_splits_version_specifier(self):
        # We import apt inside the method it is used so we can't @patch it like
        # a normal import
        apt = mock.MagicMock()
        with patch.dict("sys.modules", apt=apt):
            package_name = "foo"
            package_version = "1.3.4"
            cache_dir = mkdtemp()
            prefix = mkdtemp()
            _, sources_list = mkstemp()
            try:
                context_args = Mock()
                context_args.apt_sources_list = sources_list
                context = BundleInstallerContext(args=context_args, cache_path=cache_dir, prefix_path=prefix)
                installer = AptBundleInstallerExtension()

                installer.initialize(context)

                package_mock = mock.MagicMock()
                apt.Cache().__getitem__.return_value = package_mock
                candidate_mock = mock.MagicMock()
                package_mock.versions.get.return_value = candidate_mock

                installer.add_to_install_list(package_name + "=" + package_version)

                apt.Cache().__getitem__.assert_called_with(package_name)
                package_mock.versions.get.assert_called_with(package_mock.versions[package_version])
                self.assertEqual(package_mock.candidate, candidate_mock)
                package_mock.mark_install.assert_called_with(auto_fix=False, from_user=False)
            finally:
                shutil.rmtree(cache_dir)
                shutil.rmtree(prefix)
                os.remove(sources_list)
