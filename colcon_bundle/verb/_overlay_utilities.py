import os
import shutil
import stat
import tarfile

from colcon_bundle.verb import logger
from colcon_bundle.verb.utilities import \
    update_shebang
from jinja2 import \
    Environment, \
    FileSystemLoader, \
    select_autoescape


_CONTEXT_VAR_BASH = {'shell': 'bash'}
_CONTEXT_VAR_SH = {'shell': 'sh'}


def create_workspace_overlay(install_base: str,
                             workspace_staging_path: str,
                             overlay_path: str):
    """
    Create overlay from user's built workspace install directory.

    :param str install_base: Path to built workspace install directory
    :param str workspace_staging_path: Path to stage the overlay build at
    :param str overlay_path: Name of the overlay file (.tar.gz)
    """
    _generate_template(
        'v2_workspace_setup.jinja2.sh',
        'v2_workspace_setup.bash',
        _CONTEXT_VAR_BASH
    )

    _generate_template(
        'v2_workspace_setup.jinja2.sh',
        'v2_workspace_setup.sh',
        _CONTEXT_VAR_SH
    )
    workspace_install_path = os.path.join(
        workspace_staging_path, 'opt', 'built_workspace')
    shutil.rmtree(workspace_staging_path, ignore_errors=True)
    assets_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'assets')

    shellscript_path = os.path.join(
        assets_directory,
        'v2_workspace_setup.sh'
    )
    shellscript_path_bash = os.path.join(
        assets_directory,
        'v2_workspace_setup.bash'
    )

    # install_base: Directory with built artifacts from the workspace
    os.mkdir(workspace_staging_path)
    shutil.copy2(shellscript_path,
                 os.path.join(workspace_staging_path, 'setup.sh'))
    os.chmod(os.path.join(workspace_staging_path, 'setup.sh'), 0o777)
    shutil.copy2(shellscript_path_bash,
                 os.path.join(workspace_staging_path, 'setup.bash'))
    os.chmod(os.path.join(workspace_staging_path, 'setup.bash'), 0o777)

    shutil.copytree(install_base, workspace_install_path)

    # This is required because python3 shell scripts use a hard
    # coded shebang
    update_shebang(workspace_staging_path)

    recursive_tar_gz_in_path(overlay_path,
                             workspace_staging_path)


def create_dependencies_overlay(staging_path, overlay_path):
    """
    Create the dependencies overlay from staging_path.

    :param str staging_path: Path where all the dependencies
    have been installed/extracted to
    :param str overlay_path: Path of overlay output file
    (.tar.gz)
    """
    dependencies_staging_path = staging_path
    dependencies_tar_gz_path = overlay_path
    logger.info('Dependencies changed, updating {}'.format(
        dependencies_tar_gz_path
    ))

    assets_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'assets')

    _generate_template(
        assets_directory,
        os.path.join(assets_directory, 'v2_setup.jinja2.sh'),
        os.path.join(assets_directory, 'v2_setup.bash'),
        _CONTEXT_VAR_BASH
    )

    _generate_template(
        assets_directory,
        os.path.join(assets_directory, 'v2_setup.jinja2.sh'),
        os.path.join(assets_directory, 'v2_setup.bash'),
        _CONTEXT_VAR_BASH
    )

    shellscript_path = os.path.join(assets_directory, 'v2_setup.sh')
    shutil.copy2(shellscript_path,
                 os.path.join(dependencies_staging_path, 'setup.sh'))
    os.chmod(os.path.join(dependencies_staging_path, 'setup.sh'), 0o777)
    shellscript_path_bash = os.path.join(
        assets_directory,
        'v2_setup.bash'
    )
    shutil.copy2(shellscript_path_bash,
                 os.path.join(dependencies_staging_path, 'setup.bash'))
    os.chmod(os.path.join(dependencies_staging_path, 'setup.bash'), 0o777)
    if os.path.exists(dependencies_tar_gz_path):
        os.remove(dependencies_tar_gz_path)
    recursive_tar_gz_in_path(dependencies_tar_gz_path,
                             dependencies_staging_path)


def recursive_tar_gz_in_path(output_path, path):
    """
    Create a tar.gz archive of all files inside a directory.

    This function includes all sub-folders of path in the root of the tarfile

    :param output_path: Name of archive file to create
    :param path: path to recursively collect all files and include in
    tar.gz. These will be included with path as the root of the archive.
    """
    with tarfile.open(output_path, mode='w:gz', compresslevel=5) as tar:
        logger.info(
            'Creating tar of {path}'.format(path=path))
        for name in os.listdir(path):
            some_path = os.path.join(path, name)
            tar.add(some_path, arcname=os.path.basename(some_path))


def _generate_template(asset, src, dest, context_vars: dict):
    """
    Render a jinja2 template to a location.
    """
    env = Environment(
        autoescape=select_autoescape(['html', 'xml']),
        loader=FileSystemLoader(asset),
        keep_trailing_newline=True,
    )
    template = env.get_template(src)
    with open(dest, 'w') as file:
        file.write(template.render(context_vars))
    os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC)
