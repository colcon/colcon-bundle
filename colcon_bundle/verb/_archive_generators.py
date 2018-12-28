import os
import shutil
import tarfile

from colcon_bundle.verb import logger
from colcon_bundle.verb.utilities import rewrite_catkin_package_path, \
    update_shebang, update_symlinks


def generate_archive(install_base,
                     staging_path,
                     bundle_base):
    """
    Generate bundle archive.

    :param install_base: Directory with built artifacts from the workspace
    :param staging_path: Directory where all dependencies have been installed
    :param bundle_base: Directory to place the output of this function
    """
    logger.info('Copying {} into bundle...'.format(install_base))
    bundle_workspace_install_path = os.path.join(
        staging_path, 'opt', 'install')
    if os.path.exists(bundle_workspace_install_path):
        shutil.rmtree(bundle_workspace_install_path)
    shutil.copytree(install_base, bundle_workspace_install_path)

    update_symlinks(staging_path)
    # TODO: Update pkgconfig files?
    update_shebang(staging_path)
    # TODO: Move this to colcon-ros-bundle
    rewrite_catkin_package_path(staging_path)

    # Bundle setup shell scripts
    # TODO: Make this a plugin
    assets_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'assets')
    shellscript_path = os.path.join(assets_directory, 'setup.sh')
    shutil.copy2(shellscript_path, staging_path)

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

    with tarfile.open(bundle_tar_path, 'w') as bundle_tar:
        logger.info(
            'Creating tar of {path}'.format(path=staging_path))
        for name in os.listdir(staging_path):
            some_path = os.path.join(staging_path, name)
            bundle_tar.add(some_path, arcname=os.path.basename(some_path))

    with tarfile.open(
            archive_tar_gz_path, 'w:gz', compresslevel=5) as archive:
        assets_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets')
        archive.add(
            os.path.join(assets_directory, 'version'), arcname='version')
        archive.add(
            metadata_tar_path, arcname=os.path.basename(metadata_tar_path))
        archive.add(
            bundle_tar_path, arcname=os.path.basename(bundle_tar_path))

    os.remove(metadata_tar_path)
    os.remove(bundle_tar_path)

    logger.info('Archiving complete')
