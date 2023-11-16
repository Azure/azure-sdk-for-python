# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from corehttp.rest import HttpRequest
from corehttp.runtime import PipelineClient
from corehttp.exceptions import DecodeError

from utils import SYNC_TRANSPORTS


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_plain_no_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    decoded = content.decode("utf-8")
    assert decoded == "test"


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


@pytest.mark.live_test_only
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_compress_plain_no_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    decoded = content.decode("utf-8")
    assert decoded == "test"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_compressed_no_header(transport):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    try:
        content.decode("utf-8")
        assert False
    except UnicodeDecodeError:
        pass


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


@pytest.mark.live_test_only
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_compress_compressed_no_header(transport):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    # data = response.stream_download(client.pipeline, decompress=False)
    # content = b"".join(list(data))
    content = response.read()
    try:
        decoded = content.decode("utf-8")
        assert False
    except UnicodeDecodeError:
        pass


@pytest.mark.live_test_only
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_plain_header(transport):
    # expect error
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_bytes()
    with pytest.raises(DecodeError):
        list(data)


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
def test_compress_plain_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.txt".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    decoded = content.decode("utf-8")
    assert decoded == "test"


@pytest.mark.live_test_only
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_compressed_header(transport):
    # expect plain text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    content = response.read()
    decoded = content.decode("utf-8")
    assert decoded == "test"


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
def test_compress_compressed_header(transport):
    # expect compressed text
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    client = PipelineClient(account_url, transport=transport())
    request = HttpRequest("GET", url)
    pipeline_response = client.pipeline.run(request, stream=True)
    response = pipeline_response.http_response
    data = response.iter_raw()
    content = b"".join(list(data))
    try:
        decoded = content.decode("utf-8")
        assert False
    except UnicodeDecodeError:
        pass
