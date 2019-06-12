# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import json
import os
import time
from unittest.mock import Mock
import uuid

import pytest
from azure.identity import (
    AuthenticationError,
    AsyncClientSecretCredential,
    AsyncDefaultAzureCredential,
    AsyncEnvironmentCredential,
    AsyncTokenCredentialChain,
)
from azure.identity.aio._internal import AsyncImdsCredential, AsyncMsiCredential
from azure.identity.constants import EnvironmentVariables, MSI_ENDPOINT, MSI_SECRET


@pytest.mark.asyncio
async def test_client_secret_credential_cache():
    expired = "this token's expired"
    now = time.time()
    token_payload = {
        "access_token": expired,
        "expires_in": 0,
        "ext_expires_in": 0,
        "expires_on": now - 300,  # expired 5 minutes ago
        "not_before": now,
        "token_type": "Bearer",
        "resource": str(uuid.uuid1()),
    }

    mock_response = Mock(
        text=lambda: json.dumps(token_payload),
        headers={"content-type": "application/json"},
        status_code=200,
        content_type=["application/json"],
    )
    mock_send = Mock(return_value=mock_response)

    credential = AsyncClientSecretCredential(
        "client_id", "secret", tenant_id=str(uuid.uuid1()), transport=Mock(send=asyncio.coroutine(mock_send))
    )
    scopes = ("https://foo.bar/.default", "https://bar.qux/.default")
    token = await credential.get_token(*scopes)
    assert token == expired

    token = await credential.get_token(*scopes)
    assert token == expired
    assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_cert_environment_credential(monkeypatch):
    client_id = "fake-client-id"
    pem_path = os.path.join(os.path.dirname(__file__), "private-key.pem")
    tenant_id = "fake-tenant-id"

    monkeypatch.setenv(EnvironmentVariables.AZURE_CLIENT_ID, client_id)
    monkeypatch.setenv(EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH, pem_path)
    monkeypatch.setenv(EnvironmentVariables.AZURE_TENANT_ID, tenant_id)

    success_message = "request passed validation"

    def validate_request(request, **kwargs):
        assert tenant_id in request.url
        assert request.data["client_id"] == client_id
        assert request.data["grant_type"] == "client_credentials"
        # raising here makes mocking a transport response unnecessary
        raise AuthenticationError(success_message)

    credential = AsyncEnvironmentCredential(transport=Mock(send=validate_request))
    with pytest.raises(AuthenticationError) as ex:
        await credential.get_token("scope")
    assert str(ex.value) == success_message


@pytest.mark.asyncio
async def test_client_secret_environment_credential(monkeypatch):
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"

    monkeypatch.setenv(EnvironmentVariables.AZURE_CLIENT_ID, client_id)
    monkeypatch.setenv(EnvironmentVariables.AZURE_CLIENT_SECRET, secret)
    monkeypatch.setenv(EnvironmentVariables.AZURE_TENANT_ID, tenant_id)

    success_message = "request passed validation"

    def validate_request(request, **kwargs):
        assert tenant_id in request.url
        assert request.data["client_id"] == client_id
        assert request.data["client_secret"] == secret
        # raising here makes mocking a transport response unnecessary
        raise AuthenticationError(success_message)

    credential = AsyncEnvironmentCredential(transport=Mock(send=validate_request))
    with pytest.raises(AuthenticationError) as ex:
        await credential.get_token("scope")
    assert str(ex.value) == success_message


@pytest.mark.asyncio
async def test_environment_credential_error():
    with pytest.raises(AuthenticationError):
        await AsyncEnvironmentCredential().get_token("scope")


@pytest.mark.asyncio
async def test_credential_chain_error_message():
    def raise_authn_error(message):
        raise AuthenticationError(message)

    first_error = "first_error"
    first_credential = Mock(spec=AsyncClientSecretCredential, get_token=lambda _: raise_authn_error(first_error))
    second_error = "second_error"
    second_credential = Mock(name="second_credential", get_token=lambda _: raise_authn_error(second_error))

    with pytest.raises(AuthenticationError) as ex:
        await AsyncTokenCredentialChain(first_credential, second_credential).get_token("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


@pytest.mark.asyncio
async def test_chain_attempts_all_credentials():
    async def raise_authn_error(message="it didn't work"):
        raise AuthenticationError(message)

    expected_token = "expected_token"
    credentials = [
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=asyncio.coroutine(lambda _: expected_token)),
    ]

    token = await AsyncTokenCredentialChain(*credentials).get_token("scope")
    assert token is expected_token

    for credential in credentials[:-1]:
        assert credential.get_token.call_count == 1


@pytest.mark.asyncio
async def test_chain_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=asyncio.coroutine(lambda _: expected_token))
    second_credential = Mock(get_token=Mock())

    aggregate = AsyncTokenCredentialChain(first_credential, second_credential)
    credential = await aggregate.get_token("scope")

    assert credential is expected_token
    assert second_credential.get_token.call_count == 0


@pytest.mark.asyncio
async def test_imds_credential_cache():
    scope = "https://foo.bar"
    expired = "this token's expired"
    now = int(time.time())
    token_payload = {
        "access_token": expired,
        "refresh_token": "",
        "expires_in": 0,
        "expires_on": now - 300,  # expired 5 minutes ago
        "not_before": now,
        "resource": scope,
        "token_type": "Bearer",
    }

    mock_response = Mock(
        text=lambda: json.dumps(token_payload),
        headers={"content-type": "application/json"},
        status_code=200,
        content_type=["application/json"],
    )
    mock_send = Mock(return_value=mock_response)

    credential = AsyncImdsCredential(transport=Mock(send=asyncio.coroutine(mock_send)))
    token = await credential.get_token(scope)
    assert token == expired
    assert mock_send.call_count == 1

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    token = await credential.get_token(scope)
    assert token == good_for_an_hour
    assert mock_send.call_count == 2

    # get_token should return the cached token now
    token = await credential.get_token(scope)
    assert token == good_for_an_hour
    assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_imds_credential_retries():
    mock_response = Mock(
        text=lambda: b"",
        headers={"content-type": "application/json", "Retry-After": "0"},
        status_code=200,
        content_type=["application/json"],
    )
    mock_send = Mock(return_value=mock_response)

    retry_total = 1
    credential = AsyncImdsCredential(retry_total=retry_total, transport=Mock(send=asyncio.coroutine(mock_send)))

    for status_code in (404, 429, 500):
        mock_response.status_code = status_code
        try:
            await credential.get_token("scope")
        except AuthenticationError:
            pass
        assert mock_send.call_count is 1 + retry_total
        mock_send.reset_mock()


@pytest.mark.asyncio
async def test_msi_credential(monkeypatch):
    msi_secret = "secret"
    monkeypatch.setenv(MSI_SECRET, msi_secret)
    monkeypatch.setenv(MSI_ENDPOINT, "https://foo.bar")

    success_message = "test passed"

    async def validate_request(req, *args, **kwargs):
        assert req.url.startswith(os.environ[MSI_ENDPOINT])
        assert req.headers["secret"] == msi_secret
        exception = Exception()
        exception.message = success_message
        raise exception

    with pytest.raises(Exception) as ex:
        await AsyncMsiCredential(transport=Mock(send=validate_request)).get_token("https://scope")
    assert ex.value.message is success_message


def test_default_credential():
    AsyncDefaultAzureCredential()
