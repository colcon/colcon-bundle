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
                     'Pillow==4.3.0',
                     'matplotlib==2.0.2',
                     'numpy==1.13.0',
                     'pandas==0.20.2',
                     'pygame==1.9.3',
                     'PyOpenGL==3.1.0',
                     'scipy==0.19.0',
                     'scikit-image==0.13.0'
                 ])