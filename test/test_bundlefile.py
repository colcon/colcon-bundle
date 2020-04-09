import json
import os
import shutil
import tarfile
import tempfile
from io import BytesIO

import pytest

from colcon_bundle.verb.bundlefile import Bundle

json_data = {'test': 1, 'test_2': 2,
             'test_3': ['foo'], 'test_4': {'test_5': 1.3283}}


class TestBundlefile:
    def setup_method(self, method):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self, method):
        shutil.rmtree(self.tmpdir)

    def test_bundlefile(self):
        bundle_path = os.path.join(self.tmpdir, 'test.mba')
        json_file = os.path.join(self.tmpdir, 'file')
        with open(json_file, 'w') as f:
            f.write(json.dumps(json_data))

        blocksize_file = os.path.join(self.tmpdir, 'blocksize_file')
        with open(blocksize_file, 'wb') as f:
            f.write(bytearray(tarfile.BLOCKSIZE))

        large_file = os.path.join(self.tmpdir, 'large_file')
        with open(large_file, 'wb') as f:
            large_file_size = 12 + tarfile.BLOCKSIZE * 1000
            f.write(bytearray(large_file_size))

        dep_archive = os.path.join(self.tmpdir, 'dependencies.tar.gz')
        with tarfile.open(dep_archive, 'w:gz') as a:
            a.add(json_file, arcname='file')

        other_archive = os.path.join(self.tmpdir, 'other.tar.gz')
        with tarfile.open(other_archive, 'w:gz') as a:
            a.add(json_file, arcname='file2')

        with Bundle(name=bundle_path, mode='w') as bundle:
            bundle.add_overlay_archive(dep_archive)
            bundle.add_overlay_archive(other_archive)
            bundle.add_overlay_archive(blocksize_file)
            bundle.add_overlay_archive(large_file)

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
        size = os.stat(dep_archive).st_size
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
            other_offset = overlays[1]['offset']
            assert os.stat(other_archive).st_size == overlays[1]['size']

            assert overlays[2]['size'] == tarfile.BLOCKSIZE
            assert overlays[3]['size'] == large_file_size

        with open(bundle_path, 'rb') as bundle:
            bundle.seek(offset)
            deps = BytesIO(bundle.read(size))
            tar = tarfile.open(fileobj=deps)
            assert 'file' == tar.members[0].name
            json_buffer = tar.extractfile(tar.members[0])
            actual_data = json.loads(json_buffer.read().decode('utf-8'))
            assert actual_data == json_data

        with open(bundle_path, 'rb') as bundle:
            bundle.seek(other_offset)
            deps = BytesIO(bundle.read(size))
            tar = tarfile.open(fileobj=deps)
            assert 'file2' == tar.members[0].name
            json_buffer = tar.extractfile(tar.members[0])
            actual_data = json.loads(json_buffer.read().decode('utf-8'))
            assert actual_data == json_data

    def test_bundlefile_metadata_over_4mb(self):
        file_size = 6 * 1024 * 1024  # size in bytes
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
