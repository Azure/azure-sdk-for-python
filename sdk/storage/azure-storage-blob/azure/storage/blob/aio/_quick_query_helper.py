# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from typing import Any, Dict, Generator, IO, Iterable, Optional, Type, Union, TYPE_CHECKING

from .._shared.avro.avro_io import DatumReader
from .._shared.avro.datafile import DataFileReader

if TYPE_CHECKING:
    from .._models import BlobQueryError


class BlobQueryReader:  # pylint: disable=too-many-instance-attributes
    """A streaming object to read query results."""

    def __init__(self):
        raise NotImplementedError("BlobQueryReader is not yet implemented.")


class QuickQueryStreamer:
    """File-like streaming iterator."""

    def __init__(self, generator):
        self.generator = generator
        self.iterator = aiter(generator)
        self._buf = b""
        self._point = 0
        self._download_offset = 0
        self._buf_start = 0
        self.file_length = None
        raise NotImplementedError("QuickQueryStreamer is not yet implemented.")

    def __len__(self):
        return self.file_length

    def __aiter__(self):
        return self.iterator
