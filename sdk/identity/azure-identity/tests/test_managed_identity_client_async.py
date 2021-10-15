# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import time
from unittest.mock import Mock, patch

from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError
from azure.core.pipeline.transport import HttpRequest
from azure.identity.aio._internal.managed_identity_client import AsyncManagedIdentityClient
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, get_completed_future

pytestmark = pytest.mark.asyncio


async def test_close():
    transport = AsyncMockTransport()
    client = AsyncManagedIdentityClient(lambda *_: None, transport=transport)

    await client.close()

    assert transport.__aexit__.call_count == 1


async def test_context_manager():
    transport = AsyncMockTransport()
    client = AsyncManagedIdentityClient(lambda *_: None, transport=transport)

    async with client:
        assert transport.__aenter__.call_count == 1
        assert transport.__aexit__.call_count == 0

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


async def test_caching():
    scope = "scope"
    now = int(time.time())
    expected_expires_on = now + 3600
    expected_token = "*"
    transport = async_validating_transport(
        requests=[Request(url="http://localhost")],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 3600,
                    "expires_on": expected_expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )
    client = AsyncManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=transport
    )

    token = client.get_cached_token(scope)
    assert not token

    with patch(AsyncManagedIdentityClient.__module__ + ".time.time", lambda: now):
        token = await client.request_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token

    token = client.get_cached_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token


async def test_deserializes_json_from_text():
    """The client should gracefully handle a response with a JSON body and content-type text/plain"""

    scope = "scope"
    now = int(time.time())
    expected_expires_on = now + 3600
    expected_token = "*"

    async def send(request, **_):
        body = json.dumps(
            {
                "access_token": expected_token,
                "expires_in": 3600,
                "expires_on": expected_expires_on,
                "resource": scope,
                "token_type": "Bearer",
            }
        )
        return Mock(
            status_code=200,
            headers={"Content-Type": "text/plain"},
            content_type="text/plain",
            text=lambda encoding=None: body,
        )

    client = AsyncManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=Mock(send=send)
    )

    token = await client.request_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_managed_identity_client_retry():
    """AsyncManagedIdentityClient should retry token requests"""

    message = "can't connect"
    transport = Mock(send=Mock(side_effect=ServiceRequestError(message)), sleep=get_completed_future)
    request_factory = Mock()

    client = AsyncManagedIdentityClient(request_factory, transport=transport)

    for method in ("GET", "POST"):
        request_factory.return_value = HttpRequest(method, "https://localhost")
        with pytest.raises(ServiceRequestError, match=message):
            await client.request_token("scope")
        assert transport.send.call_count > 1
        transport.send.reset_mock()


@pytest.mark.parametrize("content_type", ("text/html", "application/json"))
async def test_unexpected_content(content_type):
    content = "<html><body>not JSON</body></html>"

    async def send(request, **_):
        return Mock(
            status_code=200,
            headers={"Content-Type": content_type},
            content_type=content_type,
            text=lambda encoding=None: content,
        )

    client = AsyncManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=Mock(send=send)
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        await client.request_token("scope")
    assert ex.value.response.text() == content

    if "json" not in content_type:
        assert content_type in ex.value.message
