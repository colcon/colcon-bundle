# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import setuptools

setuptools.setup(name='test-py-module',
                 version=0.1,
                 description='Test Module',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'flake8==3.4.0',
                     'annoy==1.8.3',
                     'numpy==1.13.0',
                 ])