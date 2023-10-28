from typing import Optional

import httpx
import pytest

from corehttp.exceptions import ServiceRequestError
from corehttp.transport.httpx import AsyncHttpXTransport
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.policies import AsyncRetryPolicy
from corehttp.rest import HttpRequest

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
        pipeline_client = AsyncPipelineClient(PLACEHOLDER_ENDPOINT, transport=transport, policies=[AsyncRetryPolicy()])
        method = "POST"
        headers = {"key": "value"}
        content = b"hello"
        request = HttpRequest(method=method, url=PLACEHOLDER_ENDPOINT, headers=headers, content=content)
        response = await pipeline_client.send_request(request)
        expected = self.mock_successful_post()
        assert response.content == expected.content
        assert response.status_code == expected.status_code
        assert response.reason == expected.reason_phrase

    @pytest.mark.asyncio
    async def test_exception(self) -> None:
        mock_transport = httpx.MockTransport(self.mock_exception)
        transport = AsyncHttpXTransport(client=httpx.AsyncClient(transport=mock_transport))
        pipeline_client = AsyncPipelineClient(PLACEHOLDER_ENDPOINT, transport=transport, policies=[AsyncRetryPolicy()])
        request = HttpRequest(method="GET", url=PLACEHOLDER_ENDPOINT)
        with pytest.raises(ServiceRequestError) as ex:
            await pipeline_client.send_request(request)
            assert ex.value == "connection timed out"

    @pytest.mark.asyncio
    async def test_compress_compressed_no_header(self,):
        # expect compressed text
        account_name = "coretests"
        account_url = "https://{}.blob.core.windows.net".format(account_name)
        url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
        client = AsyncPipelineClient(account_url, transport=AsyncHttpXTransport())
        async with client:
            request = HttpRequest("GET", url)
            pipeline_response = await client.pipeline.run(request, stream=True)
            response = pipeline_response.http_response
            data = response.iter_raw()
            content = b""
            async for d in data:
                content += d
            try:
                content.decode("utf-8")
                assert False
            except UnicodeDecodeError:
                pass
