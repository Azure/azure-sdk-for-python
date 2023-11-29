# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock

import requests
from corehttp.rest import HttpRequest
from corehttp.transport import HttpTransport
from corehttp.runtime.pipeline import Pipeline
from corehttp.rest._requests_basic import StreamDownloadGenerator, RestRequestsTransportResponse
import pytest

from utils import HTTP_RESPONSES, create_http_response, create_transport_response


@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
def test_connection_error_response(http_response):
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def close(self):
            pass

        def open(self):
            pass

        def send(self, request, **kwargs):
            request = HttpRequest("GET", "http://localhost/")
            response = create_http_response(http_response, request, None, status_code=200)
            return response

        def next(self):
            self.__next__()

        def __next__(self):
            if self._count == 0:
                self._count += 1
                raise requests.exceptions.ConnectionError

        def stream(self, chunk_size, decode_content=False):
            if self._count == 0:
                self._count += 1
                raise requests.exceptions.ConnectionError
            while True:
                yield b"test"

    class MockInternalResponse:
        def __init__(self):
            self.raw = MockTransport()

        def close(self):
            pass

    http_request = HttpRequest("GET", "http://localhost/")
    pipeline = Pipeline(MockTransport())
    http_response = create_http_response(http_response, http_request, MockInternalResponse())
    stream = StreamDownloadGenerator(pipeline, http_response, decompress=False)
    with mock.patch("time.sleep", return_value=None):
        with pytest.raises(requests.exceptions.ConnectionError):
            stream.__next__()


def test_response_streaming_error_behavior():
    block_size = 103
    total_response_size = 500
    req_response = requests.Response()
    req_request = requests.Request()

    class FakeStreamWithConnectionError:
        # fake object for urllib3.response.HTTPResponse
        def __init__(self):
            self.total_response_size = 500

        def stream(self, chunk_size, decode_content=False):
            assert chunk_size == block_size
            left = total_response_size
            while left > 0:
                if left <= block_size:
                    raise requests.exceptions.ConnectionError()
                data = b"X" * min(chunk_size, left)
                left -= len(data)
                yield data

        def read(self, chunk_size, decode_content=False):
            assert chunk_size == block_size
            if self.total_response_size > 0:
                if self.total_response_size <= block_size:
                    raise requests.exceptions.ConnectionError()
                data = b"X" * min(chunk_size, self.total_response_size)
                self.total_response_size -= len(data)
                return data

        def close(self):
            pass

    req_response.raw = FakeStreamWithConnectionError()

    response = create_transport_response(
        RestRequestsTransportResponse,
        req_request,
        req_response,
        block_size,
    )

    downloader = response.iter_raw()
    with pytest.raises(requests.exceptions.ConnectionError):
        b"".join(downloader)
