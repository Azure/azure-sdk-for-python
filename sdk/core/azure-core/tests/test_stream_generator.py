# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import requests
from azure.core.pipeline.transport import (
    HttpTransport,
    RequestsTransport,
)
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.transport._requests_basic import StreamDownloadGenerator
try:
    from unittest import mock
except ImportError:
    import mock
import pytest
from utils import HTTP_RESPONSES, REQUESTS_TRANSPORT_RESPONSES, create_http_response, create_transport_response, request_and_responses_product

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_connection_error_response(http_request, http_response):
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
            request = http_request('GET', 'http://localhost/')
            response = create_http_response(http_response, request, None)
            response.status_code = 200
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

    class MockInternalResponse():
        def __init__(self):
            self.raw = MockTransport()

        def close(self):
            pass

    http_request = http_request('GET', 'http://localhost/')
    pipeline = Pipeline(MockTransport())
    http_response = create_http_response(http_response, http_request, None)
    http_response.internal_response = MockInternalResponse()
    stream = StreamDownloadGenerator(pipeline, http_response, decompress=False)
    with mock.patch('time.sleep', return_value=None):
        with pytest.raises(requests.exceptions.ConnectionError):
            stream.__next__()

@pytest.mark.parametrize("http_response", REQUESTS_TRANSPORT_RESPONSES)
def test_response_streaming_error_behavior(http_response):
    # Test to reproduce https://github.com/Azure/azure-sdk-for-python/issues/16723
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

    s = FakeStreamWithConnectionError()
    req_response.raw = FakeStreamWithConnectionError()

    response = create_transport_response(
        http_response,
        req_request,
        req_response,
        block_size,
    )

    def mock_run(self, *args, **kwargs):
        return PipelineResponse(
            None,
            requests.Response(),
            None,
        )

    transport = RequestsTransport()
    pipeline = Pipeline(transport)
    pipeline.run = mock_run
    downloader = response.stream_download(pipeline, decompress=False)
    with pytest.raises(requests.exceptions.ConnectionError):
        full_response = b"".join(downloader)
