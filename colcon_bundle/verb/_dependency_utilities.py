import hashlib
import json
import os
from typing import List

from colcon_bundle.verb import logger
from colcon_bundle.verb._path_context import PathContext
from colcon_core.package_decorator import PackageDecorator


def update_dependencies_cache(path_context: PathContext):
    """
    Promote the latest set of logged dependencies.

    This method takes the set of the dependencies
    that were last logged by package_dependencies_changed
    and updates the cache with them.

    We use this method because when we run package_dependencies_changed
    we do not want to actually update the cache yet because the latest
    dependencies overlay has not been built. Once the dependencies
    overlay is built we then call this.

    :param path_context: paths to use
    """
    dependency_hash_path = path_context.dependency_hash_path()
    dependency_hash_cache_path = path_context.dependency_hash_cache_path()
    if os.path.exists(dependency_hash_cache_path):
        os.replace(dependency_hash_cache_path, dependency_hash_path)


def package_dependencies_changed(path_context: PathContext,
                                 decorators: List[PackageDecorator]):
    """
    Determine if workspace package dependencies have changed.

    Compares the direct dependencies of the provided decorators against the
    dependencies that were found in the invocation of this method. This does
    not take in to account transitive dependency updates coming from
    installers.

    :param PathContext path_context: paths to use
    :param PackageDecorators decorators: decorators that should be used to
    compare dependencies
    :return bool: True if package dependencies have changed
    """
    dependency_hash = {}

    for decorator in decorators:
        if not decorator.selected:
            continue
        pkg = decorator.descriptor
        dependency_list = sorted(str(dependency) for dependency in
                                 pkg.dependencies['run'])
        dependency_hash[pkg.name] = hashlib.sha256(
            ' '.join(dependency_list).encode('utf-8')).hexdigest()

    current_hash_string = json.dumps(dependency_hash, sort_keys=True)
    logger.debug('Hash for current dependencies: '
                 '{current_hash_string}'.format_map(locals()))

    dependency_hash_path = path_context.dependency_hash_path()
    dependency_hash_cache_path = path_context.dependency_hash_cache_path()

    dependencies_changed = False
    if os.path.exists(dependency_hash_path):
        with open(dependency_hash_path, 'r') as f:
            previous_hash_string = f.read()
            if previous_hash_string != current_hash_string:
                dependencies_changed = True

    with open(dependency_hash_cache_path, 'w') as f:
        f.write(current_hash_string)

    return not os.path.exists(dependency_hash_path) or dependencies_changed
