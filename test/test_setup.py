# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import colcon_bundle


def test_version():
    version = colcon_bundle.__version__
    assert version == '0.1.1'
