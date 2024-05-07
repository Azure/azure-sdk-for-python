# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import zlib
import pytest
from azure.core import AsyncPipelineClient
from azure.core.exceptions import DecodeError
from utils import HTTP_REQUESTS


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_compressed_no_header_offline(port, http_request):
    # expect compressed text
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/compressed_no_header".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=False)
        with pytest.raises(UnicodeDecodeError):
            b"".join([d async for d in data]).decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_plain_no_header_offline(port, http_request):
    # expect plain text
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/string".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=True)
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_plain_header_offline(port, http_request):
    # expect plain text
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/plain_header".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=False)
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_compressed_no_header_offline(port, http_request):
    # expect compressed text
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/compressed_no_header".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=True)
        content = b"".join([d async for d in data])
        assert content.startswith(b"\x1f\x8b")  # gzip magic number
        with pytest.raises(UnicodeDecodeError):
            content.decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_compressed_header_offline(port, http_request):
    # expect compressed text
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/compressed_header".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=False)
        with pytest.raises(UnicodeDecodeError):
            b"".join([d async for d in data]).decode("utf-8")


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_plain_header_offline(port, http_request):
    # expect error
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/compressed".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=True)
        with pytest.raises((zlib.error, DecodeError)):
            b"".join([d async for d in data])


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_compress_plain_no_header_offline(port, http_request):
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/string".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=False)
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_decompress_compressed_header_offline(port, http_request):
    # expect compressed text
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/decompress_header".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=True)
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_streaming_request_iterable(port, http_request):
    url = "http://localhost:{}/streams/upload".format(port)

    class Content:
        async def __aiter__(self):
            yield b"test 123"

    client = AsyncPipelineClient("")
    request = http_request(method="POST", url=url, data=Content())
    response = await client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_streaming_request_generator(port, http_request):
    url = "http://localhost:{}/streams/upload".format(port)

    async def content():
        yield b"test 123"
        yield b"test 456"

    client = AsyncPipelineClient("")
    request = http_request(method="POST", url=url, data=content())
    response = await client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123test 456"
