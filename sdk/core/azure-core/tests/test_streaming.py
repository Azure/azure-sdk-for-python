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
from azure.core.exceptions import DecodeError, HttpResponseError
from azure.core.pipeline.transport import RequestsTransport
from utils import HTTP_REQUESTS

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_plain_no_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=True)
    content = b"".join(list(data))
    decoded = content.decode('utf-8')
    assert decoded == "test"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_plain_no_header_offline(port, http_request):
    # thanks to Daisy Cisneros for this test!
    # expect plain text
    request = http_request(method="GET", url="http://localhost:{}/streams/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request, stream=True)
        response.raise_for_status()
        data = response.stream_download(sender, decompress=False)
        content = b"".join(list(data))
        decoded = content.decode('utf-8')
        assert decoded == "test"

@pytest.mark.live_test_only
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_plain_no_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=False)
    content = b"".join(list(data))
    decoded = content.decode('utf-8')
    assert decoded == "test"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_compressed_no_header(http_request):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=True)
    content = b"".join(list(data))
    try:
        decoded = content.decode('utf-8')
        assert False
    except UnicodeDecodeError:
        pass

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
        decoded = content.decode('utf-8')

@pytest.mark.live_test_only
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_compressed_no_header(http_request):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=False)
    content = b"".join(list(data))
    try:
        decoded = content.decode('utf-8')
        assert False
    except UnicodeDecodeError:
        pass

@pytest.mark.live_test_only
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_plain_header(http_request):
    # expect error
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=True)
    with pytest.raises(DecodeError):
        list(data)

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
def test_compress_plain_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=False)
    content = b"".join(list(data))
    decoded = content.decode('utf-8')
    assert decoded == "test"

@pytest.mark.live_test_only
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_compressed_header(http_request):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=True)
    content = b"".join(list(data))
    decoded = content.decode('utf-8')
    assert decoded == "test"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_decompress_compressed_header_offline(port, http_request):
    client = PipelineClient("")
    request = http_request(method="GET", url="http://localhost:{}/streams/decompress_header".format(port))
    with RequestsTransport() as sender:
        response = client._pipeline.run(request, stream=True).http_response
        response.raise_for_status()
        data = response.stream_download(sender, decompress=True)
        content = b"".join(list(data))
        decoded = content.decode('utf-8')
        assert decoded == "test"

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_compress_compressed_header(http_request):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = PipelineClient(account_url)
    request = http_request("GET", url)
    pipeline_response = client._pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.stream_download(client._pipeline, decompress=False)
    content = b"".join(list(data))
    try:
        decoded = content.decode('utf-8')
        assert False
    except UnicodeDecodeError:
        pass
