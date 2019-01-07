import os
import shutil
import tarfile

from colcon_bundle.verb import logger
from colcon_bundle.verb.bundlefile import Bundle


def generate_archive_v1(install_base,
                        staging_path,
                        bundle_base):
    """
    Generate bundle archive.

    output.tar.gz
    |- version
    |- metadata.tar
    |- bundle.tar

    :param install_base: Directory with built artifacts from the workspace
    :param staging_path: Directory where all dependencies have been installed
    :param bundle_base: Directory to place the output of this function
    """
    logger.info('Copying {} into bundle...'.format(install_base))
    assets_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'assets')
    shellscript_path = os.path.join(assets_directory, 'v1_setup.sh')
    shutil.copy2(shellscript_path, os.path.join(staging_path, 'setup.sh'))
    bundle_workspace_install_path = os.path.join(
        staging_path, 'opt', 'install')
    if os.path.exists(bundle_workspace_install_path):
        shutil.rmtree(bundle_workspace_install_path)
    shutil.copytree(install_base, bundle_workspace_install_path)

    logger.info('Archiving the bundle output')
    print('Creating bundle archive...')

    bundle_tar_path = os.path.join(bundle_base, 'bundle.tar')
    metadata_tar_path = os.path.join(bundle_base, 'metadata.tar')
    archive_tar_gz_path = os.path.join(bundle_base, 'output.tar.gz')

    with tarfile.open(metadata_tar_path, 'w') as archive:
        archive.add(os.path.join(bundle_base, 'installer_metadata.json'),
                    arcname='installers.json')

    if os.path.exists(bundle_tar_path):
        os.remove(bundle_tar_path)

    _recursive_tar_in_path(bundle_tar_path, staging_path)

    version_file_path = os.path.join(bundle_base, 'version')
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


def generate_archive_v2(install_base,
                        dependencies_staging_path,
                        bundle_base,
                        metadata_paths,
                        dependencies_changed):
    """
    Generate bundle archive v2.

    This archive is a tarfile that contains multiple compressed archives:

    output.tar
    |- version
    |- metadata.tar.gz
    |- pad (optional)
    |- dependencies.tar.gz
    |- workspace.tar.gz

    :param install_base: Directory with built artifacts from the workspace
    :param dependencies_staging_path: Directory where all dependencies
    have been installed
    :param bundle_base: Directory to place the output of this function
    :param metadata_paths: [str] paths to files which should be included
    in the metadata archive
    :param dependencies_changed: Boolean representing whether the staging path
    needs to be re-archvied
    """
    logger.info('Archiving the bundle output')
    print('Creating bundle archive V2...')

    archive_tar_path = os.path.join(bundle_base, 'output.tar')
    workspace_tar_gz_path = os.path.join(bundle_base, 'workspace.tar.gz')

    # Install directory
    workspace_staging_path = os.path.join(bundle_base, 'workspace_staging')
    workspace_install_path = os.path.join(
        workspace_staging_path, 'opt', 'built_workspace')
    shutil.rmtree(workspace_staging_path, ignore_errors=True)
    assets_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'assets')

    shellscript_path = os.path.join(assets_directory, 'v2_workspace_setup.sh')
    os.mkdir(workspace_staging_path)
    shutil.copy2(shellscript_path,
                 os.path.join(workspace_staging_path, 'setup.sh'))
    shutil.copytree(install_base, workspace_install_path)
    _recursive_tar_in_path(workspace_tar_gz_path, workspace_staging_path,
                           mode='w:gz')

    # Dependencies directory
    dependencies_tar_gz_path = os.path.join(bundle_base, 'dependencies.tar.gz')
    if dependencies_changed:
        logger.info('Dependencies changed, updating {}'.format(
            dependencies_tar_gz_path
        ))
        assets_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets')
        shellscript_path = os.path.join(assets_directory, 'v2_setup.sh')
        shutil.copy2(shellscript_path,
                     os.path.join(dependencies_staging_path, 'setup.sh'))
        if os.path.exists(dependencies_tar_gz_path):
            os.remove(dependencies_tar_gz_path)
        _recursive_tar_in_path(dependencies_tar_gz_path,
                               dependencies_staging_path,
                               mode='w:gz')

    with Bundle(name=archive_tar_path) as bundle:
        for path in metadata_paths:
            bundle.add_metadata(path)
        bundle.add_overlay_archive(dependencies_tar_gz_path)
        bundle.add_overlay_archive(workspace_tar_gz_path)

    logger.info('Archiving complete')
    print('Archiving complete!')


def _recursive_tar_in_path(tar_path, path, *, mode='w'):
    """
    Tar all files inside a directory.

    This function includes all sub-folders of path in the root of the tarfile

    :param tar_path: The output path
    :param path: path to recursively collect all files and include in
    tar
    :param mode: mode flags passed to tarfile
    """
    with tarfile.open(tar_path, mode) as tar:
        logger.info(
            'Creating tar of {path}'.format(path=path))
        for name in os.listdir(path):
            some_path = os.path.join(path, name)
            tar.add(some_path, arcname=os.path.basename(some_path))
