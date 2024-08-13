# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import random
from io import BytesIO

import pytest
from azure.storage.blob._shared.streams import (
    StructuredMessageConstants,
    StructuredMessageProperties,
)
from azure.storage.blob._shared.streams_async import AsyncIterStreamer, StructuredMessageDecodeStream

from test_helpers_async import AsyncStream
from test_streams import _build_structured_message


@pytest.mark.asyncio
class TestStructuredMessageDecodeStreamAsync:

    def test_empty_inner_stream(self):
        with pytest.raises(ValueError):
            StructuredMessageDecodeStream(BytesIO(), 0)

    async def test_read_past_end(self):
        data = os.urandom(10)
        message_stream, length = _build_structured_message(data, len(data), StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)
        result = await stream.read(100)
        assert result == data

        result = await stream.read(100)
        assert result == b''

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

        stream = StructuredMessageDecodeStream(message_stream, length)
        content = await stream.read()

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
    async def test_read_chunks(self, size, segment_size, chunk_size, flags):
        data = os.urandom(size)
        message_stream, length = _build_structured_message(data, segment_size, flags)

        stream = StructuredMessageDecodeStream(message_stream, length)
        read = 0
        content = b''
        while read < len(data):
            chunk = await stream.read(chunk_size)
            content += chunk
            read += chunk_size

        assert content == data

    @pytest.mark.parametrize("data_size", [100, 1024, 10 * 1024, 100 * 1024])
    async def test_random_reads(self, data_size):
        data = os.urandom(data_size)
        message_stream, length = _build_structured_message(data, data_size // 3, StructuredMessageProperties.CRC64)

        stream = StructuredMessageDecodeStream(message_stream, length)

        count = 0
        content = b''
        while count < data_size:
            read_size = random.randint(10, data_size // 3)
            read_size = min(read_size, data_size - count)

            content += await stream.read(read_size)
            count += read_size

        assert content == data

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

        stream = StructuredMessageDecodeStream(message_stream, length)
        content = await stream.read()

        assert content == data

    @pytest.mark.parametrize("invalid_segment", [1, 2, 3, -1])
    async def test_crc64_mismatch_read_all(self, invalid_segment):
        data = os.urandom(3 * 1024)
        message_stream, length = _build_structured_message(
            data,
            1024,
            StructuredMessageProperties.CRC64,
            invalid_segment)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError) as e:
            await stream.read()
        assert 'CRC64 mismatch' in str(e.value)

    @pytest.mark.parametrize("invalid_segment", [1, 2, 3, -1])
    async def test_crc64_mismatch_read_chunks(self, invalid_segment):
        data = os.urandom(3 * 1024)
        message_stream, length = _build_structured_message(
            data,
            1024,
            StructuredMessageProperties.CRC64,
            invalid_segment)

        stream = StructuredMessageDecodeStream(message_stream, length)
        # Since we only check CRC on segment borders, some reads will succeed, but we test
        # to ensure eventually the stream reading will error out.
        with pytest.raises(ValueError) as e:
            read = 0
            while read < len(data):
                await stream.read(512)

        assert 'CRC64 mismatch' in str(e.value)

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_invalid_message_version(self, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 512, flags)

        # Stream already set to front
        message_stream.write(b'\xFF')
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.parametrize("message_length", [100, 1234567])  # Correct value: 1057
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_message_length(self, message_length, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 512, flags)

        message_stream.seek(1)
        message_stream.write(int.to_bytes(message_length, 8, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.parametrize("segment_count", [2, 123])  # Correct value: 4
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_segment_count(self, segment_count, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 256, flags)

        message_stream.seek(11)
        message_stream.write(int.to_bytes(segment_count, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            await stream.read()

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
        message_stream.seek(position)
        message_stream.write(int.to_bytes(segment_number, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            await stream.read()

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
        message_stream.seek(position)
        message_stream.write(int.to_bytes(segment_size, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.parametrize("segment_size", [123, 345])  # Correct value: 256
    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_incorrect_segment_size_single_segment(self, segment_size, flags):
        data = os.urandom(256)
        message_stream, length = _build_structured_message(data, 256, flags)

        message_stream.seek(15)
        message_stream.write(int.to_bytes(segment_size, 2, 'little'))
        message_stream.seek(0)

        stream = StructuredMessageDecodeStream(message_stream, length)
        with pytest.raises(ValueError):
            await stream.read()

    @pytest.mark.parametrize("flags", [StructuredMessageProperties.NONE, StructuredMessageProperties.CRC64])
    async def test_read_async_stream(self, flags):
        data = os.urandom(1024)
        message_stream, length = _build_structured_message(data, 500, flags)
        async_message_stream = AsyncStream(message_stream.read())

        stream = StructuredMessageDecodeStream(async_message_stream, length)
        content = await stream.read()

        assert content == data


async def data_generator(data, chunk_size):
    total = len(data)
    offset = 0
    while offset < total:
        yield data[offset:offset + chunk_size]
        offset += chunk_size


@pytest.mark.asyncio
class TestAsyncIterStreamer:
    async def test_empty(self):
        async def empty_gen():
            yield b''

        async def empty_gen2():
            if False:
                yield b''

        stream = AsyncIterStreamer(empty_gen())
        assert await stream.read() == b''
        stream = AsyncIterStreamer(empty_gen2())
        assert await stream.read() == b''

    @pytest.mark.parametrize("size, chunk_size", [
        (0, 0),
        (10, 1),
        (1024, 1024),
        (1024, 512),
        (1024, 100),
        (1024, 5000)
    ])
    async def test_read_all(self, size, chunk_size):
        data = os.urandom(size)
        generator = data_generator(data, chunk_size)

        stream = AsyncIterStreamer(generator)
        assert await stream.read() == data

    @pytest.mark.parametrize("size, chunk_size, read_size", [
        (10, 1, 1),
        (10, 1, 4),
        (1024, 1024, 1024),
        (1024, 512, 512),
        (1024, 100, 100),
        (1024, 100, 37),
        (1024, 5000, 100)
    ])
    async def test_read_size(self, size, chunk_size, read_size):
        data = os.urandom(size)
        generator = data_generator(data, chunk_size)

        stream = AsyncIterStreamer(generator)
        offset = 0
        result = bytearray()
        while offset < len(data):
            chunk = await stream.read(read_size)
            result.extend(chunk)
            offset += read_size
        assert bytes(result) == data
