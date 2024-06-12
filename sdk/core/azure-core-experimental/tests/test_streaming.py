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
from itertools import product

from azure.core import PipelineClient
from azure.core.exceptions import DecodeError

from utils import SYNC_TRANSPORTS, HTTP_REQUESTS, create_http_request


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_compress_plain_no_header_offline(port, transport, requesttype):
    # cspell:disable-next-line
    # thanks to Daisy Cisneros for this test!
    # expect plain text
    request = create_http_request(requesttype, "GET", "http://localhost:{}/streams/string".format(port))
    with transport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.iter_raw()
        content = b"".join(list(data))
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_compress_compressed_no_header_offline(port, transport, requesttype):
    # expect compressed text
    client = PipelineClient("", transport=transport())
    request = create_http_request(requesttype, "GET", "http://localhost:{}/streams/compressed_no_header".format(port))
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_decompress_plain_header_offline(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "http://localhost:{}/streams/compressed".format(port))
    with transport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.iter_bytes()
        with pytest.raises(DecodeError):
            list(data)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_decompress_compressed_header_offline(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "http://localhost:{}/streams/decompress_header".format(port))
    with transport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        content = response.read()
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_decompress_plain_no_header_offline(port, transport, requesttype):
    # expect plain text
    url = "http://localhost:{}/streams/string".format(port)
    client = PipelineClient(url, transport=transport())
    request = create_http_request(requesttype, "GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    decoded = content.decode("utf-8")
    assert decoded == "test"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_compress_plain_header_offline(port, transport, requesttype):
    # expect plain text
    url = "http://localhost:{}/streams/plain_header".format(port)
    client = PipelineClient(url, transport=transport())
    request = create_http_request(requesttype, "GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    decoded = content.decode("utf-8")
    assert decoded == "test"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_decompress_compressed_no_header_offline(port, transport, requesttype):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_no_header".format(port)
    client = PipelineClient(url, transport=transport())
    request = create_http_request(requesttype, "GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    assert content.startswith(b"\x1f\x8b")  # gzip magic number
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_compress_compressed_header_offline(port, transport, requesttype):
    # expect compressed text
    url = "http://localhost:{}/streams/compressed_header".format(port)
    client = PipelineClient(url, transport=transport())
    request = create_http_request(requesttype, "GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_streaming_request_iterable(port, transport, requesttype):
    url = "http://localhost:{}/streams/upload".format(port)

    class Content:
        def __iter__(self):
            yield b"test 123"

    client = PipelineClient(url, transport=transport())
    request = create_http_request(requesttype, "POST", url, content=Content())
    response = client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_streaming_request_generator(port, transport, requesttype):
    url = "http://localhost:{}/streams/upload".format(port)

    def content():
        yield b"test 123"
        yield b"test 456"

    client = PipelineClient(url, transport=transport())
    request = create_http_request(requesttype, "POST", url, content=content())
    response = client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123test 456"
