# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import traceback

from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import instantiate_extensions, \
    order_extensions_by_priority

logger = colcon_logger.getChild(__name__)


class BundleInstallerContext:
    """The context provided to installers."""

    def __init__(self, *, args, cache_path, prefix_path):
        """
        Construct the BundleInstallerContext.

        :param args: The parsed command line arguments
        """
        self.args = args
        self.cache_path = cache_path
        self.prefix_path = prefix_path


class BundleInstallerExtensionPoint:
    """
    The interface for bundle installer extensions.

    A bundle installer extension provides an installer for use with the
    bundle verb

    For each instance the attribute `INSTALLER_NAME` is being set to the
    basename of
    the entry point registering the extension.
    """

    """The version of the bundle installer extension interface."""
    EXTENSION_POINT_VERSION = '1.0'

    """The default priority of bundle installer extensions."""
    PRIORITY = 100

    def should_load(self):
        """
        Check whether the extension should load on the system.

        Default: True

        :return: True if the extension should be loaded
        :rtype: Bool
        """
        return True

    def add_arguments(self, *, parser):
        """
        Add arguments to the command line invocation.

        :param parser: The argument parser for this command
        """

    def initialize(self, context):
        """
        Initialize the installer based on the context.

        :param context: Context for this installer instances
        :return: None
        """
        raise RuntimeError('This should be implemented in the subclass')

    def cache_invalid(self):
        """
        Check if input to the installer has changed.

        This method should look at the arguments and parameters
        provided to the installer and determine if the cache for
        the installer is invalid. An invalid cache means that
        install() should be called to update the bundle.

        :return: true if the install() for this installer
        should be re-invoked
        """
        return False

    def add_to_install_list(self, name, *, metadata=None):
        """
        Add item to the list of items to install with this installer.

        The metadata is specific for each installer type.

        :param name: Name of the item to install
        :param metadata: Installer specific metadata may or may not be required
        depending on the installer
        :return: None
        """
        raise RuntimeError('This should be implemented in a subclass')

    def remove_from_install_list(self, name, *, metadata=None):
        """
        Remove an item from the installation list based on name or metadata.

        The metadata is specific for each installer type.

        :param str name: Installer specific name of the package
        :param metadata: Installer specific metadata may or may not be required
        depending on the installer
        :return: None
        """
        raise RuntimeError('This should be implemented in a subclass')

    def install(self):
        """
        Install all items tracked by this installer.

        :returns: Metadata associated with the install. This metadata will
        be written into the metadata.tar under installers.json
        :rtype: dict
        """
        raise RuntimeError('This should be implemented in a subclass')


def get_bundle_installer_extensions():
    """
    Get the bundle installer extensions and verify if they should be loaded.

    The extensions are ordered by their entry point name.

    :rtype: OrderedDict
    """
    extensions = instantiate_extensions(__name__)
    filtered_extensions = {name: extension for name, extension in
                           extensions.items() if extension.should_load()}
    for name, extension in filtered_extensions.items():
        extension.INSTALLER_NAME = name
    return order_extensions_by_priority(extensions)


def add_installer_arguments(parser):
    """
    Add the command line arguments for the task extensions.

    :param parser: The argument parser
    """
    extensions = get_bundle_installer_extensions()
    for extension_name, extension in extensions.items():
        group = parser.add_argument_group(
            title="Arguments for '{extension_name}' installer"
            .format_map(locals()))
        try:
            retval = extension.add_arguments(parser=group)
            assert retval is None, 'add_arguments() should return None'
        except Exception as e:
            # catch exceptions raised in task extension
            exc = traceback.format_exc()
            logger.error(
                'Exception in task extension '
                "'{task_name}.{package_type}': {e}\n{exc}"
                .format(
                    task_name=extension.TASK_NAME,
                    package_type=extension.PACKAGE_TYPE,
                    e=e,
                    exc=exc))
            # skip failing extension, continue with next one


class InstallerNotFound(Exception):
    """When there is an attempt to use an installer that is not loaded."""

    pass
