# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Read/Write Avro File Object Containers."""

import logging
import sys

from ..avro import avro_io_async
from ..avro import schema
from .datafile import DataFileException
from .datafile import MAGIC, SYNC_SIZE, META_SCHEMA, SCHEMA_KEY


PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Constants

# Codecs supported by container files:
VALID_CODECS = frozenset(['null'])


class AsyncDataFileReader(object):
    """Read files written by DataFileWriter."""

    def __init__(self, reader, datum_reader):
        """Initializes a new data file reader.

        Args:
          reader: Open file to read from.
          datum_reader: Avro datum reader.
        """
        self._reader = reader
        self._raw_decoder = avro_io_async.AsyncBinaryDecoder(reader)
        self._datum_decoder = None  # Maybe reset at every block.
        self._datum_reader = datum_reader
        self.codec = "null"
        self._block_count = 0
        self._meta = None
        self._sync_marker = None

    async def init(self):
        # read the header: magic, meta, sync
        await self._read_header()

        # ensure codec is valid
        avro_codec_raw = self.get_meta('avro.codec')
        if avro_codec_raw is None:
            self.codec = "null"
        else:
            self.codec = avro_codec_raw.decode('utf-8')
        if self.codec not in VALID_CODECS:
            raise DataFileException('Unknown codec: %s.' % self.codec)

        # get ready to read
        self._block_count = 0
        self.datum_reader.writer_schema = (
            schema.parse(self.get_meta(SCHEMA_KEY).decode('utf-8')))
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, data_type, value, traceback):
        # Perform a close if there's no exception
        if data_type is None:
            self.close()

    def __aiter__(self):
        return self

    # read-only properties
    @property
    def reader(self):
        return self._reader

    @property
    def raw_decoder(self):
        return self._raw_decoder

    @property
    def datum_decoder(self):
        return self._datum_decoder

    @property
    def datum_reader(self):
        return self._datum_reader

    @property
    def sync_marker(self):
        return self._sync_marker

    @property
    def meta(self):
        return self._meta

    # read/write properties
    @property
    def block_count(self):
        return self._block_count

    def get_meta(self, key):
        """Reports the value of a given metadata key.

        Args:
          key: Metadata key (string) to report the value of.
        Returns:
          Value associated to the metadata key, as bytes.
        """
        return self._meta.get(key)

    async def _read_header(self):
        # seek to the beginning of the file to get magic block
        await self.reader.seek(0, 0)

        # read header into a dict
        header = await self.datum_reader.read_data(META_SCHEMA, self.raw_decoder)

        # check magic number
        if header.get('magic') != MAGIC:
            fail_msg = "Not an Avro data file: %s doesn't match %s." \
                       % (header.get('magic'), MAGIC)
            raise schema.AvroException(fail_msg)

        # set metadata
        self._meta = header['meta']

        # set sync marker
        self._sync_marker = header['sync']

    async def _read_block_header(self):
        self._block_count = await self.raw_decoder.read_long()
        if self.codec == "null":
            # Skip a long; we don't need to use the length.
            await self.raw_decoder.skip_long()
            self._datum_decoder = self._raw_decoder
        else:
            raise DataFileException("Unknown codec: %r" % self.codec)

    async def _skip_sync(self):
        """
        Read the length of the sync marker; if it matches the sync marker,
        return True. Otherwise, seek back to where we started and return False.
        """
        proposed_sync_marker = await self.reader.read(SYNC_SIZE)
        if SYNC_SIZE > 0 and not proposed_sync_marker:
            raise StopAsyncIteration
        if proposed_sync_marker != self.sync_marker:
            await self.reader.seek(-SYNC_SIZE, 1)

    async def __anext__(self):
        """Return the next datum in the file."""
        if self.block_count == 0:
            await self._skip_sync()
            await self._read_block_header()

        datum = await self.datum_reader.read(self.datum_decoder)
        self._block_count -= 1
        return datum

    def close(self):
        """Close this reader."""
        self.reader.close()


if __name__ == '__main__':
    raise Exception('Not a standalone module')
