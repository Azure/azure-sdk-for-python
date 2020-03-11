# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import AuthorizationCodeCredential
import pytest

from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future


@pytest.mark.asyncio
async def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", policies=[policy], transport=Mock(send=send)
    )

    await credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()
    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", transport=transport
    )

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()
    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", transport=transport
    )

    async with credential:
        assert transport.__aenter__.call_count == 1

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", transport=transport
    )

    await credential.get_token("scope")


@pytest.mark.asyncio
async def test_auth_code_credential():
    client_id = "client id"
    tenant_id = "tenant"
    expected_code = "auth code"
    redirect_uri = "https://foo.bar"
    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    obtain_by_auth_code = Mock(return_value=expected_token)
    mock_client.obtain_token_by_authorization_code = wrap_in_future(obtain_by_auth_code)

    credential = AuthorizationCodeCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        authorization_code=expected_code,
        redirect_uri=redirect_uri,
        client=mock_client,
    )

    # first call should redeem the auth code
    token = await credential.get_token("scope")
    assert token is expected_token
    assert obtain_by_auth_code.call_count == 1
    _, kwargs = obtain_by_auth_code.call_args
    assert kwargs["code"] == expected_code

    # no auth code -> credential should return cached token
    mock_client.obtain_token_by_authorization_code = None  # raise if credential calls this again
    mock_client.get_cached_access_token = lambda *_: expected_token
    token = await credential.get_token("scope")
    assert token is expected_token

    # no auth code, no cached token -> credential should use refresh token
    mock_client.get_cached_access_token = lambda *_: None
    mock_client.get_cached_refresh_tokens = lambda *_: ["this is a refresh token"]
    mock_client.obtain_token_by_refresh_token = wrap_in_future(lambda *_, **__: expected_token)
    token = await credential.get_token("scope")
    assert token is expected_token


@pytest.mark.asyncio
async def test_custom_executor_used():
    credential = AuthorizationCodeCredential(
        client_id="client id", tenant_id="tenant id", authorization_code="auth code", redirect_uri="https://foo.bar"
    )

    executor = Mock()

    with pytest.raises(ClientAuthenticationError):
        await credential.get_token("scope", executor=executor)

    assert executor.submit.call_count == 1


@pytest.mark.asyncio
async def test_custom_loop_used():
    credential = AuthorizationCodeCredential(
        client_id="client id", tenant_id="tenant id", authorization_code="auth code", redirect_uri="https://foo.bar"
    )

    loop = Mock()

    with pytest.raises(ClientAuthenticationError):
        await credential.get_token("scope", loop=loop)

    assert loop.run_in_executor.call_count == 1


@pytest.mark.asyncio
async def test_custom_loop_and_executor_used():
    credential = AuthorizationCodeCredential(
        client_id="client id", tenant_id="tenant id", authorization_code="auth code", redirect_uri="https://foo.bar"
    )

    executor = Mock()
    loop = Mock()

    with pytest.raises(ClientAuthenticationError):
        await credential.get_token("scope", executor=executor, loop=loop)

    assert loop.run_in_executor.call_count == 1
    executor_arg, _ = loop.run_in_executor.call_args[0]
    assert executor_arg is executor
