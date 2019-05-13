import shutil
import tempfile
from unittest import TestCase

from colcon_bundle.verb._dependency_utilities import \
    package_dependencies_changed, update_dependencies_cache
from colcon_bundle.verb._path_context import PathContext
from colcon_core.dependency_descriptor import DependencyDescriptor
from colcon_core.package_decorator import PackageDecorator
from colcon_core.package_descriptor import PackageDescriptor


class TestBundlefile(TestCase):
    def setUp(self) -> None:
        self.bundle_base = tempfile.mkdtemp()
        self.install_base = tempfile.mkdtemp()
        shutil.rmtree(self.bundle_base)
        self.path_context = PathContext(self.install_base,
                                        self.bundle_base,
                                        2)

    def tearDown(self) -> None:
        shutil.rmtree(self.install_base)
        shutil.rmtree(self.bundle_base)

    def test_dependencies_not_changed(self):
        package_1_desc = PackageDescriptor('fake/path')
        package_1_desc.name = 'baz'
        package_1_desc.dependencies['run'] = ['foo']
        package_1_desc.dependencies['test'] = ['bar']
        package_1 = PackageDecorator(package_1_desc)
        decorators = [package_1]
        self.assertTrue(package_dependencies_changed(
            self.path_context,
            decorators
        ))
        update_dependencies_cache(self.path_context)
        self.assertFalse(package_dependencies_changed(
            self.path_context,
            decorators
        ))

    def test_dependencies_changed(self):
        package_1_desc = PackageDescriptor('fake/path')
        package_1_desc.name = 'package1'
        package_1_desc.dependencies['run'] = [
            DependencyDescriptor('foo')]
        package_1 = PackageDecorator(package_1_desc)
        decorators = [package_1]
        self.assertTrue(package_dependencies_changed(
            self.path_context,
            decorators
        ))
        update_dependencies_cache(self.path_context)
        package_1_desc.dependencies['run'] = [
            DependencyDescriptor('foo'),
            'baz']
        package_1 = PackageDecorator(package_1_desc)
        decorators = [package_1]
        self.assertTrue(package_dependencies_changed(
            self.path_context,
            decorators
        ))