import logging
from unittest.mock import call, MagicMock
import pytest

from colcon_bundle.task.python.bundle import PythonBundleTask
from colcon_bundle.verb.bundle import BundlePackageArguments
from colcon_core.dependency_descriptor import DependencyDescriptor
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.task import TaskContext


@pytest.mark.asyncio
async def test_bundle():
    logging.disable(logging.CRITICAL)
    descriptor = PackageDescriptor('some/path')
    descriptor.name = 'python_package'
    deps = [DependencyDescriptor('pkg1', metadata={'version_eq': '1.3.2'}),
            DependencyDescriptor('pkg_in_workspace'),
            DependencyDescriptor('pkg2', metadata={'version_lt': '1.2'}),
            'ignored_pkg']
    descriptor.dependencies['run'] = deps

    workspace = {'pkg_in_workspace': 'path/to/pkg'}
    task_args = MagicMock(build_base='build/base',
                          install_base='install/base',
                          bundle_base='bundle/base')
    pip_installer = MagicMock()
    apt_installer = MagicMock()
    args = BundlePackageArguments(
        descriptor, {'pip3': pip_installer, 'apt': apt_installer}, task_args)
    context = TaskContext(pkg=descriptor, args=args, dependencies=workspace)
    task = PythonBundleTask()
    task.set_context(context=context)

    await task.bundle()

    pip_installer.add_to_install_list.assert_has_calls([call('pkg1==1.3.2'), call('pkg2<1.2')])

    apt_calls = apt_installer.add_to_install_list.call_args_list
    assert len(apt_calls) == 4
    assert apt_calls[0][0][0] == 'libpython3-dev'
    assert apt_calls[1][0][0] == 'python3-pip'
    logging.disable(logging.CRITICAL)


def test_add_arguments():
    task = PythonBundleTask()
    task.add_arguments(parser=None)
