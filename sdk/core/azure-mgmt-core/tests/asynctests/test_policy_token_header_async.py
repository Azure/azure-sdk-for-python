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
from unittest.mock import Mock
from typing import Any, cast, TYPE_CHECKING
from azure.core.exceptions import HttpResponseError
from azure.mgmt.core.policies._policy_token_header_async import (
    AsyncPolicyTokenHeaderPolicy,
)
from azure.core.pipeline.transport import HttpRequest

if TYPE_CHECKING:
    from azure.mgmt.core import AsyncARMPipelineClient

pytestmark = pytest.mark.asyncio


class MockAsyncARMPipelineClient:
    def __init__(self, response):
        self._response = response

    async def send_request(self, request, stream=False):
        return self._response


class MockHttpResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

    def text(self):
        return str(self._json_data)


async def test_async_policy_token_header_policy_adds_header():
    """Test that the async policy adds the correct header when policy token is acquired successfully."""

    # Mock client that returns a successful policy token response
    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    # Test with a subscription URL
    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    await policy.on_request(pipeline_request)

    # Verify the header was added
    assert request.headers["x-ms-policy-external-evaluations"] == "test-token-123"


async def test_async_policy_token_header_policy_no_subscription_id():
    """Test that the async policy raises an error when no subscription ID is found in the URL."""

    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    # Test with a URL without subscription ID
    request = HttpRequest("GET", "https://management.azure.com/providers/Microsoft.Resources")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    with pytest.raises(HttpResponseError, match="Failed to get subscriptionId from request url"):
        await policy.on_request(pipeline_request)


async def test_async_policy_token_header_policy_failed_response():
    """Test that the async policy raises an error when the policy token response fails."""

    # Mock client that returns a failed response
    mock_response = MockHttpResponse(500, {"error": "Internal server error"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    with pytest.raises(HttpResponseError, match="status code is not 200"):
        await policy.on_request(pipeline_request)


async def test_async_policy_token_header_policy_unsuccessful_result():
    """Test that the async policy raises an error when the policy token acquisition is unsuccessful."""

    # Mock client that returns an unsuccessful result
    mock_response = MockHttpResponse(200, {"result": "Failed", "error": "Token acquisition failed"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    with pytest.raises(HttpResponseError, match="Failed to acquire policy token"):
        await policy.on_request(pipeline_request)


async def test_async_policy_token_header_policy_disabled_by_default():
    """Test that the async policy does not acquire tokens when acquire_policy_token is False by default."""

    mock_response = MockHttpResponse(200, {"token": "test-token-123", "result": "Succeeded"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    # Policy without acquire_policy_token=True
    policy = AsyncPolicyTokenHeaderPolicy(mock_client)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    await policy.on_request(pipeline_request)

    # Verify no header was added
    assert "x-ms-policy-external-evaluations" not in request.headers


async def test_async_policy_token_header_policy_context_option_override():
    """Test that context options can override the async policy's acquire_policy_token setting."""

    mock_response = MockHttpResponse(200, {"token": "context-token-456", "result": "Succeeded"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    # Policy with acquire_policy_token=False
    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=False)

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {"acquire_policy_token": True}

    await policy.on_request(pipeline_request)

    # Verify the header was added despite the policy default being False
    assert request.headers["x-ms-policy-external-evaluations"] == "context-token-456"


async def test_async_policy_token_header_policy_with_content():
    """Test that the async policy handles request content properly when creating the policy request."""

    async def verify_policy_request(request, stream=False):
        # Verify the policy request contains the operation details including content
        import json

        body = json.loads(request.content)
        assert body["operation"]["uri"] == "https://management.azure.com/subscriptions/12345/resourceGroups/test"
        assert body["operation"]["method"] == "PUT"
        assert "content" in body["operation"]
        return MockHttpResponse(200, {"token": "content-token-789", "result": "Succeeded"})

    mock_client = cast("AsyncARMPipelineClient", Mock())
    mock_client.send_request = verify_policy_request

    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    request_content = '{"properties": {"location": "eastus"}}'
    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    request.content = request_content

    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    await policy.on_request(pipeline_request)

    # Verify the header was added
    assert request.headers["x-ms-policy-external-evaluations"] == "content-token-789"


async def test_async_policy_token_header_policy_send_method():
    """Test that the async policy's send method calls on_request and forwards to the next policy."""

    mock_response = MockHttpResponse(200, {"token": "send-token-999", "result": "Succeeded"})
    mock_client = cast("AsyncARMPipelineClient", MockAsyncARMPipelineClient(mock_response))

    policy = AsyncPolicyTokenHeaderPolicy(mock_client, acquire_policy_token=True)

    # Mock the next policy
    mock_next_policy = Mock()
    mock_pipeline_response = Mock()

    async def mock_send(request):
        return mock_pipeline_response

    mock_next_policy.send = Mock(wraps=mock_send)
    policy.next = mock_next_policy

    request = HttpRequest("PUT", "https://management.azure.com/subscriptions/12345/resourceGroups/test")
    pipeline_request = Mock()
    pipeline_request.http_request = request
    pipeline_request.context.options = {}

    # Call the send method
    response = await policy.send(pipeline_request)

    # Verify the header was added by on_request
    assert request.headers["x-ms-policy-external-evaluations"] == "send-token-999"

    # Verify the next policy was called
    mock_next_policy.send.assert_called_once_with(pipeline_request)

    # Verify the response is forwarded
    assert response == mock_pipeline_response
