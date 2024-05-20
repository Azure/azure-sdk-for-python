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
import pytest
from azure.core.pipeline.transport import RequestsTransport
from azure.core import PipelineClient
from azure.core.exceptions import DecodeError
from azure.core.pipeline.transport import RequestsTransport
from utils import HTTP_REQUESTS


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_plain_no_header_offline(port, http_request):
    # cspell:disable-next-line
    # thanks to Daisy Cisneros for this test!
    # expect plain text
    request = http_request(method="GET", url="http://localhost:{}/streams/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.stream_download(sender, decompress=False)
        content = b"".join(list(data))
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_compressed_no_header_offline(port, http_request):
    # expect compressed text
    client = PipelineClient("")
    request = http_request(method="GET", url="http://localhost:{}/streams/compressed_no_header".format(port))
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=False)
    content = b"".join(list(data))
    with pytest.raises(UnicodeDecodeError):
        decoded = content.decode("utf-8")


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_plain_header_offline(port, http_request):
    request = http_request(method="GET", url="http://localhost:{}/streams/compressed".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.stream_download(sender, decompress=True)
        with pytest.raises(DecodeError):
            list(data)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_compressed_header_offline(port, http_request):
    client = PipelineClient("")
    request = http_request(method="GET", url="http://localhost:{}/streams/decompress_header".format(port))
    with RequestsTransport() as sender:
        response = client._pipeline.run(request, stream=True).http_response
        response.raise_for_status()
        data = response.stream_download(sender, decompress=True)
        content = b"".join(list(data))
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_plain_no_header_offline(port, http_request):
    # expect plain text
    request = http_request(method="GET", url="http://localhost:{}/streams/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.stream_download(sender, decompress=True)
        content = b"".join(list(data))
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_plain_header_offline(port, http_request):
    # expect plain text
    request = http_request(method="GET", url="http://localhost:{}/streams/plain_header".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.stream_download(sender, decompress=False)
        content = b"".join(list(data))
        decoded = content.decode("utf-8")
        assert decoded == "test"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_compressed_no_header_offline(port, http_request):
    # expect compressed text
    client = PipelineClient("")
    request = http_request(method="GET", url="http://localhost:{}/streams/compressed_no_header".format(port))
    response = client._pipeline.run(request, stream=True).http_response
    response.raise_for_status()
    data = response.stream_download(client._pipeline, decompress=True)
    content = b"".join(list(data))
    assert content.startswith(b"\x1f\x8b")  # gzip magic number
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_compressed_header_offline(port, http_request):
    # expect compressed text
    client = PipelineClient("")
    request = http_request(method="GET", url="http://localhost:{}/streams/compressed_header".format(port))
    response = client._pipeline.run(request, stream=True).http_response
    response.raise_for_status()
    data = response.stream_download(client._pipeline, decompress=False)
    content = b"".join(list(data))
    with pytest.raises(UnicodeDecodeError):
        content.decode("utf-8")


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_streaming_request_iterable(port, http_request):
    url = "http://localhost:{}/streams/upload".format(port)

    class Content:
        def __iter__(self):
            yield b"test 123"

    client = PipelineClient("")
    request = http_request(method="POST", url=url, data=Content())
    response = client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123"


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_streaming_request_generator(port, http_request):
    url = "http://localhost:{}/streams/upload".format(port)

    def content():
        yield b"test 123"
        yield b"test 456"

    client = PipelineClient("")
    request = http_request(method="POST", url=url, data=content())
    response = client.send_request(request)
    response.raise_for_status()
    assert response.text() == "test 123test 456"
