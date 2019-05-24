import sys
from unittest import mock

import unittest
from mock import patch

from colcon_bundle.installer.apt import AptBundleInstallerExtension


class AptInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp_apt = sys.modules.get('apt', None)
    
    def tearDown(self):
        sys.modules['apt'] = self.tmp_apt

    @patch('colcon_bundle.installer.apt.get_ubuntu_distribution_version')
    def test_should_load_not_on_ubuntu(self, get_version):
        apt = AptBundleInstallerExtension()
        get_version.side_effect = ValueError()
        assert apt.should_load() == False

    @patch('colcon_bundle.installer.apt.get_ubuntu_distribution_version')
    def test_should_load_on_ubuntu(self, _):
        sys.modules['apt'] = mock.MagicMock()
        apt = AptBundleInstallerExtension()
        assert apt.should_load() == True

    @patch('colcon_bundle.installer.apt.get_ubuntu_distribution_version')
    def test_should_load_on_ubuntu_no_python3_apt(self, _):
        sys.modules['apt'] = None
        apt = AptBundleInstallerExtension()
        with self.assertRaises(RuntimeError): apt.should_load()

