# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import setuptools

setuptools.setup(name='test-py-module',
                 version=0.1,
                 description='Test Module',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'annoy==1.8.3',
                     'tensorflow==1.14.0',
                 ])