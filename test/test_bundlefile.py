import json
import os
import shutil
import tarfile
import tempfile
from io import BytesIO

import pytest

from colcon_bundle.verb.bundlefile import Bundle


class TestBundlefile:
    def setup_method(self, method):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self, method):
        shutil.rmtree(self.tmpdir)

    def test_bundlefile(self):
        bundle_path = os.path.join(self.tmpdir, 'test.mba')
        file_path = os.path.join(self.tmpdir, 'file')
        with open(file_path, 'w') as f:
            f.write('{}')

        archive = os.path.join(self.tmpdir, 'dependencies.tar.gz')
        with tarfile.open(archive, 'w:gz') as a:
            a.add(file_path, arcname='file')

        other = os.path.join(self.tmpdir, 'other.tar.gz')
        with tarfile.open(other, 'w:gz') as a:
            a.add(file_path, arcname='file')

        with Bundle(name=bundle_path, mode='w') as bundle:
            bundle.add_overlay_archive(archive)
            bundle.add_overlay_archive(other)

        metadata_path = os.path.join(self.tmpdir, 'metadata.tar.gz')
        with tarfile.open(bundle_path, 'r:') as bundle:
            members = bundle.getmembers()
            assert 'version' == members[0].name
            assert 'metadata.tar.gz' == members[1].name
            assert 'pad' == members[2].name
            assert 'dependencies.tar.gz' == members[3].name
            # Validate the overlays start at 4MB
            assert 4 * 1024 * 1024 == members[3].offset
            bundle.extract(members[1], self.tmpdir)

        tar_header_size = 512
        offset = 4 * 1024 * 1024 + tar_header_size
        size = os.stat(archive).st_size
        with tarfile.open(metadata_path) as metadata_tar:
            members = metadata_tar.members
            contents = metadata_tar.extractfile(members[0])
            assert members[0].name == 'overlays.json'
            metadata = json.loads(contents.read().decode())
            overlays = metadata['overlays']
            assert 'dependencies.tar.gz' == overlays[0]['name']
            assert offset == overlays[0]['offset']
            assert size == overlays[0]['size']
            assert 64 == len(overlays[0]['sha256'])

            assert 'other.tar.gz' == overlays[1]['name']
            assert offset + size + tar_header_size == overlays[1]['offset']
            assert os.stat(other).st_size == overlays[1]['size']

        with open(bundle_path, 'rb') as bundle:
            bundle.seek(offset)
            deps = BytesIO(bundle.read(size))
            tar = tarfile.open(fileobj=deps)
            assert 'file' == tar.members[0].name
            json_buffer = tar.extractfile(tar.members[0])
            json.loads(json_buffer.read().decode('utf-8'))

    def test_bundlefile_metadata_over_4mb(self):
        file_size = 6 * 1024 * 1024 # size in bytes
        large_file_path = os.path.join(self.tmpdir, 'big_file')
        with open(large_file_path, "wb") as f:
            f.write(os.urandom(file_size))

        bundle_path = os.path.join(self.tmpdir, 'test.mba')
        file_path = os.path.join(self.tmpdir, 'file')
        with open(file_path, 'wb') as f:
            f.write(bytearray(10000))

        archive = os.path.join(self.tmpdir, 'dependencies.tar.gz')
        with tarfile.open(archive, 'w:gz') as a:
            a.add(file_path, arcname='file')

        other = os.path.join(self.tmpdir, 'other.tar.gz')
        with tarfile.open(other, 'w:gz') as a:
            a.add(file_path, arcname='file')

        with pytest.raises(RuntimeError):
            with Bundle(name=bundle_path, mode='w') as bundle:
                bundle.add_metadata(large_file_path)
                bundle.add_overlay_archive(archive)
                bundle.add_overlay_archive(other)

