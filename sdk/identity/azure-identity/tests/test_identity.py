# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os
import time
import uuid

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    ChainedTokenCredential,
)
from azure.identity._managed_identity import ImdsCredential
from azure.identity.constants import EnvironmentVariables

from helpers import mock_response, Request, validating_transport


def test_client_secret_credential_cache():
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
    scope = "scope"

    credential = ClientSecretCredential("client_id", "secret", tenant_id="some-guid", transport=Mock(send=mock_send))

    # get_token initially returns the expired token because the credential
    # doesn't check whether tokens it receives from the service have expired
    token = credential.get_token(scope)
    assert token == expired_token

    access_token = "new token"
    token_payload["access_token"] = access_token
    token_payload["expires_on"] = now + 3600
    valid_token = AccessToken(access_token, now + 3600)

    # second call should observe the cached token has expired, and request another
    token = credential.get_token(scope)
    assert token == valid_token
    assert mock_send.call_count == 2


def test_client_secret_credential():
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = validating_transport(
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

    token = ClientSecretCredential(
        client_id=client_id, secret=secret, tenant_id=tenant_id, transport=transport
    ).get_token("scope")

    # not validating expires_on because doing so requires monkeypatching time, and this is tested elsewhere
    assert token.token == access_token


def test_client_secret_environment_credential(monkeypatch):
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = validating_transport(
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

    monkeypatch.setenv(EnvironmentVariables.AZURE_CLIENT_ID, client_id)
    monkeypatch.setenv(EnvironmentVariables.AZURE_CLIENT_SECRET, secret)
    monkeypatch.setenv(EnvironmentVariables.AZURE_TENANT_ID, tenant_id)

    token = EnvironmentCredential(transport=transport).get_token("scope")

    # not validating expires_on because doing so requires monkeypatching time, and this is tested elsewhere
    assert token.token == access_token


def test_environment_credential_error():
    with pytest.raises(ClientAuthenticationError):
        EnvironmentCredential().get_token("scope")


def test_credential_chain_error_message():
    def raise_authn_error(message):
        raise ClientAuthenticationError(message)

    first_error = "first_error"
    first_credential = Mock(spec=ClientSecretCredential, get_token=lambda _: raise_authn_error(first_error))
    second_error = "second_error"
    second_credential = Mock(name="second_credential", get_token=lambda _: raise_authn_error(second_error))

    with pytest.raises(ClientAuthenticationError) as ex:
        ChainedTokenCredential(first_credential, second_credential).get_token("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


def test_chain_attempts_all_credentials():
    def raise_authn_error(message="it didn't work"):
        raise ClientAuthenticationError(message)

    expected_token = AccessToken("expected_token", 0)

    credentials = [
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(return_value=expected_token)),
    ]

    token = ChainedTokenCredential(*credentials).get_token("scope")
    assert token is expected_token

    for credential in credentials:
        assert credential.get_token.call_count == 1


def test_chain_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=lambda _: expected_token)
    second_credential = Mock(get_token=Mock())

    aggregate = ChainedTokenCredential(first_credential, second_credential)
    credential = aggregate.get_token("scope")

    assert credential is expected_token
    assert second_credential.get_token.call_count == 0


def test_imds_credential_cache():
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

    credential = ImdsCredential(transport=Mock(send=mock_send))
    token = credential.get_token(scope)
    assert token.token == expired
    assert mock_send.call_count == 2  # first request was probing for endpoint availability

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    token = credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3

    # get_token should return the cached token now
    token = credential.get_token(scope)
    assert token.token == good_for_an_hour
    assert mock_send.call_count == 3


def test_imds_credential_retries():
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
            ImdsCredential(transport=Mock(send=mock_send)).get_token("scope")
        except ClientAuthenticationError:
            pass
        # first call was availability probe, second the original request;
        # credential should have then exhausted retries for each of these status codes
        assert mock_send.call_count == 2 + total_retries


def test_default_credential():
    DefaultAzureCredential()
