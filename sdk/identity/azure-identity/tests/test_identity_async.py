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
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio import (
    ChainedTokenCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
)
from azure.identity.aio._internal import ImdsCredential
from azure.identity.constants import EnvironmentVariables


@pytest.mark.asyncio
async def test_client_secret_credential_cache():
    expired = "this token's expired"
    now = time.time()
    expired_on = int(now - 300)
    expired_token = AccessToken(expired, expired_on)
    token_payload = {
        "access_token": expired,
        "expires_in": 0,
        "ext_expires_in": 0,
        "expires_on": expired_on,
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

    credential = ClientSecretCredential(
        "client_id", "secret", tenant_id=str(uuid.uuid1()), transport=Mock(send=asyncio.coroutine(mock_send))
    )
    scopes = ("https://foo.bar/.default", "https://bar.qux/.default")
    token = await credential.get_token(*scopes)
    assert token == expired_token

    token = await credential.get_token(*scopes)
    assert token == expired_token
    assert mock_send.call_count == 2


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
        raise ClientAuthenticationError(success_message)

    credential = EnvironmentCredential(transport=Mock(send=validate_request))
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    assert str(ex.value) == success_message


@pytest.mark.asyncio
async def test_environment_credential_error():
    with pytest.raises(ClientAuthenticationError):
        await EnvironmentCredential().get_token("scope")


@pytest.mark.asyncio
async def test_credential_chain_error_message():
    def raise_authn_error(message):
        raise ClientAuthenticationError(message)

    first_error = "first_error"
    first_credential = Mock(spec=ClientSecretCredential, get_token=lambda _: raise_authn_error(first_error))
    second_error = "second_error"
    second_credential = Mock(name="second_credential", get_token=lambda _: raise_authn_error(second_error))

    with pytest.raises(ClientAuthenticationError) as ex:
        await ChainedTokenCredential(first_credential, second_credential).get_token("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


@pytest.mark.asyncio
async def test_chain_attempts_all_credentials():
    async def raise_authn_error(message="it didn't work"):
        raise ClientAuthenticationError(message)

    expected_token = AccessToken("expected_token", 0)
    credentials = [
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=asyncio.coroutine(lambda _: expected_token)),
    ]

    token = await ChainedTokenCredential(*credentials).get_token("scope")
    assert token is expected_token

    for credential in credentials[:-1]:
        assert credential.get_token.call_count == 1


@pytest.mark.asyncio
async def test_chain_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=asyncio.coroutine(lambda _: expected_token))
    second_credential = Mock(get_token=Mock())

    aggregate = ChainedTokenCredential(first_credential, second_credential)
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

    credential = ImdsCredential(transport=Mock(send=asyncio.coroutine(mock_send)))
    token = await credential.get_token(scope)
    assert token.token == expired
    assert mock_send.call_count == 2  # first request was probing for endpoint availability

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    token = await credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3

    # get_token should return the cached token now
    token = await credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3


@pytest.mark.asyncio
async def test_imds_credential_retries():
    mock_response = Mock(
        text=lambda: b"{}",
        headers={"content-type": "application/json", "Retry-After": "0"},
        content_type=["application/json"],
    )
    mock_send = Mock(return_value=mock_response)

    total_retries = ImdsCredential.create_config().retry_policy.total_retries

    for status_code in (404, 429, 500):
        mock_send.reset_mock()
        mock_response.status_code = status_code
        try:
            await ImdsCredential(
                transport=Mock(send=asyncio.coroutine(mock_send), sleep=asyncio.coroutine(lambda _: None))
            ).get_token("scope")
        except ClientAuthenticationError:
            pass
        # first call was availability probe, second the original request;
        # credential should have then exhausted retries for each of these status codes
        assert mock_send.call_count == 2 + total_retries


@pytest.mark.asyncio
async def test_managed_identity_app_service(monkeypatch):
    # in App Service, MSI_SECRET and MSI_ENDPOINT are set
    msi_secret = "secret"
    monkeypatch.setenv(EnvironmentVariables.MSI_SECRET, msi_secret)
    monkeypatch.setenv(EnvironmentVariables.MSI_ENDPOINT, "https://foo.bar")

    success_message = "test passed"

    async def validate_request(req, *args, **kwargs):
        assert req.url.startswith(os.environ[EnvironmentVariables.MSI_ENDPOINT])
        assert req.headers["secret"] == msi_secret
        exception = Exception()
        exception.message = success_message
        raise exception

    with pytest.raises(Exception) as ex:
        await ManagedIdentityCredential(transport=Mock(send=validate_request)).get_token("https://scope")
    assert ex.value.message is success_message


@pytest.mark.asyncio
async def test_managed_identity_cloud_shell(monkeypatch):
    # in Cloud Shell, only MSI_ENDPOINT is set
    msi_endpoint = "https://localhost:50432"
    monkeypatch.setenv(EnvironmentVariables.MSI_ENDPOINT, msi_endpoint)

    success_message = "test passed"

    async def validate_request(req, *args, **kwargs):
        assert req.headers["Metadata"] == "true"
        assert req.url.startswith(os.environ[EnvironmentVariables.MSI_ENDPOINT])
        exception = Exception()
        exception.message = success_message
        raise exception

    with pytest.raises(Exception) as ex:
        await ManagedIdentityCredential(transport=Mock(send=validate_request)).get_token("https://scope")
    assert ex.value.message is success_message


def test_default_credential():
    DefaultAzureCredential()
