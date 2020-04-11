#!/usr/bin/env python3
# -*- mode: python -*-
# -*- coding: utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Read/Write Avro File Object Containers."""

import io
import logging
import sys
import zlib

from ..avro import avro_io
from ..avro import schema

PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Constants

# Version of the container file:
VERSION = 1

if PY3:
  MAGIC = b'Obj' + bytes([VERSION])
  MAGIC_SIZE = len(MAGIC)
else:
  MAGIC = 'Obj' + chr(VERSION)
  MAGIC_SIZE = len(MAGIC)

# Size of the synchronization marker, in number of bytes:
SYNC_SIZE = 16

# Interval between synchronization markers, in number of bytes:
# TODO: make configurable
SYNC_INTERVAL = 1000 * SYNC_SIZE

# Schema of the container header:
META_SCHEMA = schema.parse("""
{
  "type": "record", "name": "org.apache.avro.file.Header",
  "fields": [{
    "name": "magic",
    "type": {"type": "fixed", "name": "magic", "size": %(magic_size)d}
  }, {
    "name": "meta",
    "type": {"type": "map", "values": "bytes"}
  }, {
    "name": "sync",
    "type": {"type": "fixed", "name": "sync", "size": %(sync_size)d}
  }]
}
""" % {
    'magic_size': MAGIC_SIZE,
    'sync_size': SYNC_SIZE,
})

# Codecs supported by container files:
VALID_CODECS = frozenset(['null', 'deflate'])

# Not used yet
VALID_ENCODINGS = frozenset(['binary'])

# Metadata key associated to the codec:
CODEC_KEY = "avro.codec"

# Metadata key associated to the schema:
SCHEMA_KEY = "avro.schema"


# ------------------------------------------------------------------------------
# Exceptions


class DataFileException(schema.AvroException):
  """Problem reading or writing file object containers."""

  def __init__(self, msg):
    super(DataFileException, self).__init__(msg)

# ------------------------------------------------------------------------------


class DataFileReader(object):
  """Read files written by DataFileWriter."""

  # TODO: allow user to specify expected schema?
  # TODO: allow user to specify the encoder
  def __init__(self, reader, datum_reader):
    """Initializes a new data file reader.

    Args:
      reader: Open file to read from.
      datum_reader: Avro datum reader.
    """
    self._reader = reader
    self._raw_decoder = avro_io.BinaryDecoder(reader)
    self._datum_decoder = None # Maybe reset at every block.
    self._datum_reader = datum_reader

    # read the header: magic, meta, sync
    self._read_header()

    # ensure codec is valid
    avro_codec_raw = self.GetMeta('avro.codec')
    if avro_codec_raw is None:
      self.codec = "null"
    else:
      self.codec = avro_codec_raw.decode('utf-8')
    if self.codec not in VALID_CODECS:
      raise DataFileException('Unknown codec: %s.' % self.codec)

    self._file_length = self._GetInputFileLength()

    # get ready to read
    self._block_count = 0
    self.datum_reader.writer_schema = (
        schema.parse(self.GetMeta(SCHEMA_KEY).decode('utf-8')))

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    # Perform a close if there's no exception
    if type is None:
      self.close()

  def __iter__(self):
    return self

  def __next__(self):
    """Implements the iterator interface."""
    return next(self)

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

  @property
  def file_length(self):
    """Length of the input file, in bytes."""
    return self._file_length

  # read/write properties
  @property
  def block_count(self):
    return self._block_count

  def GetMeta(self, key):
    """Reports the value of a given metadata key.

    Args:
      key: Metadata key (string) to report the value of.
    Returns:
      Value associated to the metadata key, as bytes.
    """
    return self._meta.get(key)

  def SetMeta(self, key, value):
    """Sets a metadata.

    Args:
      key: Metadata key (string) to set.
      value: Metadata value to set, as bytes.
    """
    if isinstance(value, str):
      value = value.encode('utf-8')
    self._meta[key] = value

  def _GetInputFileLength(self):
    """Reports the length of the input file, in bytes.

    Leaves the current position unmodified.

    Returns:
      The length of the input file, in bytes.
    """
    current_pos = self.reader.tell()
    self.reader.seek(0, 2)
    file_length = self.reader.tell()
    self.reader.seek(current_pos)
    return file_length

  def is_EOF(self):
    return self.reader.tell() == self.file_length

  def _read_header(self):
    # seek to the beginning of the file to get magic block
    self.reader.seek(0, 0)

    # read header into a dict
    header = self.datum_reader.read_data(
      META_SCHEMA, META_SCHEMA, self.raw_decoder)

    # check magic number
    if header.get('magic') != MAGIC:
      fail_msg = "Not an Avro data file: %s doesn't match %s."\
                 % (header.get('magic'), MAGIC)
      raise schema.AvroException(fail_msg)

    # set metadata
    self._meta = header['meta']

    # set sync marker
    self._sync_marker = header['sync']

  def _read_block_header(self):
    self._block_count = self.raw_decoder.read_long()
    if self.codec == "null":
      # Skip a long; we don't need to use the length.
      self.raw_decoder.skip_long()
      self._datum_decoder = self._raw_decoder
    elif self.codec == 'deflate':
      # Compressed data is stored as (length, data), which
      # corresponds to how the "bytes" type is encoded.
      data = self.raw_decoder.read_bytes()
      # -15 is the log of the window size; negative indicates
      # "raw" (no zlib headers) decompression.  See zlib.h.
      uncompressed = zlib.decompress(data, -15)
      self._datum_decoder = avro_io.BinaryDecoder(io.BytesIO(uncompressed))
    else:
      raise DataFileException("Unknown codec: %r" % self.codec)

  def _skip_sync(self):
    """
    Read the length of the sync marker; if it matches the sync marker,
    return True. Otherwise, seek back to where we started and return False.
    """
    proposed_sync_marker = self.reader.read(SYNC_SIZE)
    if proposed_sync_marker != self.sync_marker:
      self.reader.seek(-SYNC_SIZE, 1)
      return False
    else:
      return True

  # TODO: handle block of length zero
  # TODO: clean this up with recursion
  def __next__(self):
    """Return the next datum in the file."""
    if self.block_count == 0:
      if self.is_EOF():
        raise StopIteration
      elif self._skip_sync():
        if self.is_EOF(): raise StopIteration
        self._read_block_header()
      else:
        self._read_block_header()

    datum = self.datum_reader.read(self.datum_decoder)
    self._block_count -= 1
    return datum

  # PY2
  def next(self):
    return self.__next__()

  def close(self):
    """Close this reader."""
    self.reader.close()


if __name__ == '__main__':
  raise Exception('Not a standalone module')
