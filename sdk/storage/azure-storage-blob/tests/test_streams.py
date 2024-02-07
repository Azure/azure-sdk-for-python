# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import math
import os
import random
from io import BytesIO
from typing import List, Tuple, Union

import pytest
from azure.storage.blob._shared.streams import (
    StructuredMessageConstants,
    StructuredMessageDecodeStream,
    StructuredMessageProperties,
)
from azure.storage.extensions import crc64


def _write_message_header(
    message_length: int,
    flags: StructuredMessageProperties,
    segment_count: int,
    stream: BytesIO
) -> None:
    stream.write(b'\x01')  # Version
    stream.write(message_length.to_bytes(8, 'little'))  # Message length
    stream.write(int(flags).to_bytes(2, 'little'))  # Flags
    stream.write(segment_count.to_bytes(2, 'little'))  # Num segments


def _write_segment(number: int, data: bytes, flags: StructuredMessageProperties, stream: BytesIO) -> None:
    stream.write(number.to_bytes(2, 'little'))  # Segment number
    stream.write(len(data).to_bytes(8, 'little'))  # Segment length
    stream.write(data)  # Segment content
    if StructuredMessageProperties.CRC64 in flags:
        crc: int = crc64.compute_crc64(data, 0)
        stream.write(crc.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))


def _build_structured_message(
    data: bytes,
    segment_size: Union[int, List[int]],
    flags: StructuredMessageProperties,
) -> Tuple[BytesIO, int]:
    if isinstance(segment_size, list):
        segment_count = len(segment_size)
    else:
        segment_count = 1 if segment_size == 0 else math.ceil(len(data) / segment_size)
    segment_footer_length = StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0

    message_length = (
        StructuredMessageConstants.V1_HEADER_LENGTH +
        ((StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH + segment_footer_length) * segment_count) +
        len(data))

    message = BytesIO()

    # Message Header
    _write_message_header(message_length, flags, segment_count, message)

    # Special case for 0 length content
    if len(data) == 0:
        _write_segment(1, data, flags, message)
        message.seek(0, 0)
        return message, message_length

    # Segments
    segment_sizes = segment_size if isinstance(segment_size, list) else [segment_size] * segment_count
    offset = 0
    for i in range(1, segment_count + 1):
        size = segment_sizes[i - 1]
        segment_data = data[offset: offset + size]
        offset += size

        _write_segment(i, segment_data, flags, message)

    message.seek(0, 0)
    return message, message_length


class TestStructuredMessageDecodeStream:

    def test_empty_inner_stream(self):
        with pytest.raises(ValueError):
            StructuredMessageDecodeStream(BytesIO(), 0)

    def test_read_past_end(self):
        data = os.urandom(10)
        message_stream, length = _build_structured_message(data, len(data), StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)
        result = stream.read(100)
        assert result == data

        result = stream.read(100)
        assert result == b''

    @pytest.mark.parametrize("size, segment_size, flags", [
        (0, 0, StructuredMessageProperties.NONE),
        (0, 0, StructuredMessageProperties.CRC64),
        (10, 1, StructuredMessageProperties.NONE),
        (10, 1, StructuredMessageProperties.CRC64),
        (1024, 1024, StructuredMessageProperties.NONE),
        (1024, 1024, StructuredMessageProperties.CRC64),
        (1024, 512, StructuredMessageProperties.NONE),
        (1024, 512, StructuredMessageProperties.CRC64),
        (1024, 200, StructuredMessageProperties.NONE),
        (1024, 200, StructuredMessageProperties.CRC64),
        (123456, 1234, StructuredMessageProperties.NONE),
        (123456, 1234, StructuredMessageProperties.CRC64),
        (10 * 1024 * 1024, 4 * 1024 * 1024, StructuredMessageProperties.NONE),
        (10 * 1024 * 1024, 4 * 1024 * 1024, StructuredMessageProperties.CRC64),
    ])
    def test_read_all(self, size, segment_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = StructuredMessageDecodeStream(message_stream, length)
        content = stream.read()

        assert content == data

    @pytest.mark.parametrize("size, segment_size, chunk_size, flags", [
        (10, 10, 1, StructuredMessageProperties.NONE),
        (10, 10, 1, StructuredMessageProperties.CRC64),
        (1024, 512, 512, StructuredMessageProperties.NONE),
        (1024, 512, 512, StructuredMessageProperties.CRC64),
        (1024, 512, 123, StructuredMessageProperties.NONE),
        (1024, 512, 123, StructuredMessageProperties.CRC64),
        (1024, 200, 512, StructuredMessageProperties.NONE),
        (1024, 200, 512, StructuredMessageProperties.CRC64),
        (10 * 1024 * 1024, 4 * 1024 * 1024, 1 * 1024 * 1024, StructuredMessageProperties.NONE),
        (10 * 1024 * 1024, 4 * 1024 * 1024, 1 * 1024 * 1024, StructuredMessageProperties.CRC64),
    ])
    def test_read_chunks(self, size, segment_size, chunk_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = StructuredMessageDecodeStream(message_stream, length)
        read = 0
        content = b''
        while read < len(data):
            chunk = stream.read(chunk_size)
            content += chunk
            read += chunk_size

        assert content == data

    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    def test_random_reads(self, data_size):
        pass

    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    def test_random_segment_sizes(self, data_size):
        segment_sizes = []
        count = 0
        while count < data_size:
            size = random.randint(10, data_size // 3)
            size = min(size, data_size - count)
            segment_sizes.append(size)
            count += size

        data = os.urandom(data_size)
        message_stream, length = _build_structured_message(data, segment_sizes, StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)
        content = stream.read()

        assert content == data
