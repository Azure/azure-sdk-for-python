# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""
Streaming tests.

Test naming convention for streaming response tests: test_{1}_{2}

1:
compress or decompress. Refers to the stream that is returned from the testserver / streams.py

2:
plain_header - text file with {Content-Type: text/plain} and {Content-Encoding: gzip}
plain_no_header - text file with {Content-Type: text/plain}
compressed_no_header - tar.gz file with {Content-Type: application/gzip}
compressed_header - tar.gz file with {Content-Type: application/gzip} and {Content-Encoding: gzip}
"""
import pytest

from corehttp.rest import HttpRequest
from corehttp.runtime import PipelineClient
from corehttp.exceptions import DecodeError

from utils import SYNC_TRANSPORTS


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_compress_plain_no_header_offline(port, transport):
    # cspell:disable-next-line
    # thanks to Daisy Cisneros for this test!
    # expect plain text
    request = HttpRequest(method="GET", url="http://localhost:{}/streams/string".format(port))
    with transport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.iter_raw()
        content = b"".join(list(data))
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_compress_compressed_no_header_offline(port, transport):
    # expect compressed text
    client = PipelineClient("", transport=transport())
    request = HttpRequest(method="GET", url="http://localhost:{}/streams/compressed_no_header".format(port))
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_plain_header_offline(port, transport):
    request = HttpRequest(method="GET", url="http://localhost:{}/streams/compressed".format(port))
    with transport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.iter_bytes()
        with pytest.raises(DecodeError):
            list(data)


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_compressed_header_offline(port, transport):
    client = PipelineClient("")
    request = HttpRequest(method="GET", url="http://localhost:{}/streams/decompress_header".format(port))
    with transport() as sender:
        response = client.pipeline.run(request, stream=True).http_response
        response.raise_for_status()
        content = response.read()
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_plain_no_header_offline(port, transport):
    # expect plain text
    url = "http://localhost:{}/streams/string".format(port)
    client = PipelineClient(url, transport=transport())
    request = HttpRequest("GET", url=url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    decoded = content.decode("utf-8")
    assert decoded == "test"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_compress_plain_header_offline(port, transport):
    # expect plain text
    url = "http://localhost:{}/streams/plain_header".format(port)
    client = PipelineClient(url, transport=transport())
    request = HttpRequest("GET", url=url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    decoded = content.decode("utf-8")
    assert decoded == "test"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_compressed_no_header_offline(port, transport):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_no_header".format(port)
    client = PipelineClient(url, transport=transport())
    request = HttpRequest("GET", url=url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    assert content.startswith(b"\x1f\x8b")  # gzip magic number
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_compress_compressed_header_offline(port, transport):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_header".format(port)
    client = PipelineClient(url, transport=transport())
    request = HttpRequest("GET", url=url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_streaming_request_iterable(port, transport):
    url = "http://localhost:{}/streams/upload".format(port)

    class Content:
        def __iter__(self):
            yield b"test 123"

    client = PipelineClient(url, transport=transport())
    request = HttpRequest("POST", url=url, content=Content())
    response = client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_streaming_request_generator(port, transport):
    url = "http://localhost:{}/streams/upload".format(port)

    def content():
        yield b"test 123"
        yield b"test 456"

    client = PipelineClient(url, transport=transport())
    request = HttpRequest("POST", url=url, content=content())
    response = client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123test 456"
