import json
import math
import os
import tarfile
import tempfile

from colcon_core.logging import colcon_logger

from .utilities import filechecksum

logger = colcon_logger.getChild(__name__)

# Size in bytes
MAX_METADATA_SIZE = 4 * 1024 * 1024

# tarfile format used in bundlefiles
TARFILE_FORMAT = tarfile.GNU_FORMAT


class Bundle:
    """Provides an interface to application bundle files."""

    def __init__(self, *, name=None, mode='w'):
        """
        Open a bundle archive for writing.

        mode:
        'w' open for writing

        :param name: path to the bundle archive
        :param mode: mode to open file as
        """
        self.tarfile = tarfile.open(name, mode, format=TARFILE_FORMAT)
        self.overlays = []
        self.metadata = []
        self.mode = mode
        self.closed = False

    def add_metadata(self, path):
        """
        Add the json file at path to the metadata archive.

        :param path: path to json file
        """
        self._check('w')
        self.metadata.append(path)

    def add_overlay_archive(self, path):
        """
        Add the archive at path to the bundle as an overlay.

        This does not write immediately, once the object is closed all
        writes will occur.
        """
        self._check('w')
        self.overlays.append(path)

    def _close(self):
        if 'w' in self.mode:
            logger.debug('Start: Bundle')
            self._check('w')
            tempdir = tempfile.mkdtemp()
            version_path = os.path.join(tempdir, 'version')

            with open(version_path, 'w') as v:
                v.write('2')
            self.tarfile.add(version_path, arcname='version')
            logger.debug('Start: metadata')
            offset = MAX_METADATA_SIZE
            overlay_metadata = []
            for overlay in self.overlays:
                name = os.path.basename(overlay)
                checksum = filechecksum(overlay)
                info = self.tarfile.gettarinfo(overlay, arcname=name)
                header_size = len(info.tobuf(TARFILE_FORMAT))
                file_size = os.stat(overlay).st_size
                overlay_metadata.append({
                    'name': name,
                    'sha256': checksum,
                    'offset': offset + header_size,
                    'size': file_size
                })
                num_blocks = math.ceil(file_size / tarfile.BLOCKSIZE)
                offset = offset + header_size + num_blocks * tarfile.BLOCKSIZE

            metadata_path = os.path.join(tempdir, 'overlays.json')
            with open(metadata_path, 'w') as md:
                metadata = {
                    'overlays': overlay_metadata
                }
                json.dump(metadata, md)

            metadata_archive_path = os.path.join(tempdir, 'metadata.tar.gz')
            with tarfile.open(metadata_archive_path, 'w:gz') as md:
                md.add(metadata_path, arcname=os.path.basename(metadata_path))
                for item in self.metadata:
                    md.add(item, arcname=os.path.basename(item))
            self.tarfile.add(metadata_archive_path,
                             arcname=os.path.basename(metadata_archive_path))
            logger.debug('End: metadata')
            if os.stat(metadata_archive_path).st_size > MAX_METADATA_SIZE:
                raise RuntimeError('Metadata too large, must be less than 4MB')
            logger.debug('Start: pad')
            tar_header_len = tarfile.BLOCKSIZE
            pad_size = MAX_METADATA_SIZE - self.tarfile.offset - tar_header_len
            pad_path = os.path.join(tempdir, 'pad')
            with open(pad_path, 'wb') as f:
                data = bytearray(pad_size)
                f.write(data)
            self.tarfile.add(pad_path, arcname='pad')
            logger.debug('End: pad')
            for overlay in self.overlays:
                logger.info('Start tar overlay file: %s', overlay)
                name = os.path.basename(overlay)
                self.tarfile.add(overlay, arcname=name)
                logger.info('End tar overlay file: %s', overlay)
            self.tarfile.close()
            logger.debug('End: Bundle')
            self.closed = True

    def close(self):  # noqa: N806
        """Close the archive."""
        self._close()

    def _check(self, mode=None):
        """Check if Bundle is still open. And mode is valid."""
        if self.closed:
            raise OSError('%s is closed' % self.__class__.__name__)
        if mode is not None and self.mode not in mode:
            raise OSError('bad operation for mode %r' % self.mode)

    def __enter__(self):  # noqa: D105
        return self

    def __exit__(self, t, value, traceback):  # noqa: D105
        self.close()
