# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import math
import os
import random
from io import BytesIO
from typing import AsyncIterator, List, Optional, Tuple, Union

import pytest
import pytest_asyncio
from azure.storage.blob._shared.streams import (
    StructuredMessageConstants,
    StructuredMessageProperties,
)
from azure.storage.blob._shared.streams_async import AsyncStructuredMessageDecoder
from azure.storage.extensions import crc64


async def _async_iter_bytes(data: bytes, chunk_size: int = 1024) -> AsyncIterator[bytes]:
    """Convert bytes to an AsyncIterator[bytes] with the given chunk size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def _write_segment(
    number: int,
    data: bytes,
    data_crc: Optional[int],
    stream: BytesIO,
) -> None:
    stream.write(number.to_bytes(2, 'little'))  # Segment number
    stream.write(len(data).to_bytes(8, 'little'))  # Segment length
    stream.write(data)  # Segment content
    if data_crc is not None:
        stream.write(data_crc.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))


def _build_structured_message(
    data: bytes,
    segment_size: Union[int, List[int]],
    flags: StructuredMessageProperties,
    invalidate_crc_segment: Optional[int] = None,
) -> Tuple[BytesIO, int]:
    if isinstance(segment_size, list):
        segment_count = len(segment_size)
    else:
        segment_count = math.ceil(len(data) / segment_size) or 1
    segment_footer_length = StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0

    message_length = (
        StructuredMessageConstants.V1_HEADER_LENGTH +
        ((StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH + segment_footer_length) * segment_count) +
        len(data) +
        (StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0))

    message = BytesIO()
    message_crc = 0

    # Message Header
    message.write(b'\x01')  # Version
    message.write(message_length.to_bytes(8, 'little'))  # Message length
    message.write(int(flags).to_bytes(2, 'little'))  # Flags
    message.write(segment_count.to_bytes(2, 'little'))  # Num segments

    # Special case for 0 length content
    if len(data) == 0:
        crc = 0 if StructuredMessageProperties.CRC64 in flags else None
        _write_segment(1, data, crc, message)
    else:
        # Segments
        segment_sizes = segment_size if isinstance(segment_size, list) else [segment_size] * segment_count
        offset = 0
        for i in range(1, segment_count + 1):
            size = segment_sizes[i - 1]
            segment_data = data[offset: offset + size]
            offset += size

            segment_crc = None
            if StructuredMessageProperties.CRC64 in flags:
                segment_crc = crc64.compute(segment_data, 0)
                if i == invalidate_crc_segment:
                    segment_crc += 5
            _write_segment(i, segment_data, segment_crc, message)

            message_crc = crc64.compute(segment_data, message_crc)

    # Message footer
    if StructuredMessageProperties.CRC64 in flags:
        if invalidate_crc_segment == -1:
            message_crc += 5
        message.write(message_crc.to_bytes(StructuredMessageConstants.CRC64_LENGTH, 'little'))

    message.seek(0, 0)
    return message, message_length


class TestAsyncStructuredMessageDecoder:

    @pytest.mark.asyncio
    async def test_empty_inner_stream(self):
        with pytest.raises(ValueError):
            AsyncStructuredMessageDecoder(_async_iter_bytes(b''), 0)

    @pytest.mark.asyncio
    async def test_read_past_end(self):
        data = os.urandom(10)
        message_stream, length = _build_structured_message(data, len(data), StructuredMessageProperties.CRC64)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)
        result = await stream.read(100)
        assert result == data

        result = await stream.read(100)
        assert result == b''

    @pytest.mark.asyncio
    @pytest.mark.parametrize("size, segment_size, flags", [
        (0, 1, StructuredMessageProperties.NONE),
        (0, 1, StructuredMessageProperties.CRC64),
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
    async def test_read_all(self, size, segment_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)
        content = await stream.read()

        assert content == data

    @pytest.mark.asyncio
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
    async def test_read_chunks(self, size, segment_size, chunk_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)
        read = 0
        content = b''
        while read < len(data):
            chunk = await stream.read(chunk_size)
            content += chunk
            read += chunk_size

        assert content == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    async def test_random_reads(self, data_size):
        data = os.urandom(data_size)
        message_stream, length = _build_structured_message(data, data_size // 3, StructuredMessageProperties.CRC64)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)

        count = 0
        content = b''
        while count < data_size:
            read_size = random.randint(10, data_size // 3)
            read_size = min(read_size, data_size - count)

            content += await stream.read(read_size)
            count += read_size

        assert content == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("size, segment_size, block_size, flags", [
        (0, 1, 1, StructuredMessageProperties.NONE),
        (0, 1, 1, StructuredMessageProperties.CRC64),
        (1, 1, 1, StructuredMessageProperties.NONE),
        (1, 1, 1, StructuredMessageProperties.CRC64),
        (10, 10, 1, StructuredMessageProperties.NONE),
        (10, 10, 1, StructuredMessageProperties.CRC64),
        (1024, 512, 512, StructuredMessageProperties.NONE),
        (1024, 512, 512, StructuredMessageProperties.CRC64),
        (1024, 512, 123, StructuredMessageProperties.NONE),
        (1024, 512, 123, StructuredMessageProperties.CRC64),
        (1024, 200, 512, StructuredMessageProperties.NONE),
        (1024, 200, 512, StructuredMessageProperties.CRC64),
        (1024, 200, 1024, StructuredMessageProperties.NONE),
        (1024, 200, 1024, StructuredMessageProperties.CRC64),
        (1024, 200, 50, StructuredMessageProperties.NONE),
        (1024, 200, 50, StructuredMessageProperties.CRC64),
        (100 * 1024, 4 * 1024, 7 * 1024, StructuredMessageProperties.NONE),
        (100 * 1024, 4 * 1024, 7 * 1024, StructuredMessageProperties.CRC64),
    ])
    async def test_iterate(self, size, segment_size, block_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        decoder = AsyncStructuredMessageDecoder(
            _async_iter_bytes(message_stream.getvalue()), length, block_size=block_size)
        content = b''
        async for chunk in decoder:
            content += chunk

        assert content == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    async def test_random_segment_sizes(self, data_size):
        segment_sizes = []
        count = 0
        while count < data_size:
            size = random.randint(10, data_size // 3)
            size = min(size, data_size - count)
            segment_sizes.append(size)
            count += size

        data = os.urandom(data_size)
        message_stream, length = _build_structured_message(data, segment_sizes, StructuredMessageProperties.CRC64)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)
        content = await stream.read()

        assert content == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_segment", [1, 2, 3, -1])
    async def test_crc64_mismatch_read_all(self, invalid_segment):
        data = os.urandom(3 * 1024)
        message_stream, length = _build_structured_message(
            data,
            1024,
            StructuredMessageProperties.CRC64,
            invalid_segment)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)
        with pytest.raises(ValueError) as e:
            await stream.read()
        assert 'CRC64 mismatch' in str(e.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_segment", [1, 2, 3, -1])
    async def test_crc64_mismatch_read_chunks(self, invalid_segment):
        data = os.urandom(3 * 1024)
        message_stream, length = _build_structured_message(
            data,
            1024,
            StructuredMessageProperties.CRC64,
            invalid_segment)

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(message_stream.getvalue()), length)
        # Since we only check CRC on segment borders, some reads will succeed, but we test
        # to ensure eventually the stream reading will error out.
        with pytest.raises(ValueError) as e:
            read = 0
            while read < len(data):
                await stream.read(512)

        assert 'CRC64 mismatch' in str(e.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_invalid_message_version(self, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 512, flags)

        # Corrupt the version byte
        raw = bytearray(message_stream.getvalue())
        raw[0] = 0xFF

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(bytes(raw)), length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message_length", [100, 1234567])  # Correct value: 1057
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_message_length(self, message_length, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 512, flags)

        raw = bytearray(message_stream.getvalue())
        raw[1:9] = int.to_bytes(message_length, 8, 'little')

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(bytes(raw)), length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("segment_count", [2, 123])  # Correct value: 4
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_segment_count(self, segment_count, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        raw = bytearray(message_stream.getvalue())
        raw[11:13] = int.to_bytes(segment_count, 2, 'little')

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(bytes(raw)), length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("segment_number", [1, 123])  # Correct value: 2
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_segment_number(self, segment_number, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        # Change the second segment to be the incorrect number
        position = (StructuredMessageConstants.V1_HEADER_LENGTH +
                    StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH +
                    256 +
                    (StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0))
        raw = bytearray(message_stream.getvalue())
        raw[position:position + 2] = int.to_bytes(segment_number, 2, 'little')

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(bytes(raw)), length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("segment_size", [123, 345])  # Correct value: 256
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_segment_size(self, segment_size, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        # Change the second segment to be the incorrect size
        position = (StructuredMessageConstants.V1_HEADER_LENGTH +
                    StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH +
                    256 +
                    (StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in flags else 0) +
                    2)
        raw = bytearray(message_stream.getvalue())
        raw[position:position + 8] = int.to_bytes(segment_size, 8, 'little')

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(bytes(raw)), length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("segment_size", [123, 345])  # Correct value: 256
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_segment_size_single_segment(self, segment_size, flags):
        data = os.urandom(256)
        message_stream, length = _build_structured_message(data, 256, flags)

        raw = bytearray(message_stream.getvalue())
        raw[15:23] = int.to_bytes(segment_size, 8, 'little')

        stream = AsyncStructuredMessageDecoder(_async_iter_bytes(bytes(raw)), length)
        with pytest.raises(ValueError):
            await stream.read()
