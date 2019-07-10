# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import txxlz


def test():
    from annoy import AnnoyIndex
    import random

    f = 40
    t = AnnoyIndex(f)  # Length of item vector that will be indexed
    for i in range(1000):
        v = [random.gauss(0, 1) for z in range(f)]
        t.add_item(i, v)

    t.build(10) # 10 trees
    print("test-py-module passed...")