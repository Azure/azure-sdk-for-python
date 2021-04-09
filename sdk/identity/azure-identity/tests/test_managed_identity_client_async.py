# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import patch

from azure.core.pipeline.transport import HttpRequest
from azure.identity.aio._internal.managed_identity_client import AsyncManagedIdentityClient
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport


@pytest.mark.asyncio
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
