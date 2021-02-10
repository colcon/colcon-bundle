import os
from pathlib import Path
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
    ws_install_path = Path(workspace_staging_path) / 'opt' / 'built_workspace'

    shutil.rmtree(workspace_staging_path, ignore_errors=True)

    # install_base: Directory with built artifacts from the workspace
    os.mkdir(workspace_staging_path)

    shellscript_dest = Path(workspace_staging_path) / 'setup.sh'
    _render_template(
        Path('v2_workspace_setup.jinja2.sh'),
        shellscript_dest,
        _CONTEXT_VAR_SH
    )
    shellscript_dest.chmod(0o755)

    shellscript_dest_bash = Path(workspace_staging_path) / 'setup.bash'
    _render_template(
        Path('v2_workspace_setup.jinja2.sh'),
        shellscript_dest_bash,
        _CONTEXT_VAR_BASH
    )
    shellscript_dest_bash.chmod(0o755)

    shutil.copytree(install_base, str(ws_install_path))

    # This is required because python3 shell scripts use a hard
    # coded shebang
    update_shebang(workspace_staging_path)

    recursive_tar_gz_in_path(Path(overlay_path), Path(workspace_staging_path))


def create_dependencies_overlay(staging_path: str, overlay_path: str):
    """
    Create the dependencies overlay from staging_path.

    :param str staging_path: Path where all the dependencies
    have been installed/extracted to
    :param str overlay_path: Path of overlay output file
    (.tar.gz)
    """
    dep_staging_path = Path(staging_path)
    dep_tar_gz_path = Path(overlay_path)
    logger.info('Dependencies changed, updating {}'.format(
        str(dep_tar_gz_path)
    ))

    shellscript_dest = Path(dep_staging_path) / 'setup.sh'
    _render_template(
        Path('v2_setup.jinja2.sh'),
        shellscript_dest,
        _CONTEXT_VAR_SH
    )
    shellscript_dest.chmod(0o755)

    shellscript_dest_bash = Path(dep_staging_path) / 'setup.bash'
    _render_template(
        Path('v2_setup.jinja2.sh'),
        shellscript_dest_bash,
        _CONTEXT_VAR_BASH
    )
    shellscript_dest_bash.chmod(0o755)

    if dep_tar_gz_path.exists():
        dep_tar_gz_path.unlink()
    recursive_tar_gz_in_path(dep_tar_gz_path, dep_staging_path)


def recursive_tar_gz_in_path(output_path: Path, tar_path: Path):
    """
    Create a tar.gz archive of all files inside a directory.

    This function includes all sub-folders of path in the root of the tarfile

    :param output_path: Name of archive file to create
    :param tar_path: path to recursively collect all files and include in
    tar.gz. These will be included with path as the root of the archive.
    """
    with tarfile.open(str(output_path), mode='w:gz', compresslevel=5) as tar:
        logger.info(
            'Creating tar of {path}'.format(path=tar_path))
        for child in tar_path.iterdir():
            tar.add(str(child), arcname=str(child.name))


def _render_template(template_name: Path,
                     script_dest: Path,
                     context_vars: dict):
    """
    Render setup.bash or setup.sh files from template.

    This assumes the template is in the assets folder.

    :param template_name: Name of the template to be used
    :param script_dest: path of the script to be rendered
    :param context_vars: dictionary of values to be used for the variables in
    the template
    """
    src = Path(__file__).parent.absolute() / 'assets' / template_name
    env = Environment(
        autoescape=select_autoescape(['html', 'xml']),
        loader=FileSystemLoader(str(src.parent)),
        keep_trailing_newline=True,
    )
    template = env.get_template(str(src.name))

    with script_dest.open('w') as file:
        file.write(template.render(context_vars))
    script_dest.chmod(script_dest.stat().st_mode | stat.S_IEXEC)
