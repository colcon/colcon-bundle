import os
import shutil
import tempfile
from unittest import TestCase

from colcon_bundle.verb import check_and_mark_bundle_tool, check_and_mark_bundle_version, \
    get_and_mark_bundle_cache_version


class TestCheckAndMarkBundle(TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.mkdtemp()
        self.marker_path = os.path.join(self.dir, '.bundled_by')

    def tearDown(self) -> None:
        shutil.rmtree(self.dir)

    def test_marker_does_not_exist(self):
        check_and_mark_bundle_tool(self.dir)

        self.assertTrue(os.path.exists(self.marker_path))
        with open(self.marker_path) as f:
            contents = f.readline()
            self.assertEqual('colcon\n', contents)

    def test_marker_matches(self):
        with open(self.marker_path, 'w') as f:
            f.write('colcon\n')
        check_and_mark_bundle_tool(self.dir)

    def test_marker_does_not_match(self):
        with open(self.marker_path, 'w') as f:
            f.write('donotmatch\n')
        self.assertRaises(RuntimeError,
                          lambda: check_and_mark_bundle_tool(self.dir))

    def test_directory_does_not_exist(self):
        shutil.rmtree(self.dir)
        check_and_mark_bundle_tool(self.dir)
        with open(self.marker_path) as f:
            contents = f.readline()
            self.assertEqual('colcon\n', contents)


class TestCheckAndMarkBundleVersion(TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.mkdtemp()
        self.marker_path = os.path.join(self.dir, '.bundle_version')

    def tearDown(self) -> None:
        shutil.rmtree(self.dir)

    def test_sets_v1_not_previously_bundled(self):
        self._test_sets_version_not_previously_bundled(1)

    def test_sets_v2_not_previously_bundled(self):
        self._test_sets_version_not_previously_bundled(2)

    def _test_sets_version_not_previously_bundled(self, version):
        check_and_mark_bundle_version(self.dir,
                                      this_bundle_version=version,
                                      previously_bundled=False)
        with open(self.marker_path) as f:
            contents = f.readline()
            self.assertEqual('%s\n' % version, contents)

    def test_previously_bundled_v1(self):
        check_and_mark_bundle_version(self.dir,
                                      this_bundle_version=1,
                                      previously_bundled=True)
        with open(self.marker_path) as f:
            contents = f.readline()
            self.assertEqual('1\n', contents)

    def test_previously_bundled_w_no_marker_attempt_v2_raises(self):
        self.assertRaises(
            RuntimeError,
            lambda: check_and_mark_bundle_version(self.dir,
                                                  this_bundle_version=2,
                                                  previously_bundled=True))

    def test_version_mismatch_raises(self):
        with open(self.marker_path, 'w') as f:
            f.write('1\n')
        self.assertRaises(
            RuntimeError,
            lambda: check_and_mark_bundle_version(self.dir,
                                                  this_bundle_version=2,
                                                  previously_bundled=True))

    def test_v1_pass(self):
        check_and_mark_bundle_version(self.dir,
                                      this_bundle_version=1,
                                      previously_bundled=False)
        check_and_mark_bundle_version(self.dir,
                                      this_bundle_version=1,
                                      previously_bundled=True)

    def test_v2_pass(self):
        check_and_mark_bundle_version(self.dir,
                                      this_bundle_version=2,
                                      previously_bundled=False)
        check_and_mark_bundle_version(self.dir,
                                      this_bundle_version=2,
                                      previously_bundled=True)


class TestCheckAndMarkCacheVersion(TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.mkdtemp()
        self.marker_path = os.path.join(self.dir, '.bundle_cache_version')

    def tearDown(self) -> None:
        shutil.rmtree(self.dir)

    def test_previously_bundled_sets_cache_v1(self):
        version = get_and_mark_bundle_cache_version(self.dir,
                                                    previously_bundled=True)
        self.assertEqual(1, version)

    def test_not_previously_bundled_sets_cache_v2(self):
        version = get_and_mark_bundle_cache_version(self.dir,
                                                    previously_bundled=False)
        self.assertEqual(2, version)

    def test_previously_bundled_v1(self):
        with open(self.marker_path, 'w') as f:
            f.write('1\n')
        version = get_and_mark_bundle_cache_version(self.dir,
                                                    previously_bundled=True)
        self.assertEqual(1, version)

    def test_previously_bundled_v2(self):
        with open(self.marker_path, 'w') as f:
            f.write('2\n')
        version = get_and_mark_bundle_cache_version(self.dir,
                                                    previously_bundled=True)
        self.assertEqual(2, version)
