from unittest.mock import patch, Mock, mock_open
from tempfile import mkdtemp
import shutil
import os

from colcon_bundle.installer import BundleInstallerContext
from colcon_bundle.installer.pip import PipBundleInstallerExtensionPoint


def test_install_nothing():
    installer = PipBundleInstallerExtensionPoint()
    cache_dir = mkdtemp()
    prefix = mkdtemp()
    context_args = Mock()
    context_args.pip_requirements = None
    context = BundleInstallerContext(
        args=context_args, cache_path=cache_dir, prefix_path=prefix)
    installer.initialize(context)
    result = installer.install()
    assert result == {'installed_packages': []}


@patch('subprocess.check_call')
@patch('subprocess.check_output')
def test_install(check_output, check_call):
    installer = PipBundleInstallerExtensionPoint()
    cache_dir = mkdtemp()
    prefix = mkdtemp()
    python_path = os.path.join(prefix, 'usr', 'bin', 'python2')
    context_args = Mock()
    context_args.pip_args = []
    context_args.pip_requirements = None
    context = BundleInstallerContext(
        args=context_args, cache_path=cache_dir, prefix_path=prefix)
    check_output.return_value = 'pkg1==3.4.5\npkg2==3.1.2\n'
    try:
        installer.initialize(context)
        installer.add_to_install_list('pkg1==3.4.5')
        installer.add_to_install_list('pkg2>=3.1.2')
        installer.add_to_install_list('remove_me')
        installer.remove_from_install_list('remove_me')
        result = installer.install()

        assert result == {
            'installed_packages': [
                {
                    'name': 'pkg1',
                    'version': '3.4.5'
                },
                {
                    'name': 'pkg2',
                    'version': '3.1.2'
                }
            ]
        }
    finally:
        shutil.rmtree(cache_dir)
        shutil.rmtree(prefix)


@patch('subprocess.check_call')
@patch('subprocess.check_output')
def test_install_with_additional_arguments(check_output, check_call):
    installer = PipBundleInstallerExtensionPoint()
    cache_dir = mkdtemp()
    prefix = mkdtemp()
    python_path = os.path.join(prefix, 'usr', 'bin', 'python2')
    context_args = Mock()
    context_args.pip_args = [' --test-arg-1', '--test-arg-2']
    context_args.pip_requirements = None
    context = BundleInstallerContext(
        args=context_args, cache_path=cache_dir, prefix_path=prefix)
    check_output.return_value = 'pkg1==3.4.5\npkg2==3.1.2\n'
    try:
        installer.initialize(context)
        installer.add_to_install_list('pkg1==3.4.5')
        installer.add_to_install_list('pkg2>=3.1.2')
        installer.add_to_install_list('remove_me')
        installer.remove_from_install_list('remove_me')
        result = installer.install()

        assert result == {
            'installed_packages': [
                {
                    'name': 'pkg1',
                    'version': '3.4.5'
                },
                {
                    'name': 'pkg2',
                    'version': '3.1.2'
                }
            ]
        }
    finally:
        shutil.rmtree(cache_dir)
        shutil.rmtree(prefix)

@patch('subprocess.check_call')
@patch('subprocess.check_output')
def test_install_not_required(check_output, check_call):
    installer = PipBundleInstallerExtensionPoint()
    cache_dir = mkdtemp()

    prefix = mkdtemp()
    python_path = os.path.join(prefix, 'usr', 'bin', 'python2')
    context_args = Mock()
    context_args.pip_args = []
    context_args.pip_requirements = None
    context = BundleInstallerContext(
        args=context_args, cache_path=cache_dir, prefix_path=prefix)
    check_output.return_value = 'pkg1==3.4.5\npkg2==3.1.2\n'
    try:
        installer.initialize(context)
        installer.add_to_install_list('pkg1==3.4.5')
        installer.add_to_install_list('pkg2>=3.1.2')
        installer.add_to_install_list('remove_me')
        installer.remove_from_install_list('remove_me')
        result = installer.install()

        assert result == {
            'installed_packages': [
                {
                    'name': 'pkg1',
                    'version': '3.4.5'
                },
                {
                    'name': 'pkg2',
                    'version': '3.1.2'
                }
            ]
        }

        result_2 = installer.install()
        assert result == result_2
        # Verify we haven't called pip
        assert check_call.call_count == 4
        # Verify we haven't called pip freeze
        assert check_output.call_count == 1
    finally:
        shutil.rmtree(cache_dir)
        shutil.rmtree(prefix)


@patch('subprocess.check_call')
@patch('subprocess.check_output')
@patch('builtins.open', mock_open(read_data='rpkg==1.2.3'))
def test_install_addtional_requirements(check_output, check_call):
    """
    This test should be mocking the read and write to the file
    and then reading the requirements file. Instead I am just
    checking the packages array after the install to verify
    the "requrements.txt" was read and added to the list.
    """
    installer = PipBundleInstallerExtensionPoint()
    cache_dir = mkdtemp()
    prefix = mkdtemp()
    python_path = os.path.join(prefix, 'usr', 'bin', 'python2')
    context_args = Mock()
    context_args.pip_args = []
    context_args.pip_requirements = 'requirements.txt'
    context = BundleInstallerContext(
        args=context_args, cache_path=cache_dir, prefix_path=prefix)
    check_output.return_value = 'pkg1==3.4.5\npkg2==3.1.2\nrpkg==1.2.3\n'
    try:
        installer.initialize(context)
        installer.add_to_install_list('pkg1==3.4.5')
        installer.add_to_install_list('pkg2==3.1.2')

        result = installer.install()
        assert installer._packages == [
            'pkg1==3.4.5', 'pkg2==3.1.2', 'rpkg==1.2.3'
        ]

        assert result == {
            'installed_packages': [
                {
                    'name': 'pkg1',
                    'version': '3.4.5'
                },
                {
                    'name': 'pkg2',
                    'version': '3.1.2'
                },
                {
                    'name': 'rpkg',
                    'version': '1.2.3'
                }
            ]
        }
    finally:
        shutil.rmtree(cache_dir)
        shutil.rmtree(prefix)
