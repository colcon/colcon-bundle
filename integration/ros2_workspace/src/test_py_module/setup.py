# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import setuptools

setuptools.setup(
    name='test_py_module',
    version=0.1,
    description='Test Module',
    packages=setuptools.find_packages(),
    zip_safe=True,
    install_requires=[
        'annoy',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
        'run_py_module_tests = test_py_module.run_annoy:test',
    ],
    })