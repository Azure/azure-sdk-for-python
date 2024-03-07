# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""
Asynchronous streaming tests.

Test naming convention: test_{1}_{2}

1:
compress or decompress. Refers to the stream that is returned from the testserver / streams.py

2:
plain_header - text file with {Content-Type: text/plain} and {Content-Encoding: gzip}
plain_no_header - text file with {Content-Type: text/plain}
compressed_no_header - tar.gz file with {Content-Type: application/gzip}
compressed_header - tar.gz file with {Content-Type: application/gzip} and {Content-Encoding: gzip}
"""
import zlib

import pytest
from corehttp.rest import HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.exceptions import DecodeError

from utils import ASYNC_TRANSPORTS


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_plain_no_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_plain_no_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_compressed_no_header(transport):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        content = b"".join([d async for d in data])
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_compressed_no_header(transport):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b"".join([d async for d in data])
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_compressed_no_header_offline(port, transport):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_no_header".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b"".join([d async for d in data])
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_plain_header(transport):
    # expect error
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        with pytest.raises((zlib.error, DecodeError)):
            b"".join([d async for d in data])


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_plain_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_compressed_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.live_test_only
@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_compressed_header(transport):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = AsyncPipelineClient(account_url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b"".join([d async for d in data])
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_plain_no_header_offline(port, transport):
    # expect plain text
    url = "http://localhost:{}/streams/string".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_plain_header_offline(port, transport):
    # expect plain text
    url = "http://localhost:{}/streams/plain_header".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_compressed_no_header_offline(port, transport):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_no_header".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        content = b"".join([d async for d in data])
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_compressed_header_offline(port, transport):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_header".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        content = b"".join([d async for d in data])
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_plain_header_offline(port, transport):
    # expect error
    url = "http://localhost:{}/streams/compressed".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        with pytest.raises((zlib.error, DecodeError)):
            b"".join([d async for d in data])


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_compress_plain_no_header_offline(port, transport):
    url = "http://localhost:{}/streams/string".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_raw()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_compressed_header_offline(port, transport):
    # expect compressed text
    url = "http://localhost:{}/streams/decompress_header".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    async with client:
        request = HttpRequest("GET", url)
        pipeline_response = await client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"
