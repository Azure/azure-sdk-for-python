# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Optional

import httpx
import pytest

from corehttp.exceptions import ServiceRequestError
from corehttp.transport.httpx import HttpXTransport
from corehttp.runtime import PipelineClient
from corehttp.runtime.policies import RetryPolicy
from corehttp.rest import HttpRequest


PLACEHOLDER_ENDPOINT = "https://my-resource-group.cognitiveservices.azure.com/"


class TestHttpXTransport:
    def mock_successful_post(self, request: Optional[httpx.Request] = None) -> httpx.Response:
        return httpx.Response(200, content=b"Hello, world!")

    def mock_exception(self, request: Optional[httpx.Request] = None) -> None:
        raise httpx.TimeoutException(message="connection timed out")

    def test_send_success(self) -> None:
        mock_transport = httpx.MockTransport(self.mock_successful_post)
        transport = HttpXTransport(client=httpx.Client(transport=mock_transport))
        pipeline_client = PipelineClient(PLACEHOLDER_ENDPOINT, transport=transport, policies=[RetryPolicy()])
        method = "POST"
        headers = {"key": "value"}
        content = b"hello"
        request = HttpRequest(method=method, url=PLACEHOLDER_ENDPOINT, headers=headers, content=content)
        response = pipeline_client.send_request(request)
        expected = self.mock_successful_post()
        assert response.content == expected.content
        assert response.status_code == expected.status_code
        assert response.reason == expected.reason_phrase

    def test_exception(self) -> None:
        mock_transport = httpx.MockTransport(self.mock_exception)
        transport = HttpXTransport(client=httpx.Client(transport=mock_transport))
        pipeline_client = PipelineClient(PLACEHOLDER_ENDPOINT, transport=transport, policies=[RetryPolicy()])
        request = HttpRequest(method="GET", url=PLACEHOLDER_ENDPOINT)
        with pytest.raises(ServiceRequestError) as ex:
            pipeline_client.send_request(request)
            assert ex.value == "connection timed out"

    def test_iter_raw(self, port):
        client = PipelineClient(PLACEHOLDER_ENDPOINT, transport=HttpXTransport())
        request = HttpRequest("GET", url="http://localhost:{}/streams/basic".format(port))
        with client.send_request(request, stream=True) as response:
            raw = b""
            for part in response.iter_raw():
                # assert not response._internal_response._content_consumed
                assert not response.is_closed
                assert response.is_stream_consumed  # we follow httpx behavior here
                raw += part
            assert raw == b"Hello, world!"
        # assert response._internal_response._content_consumed
        assert response.is_closed
        assert response.is_stream_consumed
