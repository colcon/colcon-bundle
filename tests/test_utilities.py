# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import filecmp
import os
import shutil
import tempfile

from colcon_bundle.verb._utilities import update_shebang


class TestUtilities:

    def setup_method(self, method):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self, method):
        shutil.rmtree(self.tmpdir)

    def test_replaces_regular_shebang(self):
        regular_python_shebang_script = 'regular_python_shebang.sh'
        assets_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets')
        shutil.copy(
            os.path.join(assets_directory, regular_python_shebang_script),
            self.tmpdir)

        update_shebang(self.tmpdir)

        actual_file = os.path.join(self.tmpdir, regular_python_shebang_script)
        expected_file = os.path.join(assets_directory,
                                     'regular_python_shebang_expected.sh')
        print(actual_file)

        assert filecmp.cmp(actual_file, expected_file)

    def test_replaces_py3_shebang(self):
        regular_python_shebang_script = 'regular_python3_shebang.sh'
        assets_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets')
        shutil.copy(
            os.path.join(assets_directory, regular_python_shebang_script),
            self.tmpdir)

        update_shebang(self.tmpdir)

        actual_file = os.path.join(self.tmpdir, regular_python_shebang_script)
        expected_file = os.path.join(assets_directory,
                                     'regular_python3_shebang_expected.sh')
        print(actual_file)

        assert filecmp.cmp(actual_file, expected_file)

    def test_ignores_symlinks(self):
        pass

    def test_replaces_shebang_with_arguments(self):
        pass
