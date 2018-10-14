from unittest.mock import patch
from tempfile import mkdtemp
import shutil
import os

from colcon_bundle.installer import BundleInstallerContext
from colcon_bundle.installer.pip3 import Pip3BundleInstallerExtensionPoint


def test_install_nothing():
    installer = Pip3BundleInstallerExtensionPoint()
    context = BundleInstallerContext(
        args=None, cache_path=None, prefix_path=None)
    installer.initialize(context)
    result = installer.install()
    assert result == {'message': 'No dependencies installed...'}


@patch('subprocess.check_call')
def test_install(check_call):
    installer = Pip3BundleInstallerExtensionPoint()
    cache_dir = mkdtemp()
    prefix = mkdtemp()
    python_path = os.path.join(prefix, 'usr', 'bin', 'python3')
    context = BundleInstallerContext(
        args=None, cache_path=cache_dir, prefix_path=prefix)
    try:
        installer.initialize(context)
        installer.add_to_install_list('pkg1==3.4.5')
        installer.add_to_install_list('pkg2>=3.1.2')
        installer.add_to_install_list('remove_me')
        installer.remove_from_install_list('remove_me')
        result = installer.install()

        args_list = check_call.call_args_list
        args = args_list[0][0][0]
        assert args[0] == python_path
        # Ensure we upgrade pip/setuptools
        assert args[1:] == ['-m', 'pip', 'install', '-U', 'pip', 'setuptools']

        args = args_list[1][0][0]
        assert args[0] == python_path
        assert args[1:-1] == [
            '-m', 'pip', 'install', '--ignore-installed', '-r']

        assert result == {
            'requirements': ['pkg1==3.4.5', 'pkg2>=3.1.2']
        }
    finally:
        shutil.rmtree(cache_dir)
        shutil.rmtree(prefix)


