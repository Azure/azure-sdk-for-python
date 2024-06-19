# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

import pytest
from azure.storage.blob._shared.streams_async import AsyncIterStreamer


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
