# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import time
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import ClientSecretCredential
from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future

import pytest


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()
    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()
    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    async with credential:
        assert transport.__aenter__.call_count == 1

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = ClientSecretCredential(
        "tenant-id", "client-id", "client-secret", policies=[ContentDecodePolicy(), policy], transport=Mock(send=send)
    )

    await credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = ClientSecretCredential("tenant-id", "client-id", "client-secret", transport=transport)

    await credential.get_token("scope")


@pytest.mark.asyncio
async def test_client_secret_credential():
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = async_validating_transport(
        requests=[Request(url_substring=tenant_id, required_data={"client_id": client_id, "client_secret": secret})],
        responses=[
            mock_response(
                json_payload={
                    "token_type": "Bearer",
                    "expires_in": 42,
                    "ext_expires_in": 42,
                    "access_token": access_token,
                }
            )
        ],
    )

    token = await ClientSecretCredential(
        tenant_id=tenant_id, client_id=client_id, client_secret=secret, transport=transport
    ).get_token("scope")

    # not validating expires_on because doing so requires monkeypatching time, and this is tested elsewhere
    assert token.token == access_token


@pytest.mark.asyncio
async def test_cache():
    expired = "this token's expired"
    now = int(time.time())
    expired_on = now - 3600
    expired_token = AccessToken(expired, expired_on)
    token_payload = {
        "access_token": expired,
        "expires_in": 0,
        "ext_expires_in": 0,
        "expires_on": expired_on,
        "not_before": now,
        "token_type": "Bearer",
    }
    mock_send = Mock(return_value=mock_response(json_payload=token_payload))
    transport = Mock(send=wrap_in_future(mock_send))
    scope = "scope"

    credential = ClientSecretCredential("tenant-id", "client-id", "secret", transport=transport)

    # get_token initially returns the expired token because the credential
    # doesn't check whether tokens it receives from the service have expired
    token = await credential.get_token(scope)
    assert token == expired_token

    access_token = "new token"
    token_payload["access_token"] = access_token
    token_payload["expires_on"] = now + 3600
    valid_token = AccessToken(access_token, now + 3600)

    # second call should observe the cached token has expired, and request another
    token = await credential.get_token(scope)
    assert token == valid_token
    assert mock_send.call_count == 2
