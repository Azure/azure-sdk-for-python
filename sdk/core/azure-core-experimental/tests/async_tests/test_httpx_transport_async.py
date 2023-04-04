from typing import Optional

import httpx
import pytest

from azure.core.exceptions import ServiceRequestError
from azure.core.experimental.transport import AsyncHttpXTransport
from azure.core.pipeline._base_async import AsyncPipeline
from azure.core.pipeline.policies._retry_async import AsyncRetryPolicy
from azure.core.rest import HttpRequest

PLACEHOLDER_ENDPOINT = "https://my-resource-group.cognitiveservices.azure.com/"


class TestAsyncHttpXTransport:
    def mock_successful_post(self, request: Optional[httpx.Request] = None) -> httpx.Response:
        return httpx.Response(200, content=b"Hello, world!")

    def mock_exception(self, request: Optional[httpx.Request] = None) -> None:
        raise httpx.TimeoutException(message="connection timed out")

    @pytest.mark.asyncio
    async def test_send_success(self) -> None:
        mock_transport = httpx.MockTransport(self.mock_successful_post)
        transport = AsyncHttpXTransport(client=httpx.AsyncClient(transport=mock_transport))
        pipeline = AsyncPipeline(transport, [AsyncRetryPolicy()])
        method = "POST"
        headers = {"key": "value"}
        content = b"hello"
        request = HttpRequest(method=method, url=PLACEHOLDER_ENDPOINT, headers=headers, content=content)
        response = (await pipeline.run(request=request)).http_response
        expected = self.mock_successful_post()
        assert response.body() == expected.content
        assert response.status_code == expected.status_code
        assert response.reason == expected.reason_phrase

    @pytest.mark.asyncio
    async def test_exception(self) -> None:
        mock_transport = httpx.MockTransport(self.mock_exception)
        transport = AsyncHttpXTransport(client=httpx.Client(transport=mock_transport))
        pipeline = AsyncPipeline(transport, [AsyncRetryPolicy()])
        request = HttpRequest(method="GET", url=PLACEHOLDER_ENDPOINT)
        with pytest.raises(ServiceRequestError) as ex:
            await pipeline.run(request=request)
            assert ex.value == "connection timed out"
