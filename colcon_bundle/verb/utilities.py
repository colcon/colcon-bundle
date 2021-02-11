# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import hashlib
import itertools
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from colcon_bundle.verb import logger

ENV_COMMAND = 'env'


def get_ros_distribution_version():
    """
    Discover and return ROS distribution version.

    :return: the ROS distribution version to be used.
    example: kinetic, melodic
    """
    ros_distribution_version = 'kinetic'
    if get_ubuntu_distribution_version() == 'bionic':
        ros_distribution_version = 'melodic'
    elif get_ubuntu_distribution_version() == 'focal':
        ros_distribution_version = 'noetic'
    return ros_distribution_version


def get_ubuntu_distribution_version():
    """
    Discover and return Ubuntu distribution version.

    :return: the Ubuntu distribution version of the build server.
    example: xenial, bionic
    """
    import distro
    distribution = distro.linux_distribution()
    if distribution[0] == 'Ubuntu' and distribution[1] == '16.04':
        return 'xenial'
    elif distribution[0] == 'Ubuntu' and distribution[1] == '18.04':
        return 'bionic'
    elif distribution[0] == 'Ubuntu' and distribution[1] == '20.04':
        return 'focal'
    else:
        raise ValueError('Unsupported distribution', distribution)


def update_shebang(path):
    """
    Search and replace shebangs in path and all sub-paths with /usr/bin/env.

    `env` does not support parameters so parameters are removed.
    Environment variables should be used instead of parameters
    (specifically for Python).

    :param path: Path to directory with files to replace shebang in.
    """
    # Parse the shebang
    shebang_regex = re.compile(r'^#!\s*\S*.')
    # Shebangs in templates are a special case we need to handle.
    # Example: #!@PYTHON_EXECUTABLE@
    template_shebang_regex = re.compile(r'^#!\s*@\S*.@')
    # Parse the command to execute in the shebang
    cmd_regex = re.compile(r'([^\/]*)\/*$')
    logger.info('Starting shebang update...')
    for (root, dirs, files) in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path) and \
                    '.so' not in os.path.basename(file_path) and \
                    'README' not in os.path.basename(file_path):
                with open(file_path, 'rb+') as file_handle:
                    contents = file_handle.read()
                    try:
                        str_contents = contents.decode()
                    except UnicodeError:
                        continue
                    template_shebang_match = template_shebang_regex.match(
                        str_contents)
                    if template_shebang_match:
                        logger.debug('Skipping templated shebang')
                        continue
                    shebang_match = shebang_regex.match(str_contents)
                    if shebang_match:
                        shebang_str = shebang_match.group(0)
                        logger.info('Found shebang in {}'.format(file_path))
                        shebang_command = cmd_regex.search(shebang_str)
                        if not shebang_command:
                            logger.warning(
                              'Unable to find shebang command in {}.'
                              'It may be malformed.'.format(file_path))
                            continue
                        shebang_command = shebang_command.group(0)
                        if shebang_command.strip() == ENV_COMMAND:
                            logger.debug('Valid shebang for {}.'
                                         'Skipping.'.format(file_path))
                            continue
                        logger.info('Modifying shebang for {}'.format(
                            file_path))
                        result, _ = shebang_regex.subn(
                          '#!/usr/bin/env {}'.format(shebang_command),
                          str_contents,
                          count=1
                        )
                        file_handle.seek(0)
                        file_handle.truncate()
                        file_handle.write(result.encode())


def update_symlinks(base_path):
    """
    Update all symlinks inside of base_path to be relative.

    Recurse through the path and update all symlinks to be relative except
    symlinks to libc this is because we want our applications to call into
    the libraries we are bundling. We do not bundle libc and want to use the
    system's version, so we should not update those. Copy any other libraries,
    not found in the bundle, into the bundle so that relative symlinks work.

    :param base_path: Directory that will be recursed
    """
    logger.info('Updating symlinks in {base_path}'.format_map(locals()))
    encoding = sys.getfilesystemencoding()
    dpkg_libc_paths = subprocess.check_output(['dpkg', '-L', 'libc6']).decode(
        encoding).strip()
    libc_paths = set(dpkg_libc_paths.split('\n'))

    for root, subdirs, files in os.walk(base_path):
        for name in itertools.chain(subdirs, files):
            symlink_path = os.path.join(root, name)
            if os.path.islink(symlink_path) and os.path.isabs(
                    os.readlink(symlink_path)):
                symlink_dest_path = os.readlink(symlink_path)
                if symlink_dest_path in libc_paths:
                    # We don't want to update symlinks which are pointing to
                    # libc
                    continue
                else:
                    logger.info(
                        'Symlink: {symlink_path} Points to: {'
                        'symlink_dest_path}'.format_map(locals()))
                    bundle_library_path = os.path.join(base_path,
                                                       symlink_dest_path[1:])
                    if os.path.exists(bundle_library_path):
                        # Dep is already installed, update symlink
                        logger.info(
                            'Linked file is already in bundle at {}, '
                            'updating symlink...'.format(bundle_library_path))
                    else:
                        # Dep is not installed, we need to copy it...
                        logger.info(
                            'Linked file is not in bundle, copying and '
                            'updating symlink...')
                        if not os.path.exists(
                                os.path.dirname(bundle_library_path)):
                            # Create directory (permissions?)
                            os.makedirs(os.path.dirname(bundle_library_path),
                                        exist_ok=True)
                        if os.path.exists(symlink_dest_path):
                            shutil.copy(symlink_dest_path,
                                        bundle_library_path)
                        else:
                            logger.error('Attempted to copy {} for symlink, '
                                         'but it does not exist. Skipping'
                                         .format(symlink_dest_path))
                            continue

                    bundle_library_path_obj = Path(bundle_library_path)
                    symlink_path_obj = Path(symlink_path)

                    relative_path = os.path.relpath(bundle_library_path,
                                                    symlink_path)
                    logger.info(
                        'bundle_library_path {} relative path {}'.format(
                            bundle_library_path, relative_path))
                    os.remove(symlink_path)
                    os.symlink(relative_path, symlink_path)


def rewrite_catkin_package_path(base_path):
    """
    Update catkin/profile.d to use correct shebangs.

    :param base_path: Path to the bundle staging directory
    """
    # TODO: This should be in the ros package
    import re
    python_regex = re.compile('/usr/bin/python')
    logger.info('Starting shebang update...')

    ros_distribution_version = get_ros_distribution_version()
    # These files contain references to /usr/bin/python that need
    # to be converted to avoid errors when setting up the ROS workspace
    files = ['1.ros_package_path.sh', '10.ros.sh']

    profiled_path = os.path.join(
        base_path, 'opt', 'ros', ros_distribution_version,
        'etc', 'catkin', 'profile.d')

    for file in map(lambda s: os.path.join(profiled_path, s), files):
        if os.path.isfile(file):
            with open(file, 'rb+') as file_handle:
                contents = file_handle.read()
                try:
                    str_contents = contents.decode()
                except UnicodeError:
                    logger.error(
                        '{file} should be a text file'.format_map(
                            locals()))
                    continue
                replacement_tuple = python_regex.subn('python', str_contents)
                if replacement_tuple[1] > 0:
                    logger.info(
                        'Found direct python invocation in {file}'
                        .format_map(locals()))
                    file_handle.seek(0)
                    file_handle.truncate()
                    file_handle.write(replacement_tuple[0].encode())


def filechecksum(filename, algorithm='sha256', printing=False):
    """
    Generate hash of file.

    :param filename: path to file to generate hash from
    :param algorithm: Choose one of sha256, sha512, sha1, md5
    :param printing: print to stdout
    :return: the hash
    :rtype: str
    """
    if algorithm == 'sha256':
        hasher = hashlib.sha256()
    elif algorithm == 'sha512':
        hasher = hashlib.sha512()
    elif algorithm == 'sha1':
        hasher = hashlib.sha1()
    elif algorithm == 'md5':
        hasher = hashlib.md5()
    else:
        raise RuntimeError('Unsupported hash algorithm')
    try:
        with open(filename, 'rb') as afile:
            FILE_READER_CHUNK_SIZE = 65536  # noqa: N806
            buf = afile.read(FILE_READER_CHUNK_SIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(FILE_READER_CHUNK_SIZE)
        checksum = hasher.hexdigest()
        if printing:
            print(filename + ' - ' + checksum)
        return checksum
    except Exception as e:
        raise RuntimeError(e)
