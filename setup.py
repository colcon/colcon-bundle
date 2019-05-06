# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='colcon-bundle',
    version='0.0.13',
    author='Matthew Murphy',
    author_email='matmur@amazon.com',
    maintainer='Matthew Murphy',
    maintainer_email='matmur@amazon.com',
    url='https://github.com/colcon/colcon-bundle/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    license='Apache License, Version 2.0',
    description='Plugin to bundle built software for the colcon command line tool',
    long_description=long_description,
    keywords='colcon',
    python_requires='>=3.5',
    install_requires=[
        'setuptools>=30.3.0',
        'colcon-core>=0.3.15',
        'colcon-python-setup-py>=0.2.1',
        'distro>=1.3.0'
    ],
    tests_require=[
        'flake8',
        'flake8-blind-except',
        'flake8-builtins',
        'flake8-class-newline',
        'flake8-comprehensions',
        'flake8-deprecated',
        'flake8-docstrings',
        'flake8-import-order',
        'flake8-quotes',
        'mock',
        'pep8-naming',
        'pyenchant',
        'pylint',
        'pytest',
        'pytest-cov',
        'pytest-asyncio',
        'pycodestyle==2.3.0',
    ],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=['test', 'test.*', 'integration']),
    entry_points={
        'colcon_core.verb': [
            'bundle = colcon_bundle.verb.bundle:BundleVerb'
        ],
        'colcon_bundle.installer': [
            'apt = colcon_bundle.installer.apt:AptBundleInstallerExtension',
            'pip = colcon_bundle.installer.pip:PipBundleInstallerExtensionPoint',
            'pip3 = colcon_bundle.installer.pip3:Pip3BundleInstallerExtensionPoint'
        ],
        'colcon_bundle.task.bundle': [
            'python = colcon_bundle.task.python.bundle:PythonBundleTask'
        ]
    }
)
