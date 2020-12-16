import os
import shutil
import tarfile
from typing import List

from colcon_bundle.verb import logger
from colcon_bundle.verb._dependency_utilities import update_dependencies_cache
from colcon_bundle.verb._overlay_utilities import \
    create_dependencies_overlay, create_workspace_overlay
from colcon_bundle.verb._path_context import PathContext
from colcon_bundle.verb.bundlefile import Bundle


def generate_archive_v1(path_context):
    """
    Generate bundle archive.

    output.tar.gz
    |- version
    |- metadata.tar
    |- bundle.tar

    :param path_context: PathContext object including path configurations
    """
    # install_base: Directory with built artifacts from the workspace
    install_base = path_context.install_base()
    # staging_path: Directory where all dependencies have been installed
    staging_path = path_context.dependencies_staging_path()

    logger.info('Copying {} into bundle...'.format(install_base))
    assets_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'assets')
    shellscript_path = os.path.join(assets_directory, 'v1_setup.sh')
    shutil.copy2(shellscript_path, os.path.join(staging_path, 'setup.sh'))
    os.chmod(os.path.join(staging_path, 'setup.sh'), 0o755)
    bundle_workspace_install_path = os.path.join(
        staging_path, 'opt', 'install')
    if os.path.exists(bundle_workspace_install_path):
        shutil.rmtree(bundle_workspace_install_path)
    shutil.copytree(install_base, bundle_workspace_install_path)

    logger.info('Archiving the bundle output')
    print('Creating bundle archive...')

    bundle_tar_path = path_context.bundle_tar_path()
    metadata_tar_path = path_context.metadata_tar_path()
    archive_tar_gz_path = path_context.bundle_v1_output_path()

    with tarfile.open(metadata_tar_path, 'w') as archive:
        archive.add(path_context.installer_metadata_path(),
                    arcname='installers.json')

    if os.path.exists(bundle_tar_path):
        os.remove(bundle_tar_path)

    recursive_tar_in_path(bundle_tar_path, staging_path)

    version_file_path = path_context.version_file_path()
    with open(version_file_path, 'w') as v:
        v.write('1')

    with tarfile.open(
            archive_tar_gz_path, 'w:gz', compresslevel=5) as archive:
        archive.add(
            version_file_path, arcname='version')
        archive.add(
            metadata_tar_path, arcname=os.path.basename(metadata_tar_path))
        archive.add(
            bundle_tar_path, arcname=os.path.basename(bundle_tar_path))

    os.remove(metadata_tar_path)
    os.remove(bundle_tar_path)

    logger.info('Archiving complete')


def generate_archive_v2(path_context: PathContext,
                        metadata_paths: List[str],
                        dependencies_changed: bool):
    """
    Generate bundle archive v2.

    This archive is a tarfile that contains multiple compressed archives:

    output.tar
    |- version
    |- metadata.tar.gz
    |- pad (optional)
    |- dependencies.tar.gz
    |- workspace.tar.gz

    :param path_context: PathContext object including all path configurations
    :param metadata_paths: [str] paths to files which should be included
    in the metadata archive
    :param dependencies_changed: Boolean representing whether the staging path
    needs to be re-archvied
    """
    logger.info('Archiving the bundle output')
    print('Creating bundle archive V2...')
    logger.debug('Start: workspace.tar.gz')
    workspace_tar_gz_path = path_context.workspace_overlay_path()
    create_workspace_overlay(path_context.install_base(),
                             path_context.workspace_staging_path(),
                             workspace_tar_gz_path)
    logger.debug('End: workspace.tar.gz')

    logger.debug('Start: dependencies.tar.gz')
    dependencies_overlay_path = path_context.dependencies_overlay_path()
    if dependencies_changed:
        create_dependencies_overlay(path_context.dependencies_staging_path(),
                                    dependencies_overlay_path)
        update_dependencies_cache(path_context)
    logger.debug('End: dependencies.tar.gz')

    logger.debug('Start: bundle.tar')
    with Bundle(name=path_context.bundle_v2_output_path()) as bundle:
        for path in metadata_paths:
            bundle.add_metadata(path)
        bundle.add_overlay_archive(dependencies_overlay_path)
        bundle.add_overlay_archive(workspace_tar_gz_path)
    logger.debug('End: bundle.tar')

    logger.info('Archiving complete')
    print('Archiving complete!')
    _mark_cache_valid(path_context)


def _mark_cache_valid(path_context):
    cache_valid_file = path_context.cache_valid_path()
    with open(cache_valid_file, 'a'):
        os.utime(cache_valid_file)


def recursive_tar_in_path(tar_path, path):
    """
    Tar all files inside a directory.

    This function includes all sub-folders of path. Path
    is treated as the root of the tarfile.

    :param tar_path: The output path
    :param path: path to recursively collect all files and include in
    tar
    mode type
    """
    with tarfile.open(tar_path, mode='w') as tar:
        logger.info(
            'Creating tar of {path}'.format(path=path))
        for name in os.listdir(path):
            some_path = os.path.join(path, name)
            tar.add(some_path, arcname=os.path.basename(some_path))
