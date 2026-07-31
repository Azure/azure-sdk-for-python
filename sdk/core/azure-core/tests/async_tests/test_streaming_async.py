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

try:
    import brotli as _brotli

    _HAS_BROTLI = True
except ImportError:
    _brotli = None
    _HAS_BROTLI = False


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


class _MockStreamContent:
    """Yields the pre-split chunks regardless of the requested read size,
    forcing the streaming generator to decode across multiple chunks."""

    def __init__(self, chunks):
        self._chunks = list(chunks)

    async def read(self, size):
        if self._chunks:
            return self._chunks.pop(0)
        return b""


class _MockInternalResponse:
    def __init__(self, chunks, headers):
        self.content = _MockStreamContent(chunks)
        self.headers = headers
        self.closed = False

    def close(self):
        self.closed = True


class _MockStreamResponse:
    def __init__(self, internal_response, block_size):
        self.request = None
        self.internal_response = internal_response
        self.block_size = block_size


def _split(data, size):
    return [data[i : i + size] for i in range(0, len(data), size)]


@pytest.mark.asyncio
async def test_streaming_decompress_multichunk_gzip():
    from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

    payload = b"the quick brown fox jumps over the lazy dog. " * 100
    compressor = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
    compressed = compressor.compress(payload) + compressor.flush()
    chunks = _split(compressed, 7)
    assert len(chunks) > 1  # ensure multiple compressed chunks
    internal = _MockInternalResponse(chunks, {"Content-Encoding": "gzip"})
    response = _MockStreamResponse(internal, block_size=7)
    generator = AioHttpStreamDownloadGenerator(None, response, decompress=True)
    decoded = b"".join([chunk async for chunk in generator])
    assert decoded == payload


@pytest.mark.asyncio
async def test_streaming_decompress_multichunk_deflate():
    from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

    payload = b"the quick brown fox jumps over the lazy dog. " * 100
    compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
    compressed = compressor.compress(payload) + compressor.flush()
    chunks = _split(compressed, 7)
    assert len(chunks) > 1
    internal = _MockInternalResponse(chunks, {"Content-Encoding": "deflate"})
    response = _MockStreamResponse(internal, block_size=7)
    generator = AioHttpStreamDownloadGenerator(None, response, decompress=True)
    decoded = b"".join([chunk async for chunk in generator])
    assert decoded == payload


@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_BROTLI, reason="Brotli support is not available")
async def test_streaming_decompress_singlechunk_brotli():
    from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

    payload = b"hello world"
    compressed = _brotli.compress(payload)
    internal = _MockInternalResponse([compressed], {"Content-Encoding": "br"})
    response = _MockStreamResponse(internal, block_size=len(compressed))
    generator = AioHttpStreamDownloadGenerator(None, response, decompress=True)
    decoded = b"".join([chunk async for chunk in generator])
    assert decoded == payload


@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_BROTLI, reason="Brotli support is not available")
async def test_streaming_decompress_multichunk_brotli():
    from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

    # Large enough to span many chunks and exceed the decompressor's per-call output cap,
    # exercising the cross-chunk stateful decode and the per-chunk drain loop.
    payload = b"the quick brown fox jumps over the lazy dog. " * 1000
    compressed = _brotli.compress(payload)
    chunks = _split(compressed, 7)
    assert len(chunks) > 1  # ensure multiple compressed chunks
    internal = _MockInternalResponse(chunks, {"Content-Encoding": "br"})
    response = _MockStreamResponse(internal, block_size=7)
    generator = AioHttpStreamDownloadGenerator(None, response, decompress=True)
    decoded = b"".join([chunk async for chunk in generator])
    assert decoded == payload


@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_BROTLI, reason="Brotli support is not available")
async def test_streaming_brotli_no_decompress():
    from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

    payload = b"hello world"
    compressed = _brotli.compress(payload)
    chunks = _split(compressed, 4)
    internal = _MockInternalResponse(list(chunks), {"Content-Encoding": "br"})
    response = _MockStreamResponse(internal, block_size=4)
    generator = AioHttpStreamDownloadGenerator(None, response, decompress=False)
    raw = b"".join([chunk async for chunk in generator])
    assert raw == compressed


@pytest.mark.asyncio
async def test_streaming_brotli_missing_library(monkeypatch):
    import aiohttp.compression_utils

    monkeypatch.setattr(aiohttp.compression_utils, "HAS_BROTLI", False)
    from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

    internal = _MockInternalResponse([b"\x8b\x01\x80test\x03"], {"Content-Encoding": "br"})
    response = _MockStreamResponse(internal, block_size=64)
    generator = AioHttpStreamDownloadGenerator(None, response, decompress=True)
    with pytest.raises(DecodeError) as err:
        await generator.__anext__()
    assert "Content-Encoding: br" in str(err.value)
    assert "Brotli" in str(err.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
@pytest.mark.skipif(not _HAS_BROTLI, reason="Brotli support is not available")
async def test_decompress_brotli_header_offline(port, http_request):
    # expect plain text decoded from a streamed Content-Encoding: br body
    client = AsyncPipelineClient("")
    async with client:
        request = http_request(method="GET", url="http://localhost:{}/streams/brotli_decompress_header".format(port))
        pipeline_response = await client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline, decompress=True)
        decoded = b"".join([d async for d in data]).decode("utf-8")
        assert decoded == "test"
