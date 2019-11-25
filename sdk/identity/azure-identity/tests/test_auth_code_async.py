# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio import AuthorizationCodeCredential
import pytest


@pytest.mark.asyncio
async def test_auth_code_credential():
    client_id = "client id"
    tenant_id = "tenant"
    expected_code = "auth code"
    redirect_uri = "https://foo.bar"
    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    obtain_by_auth_code = Mock(return_value=expected_token)
    mock_client.obtain_token_by_authorization_code = asyncio.coroutine(obtain_by_auth_code)

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
    mock_client.obtain_token_by_refresh_token = asyncio.coroutine(lambda *_, **__: expected_token)
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
