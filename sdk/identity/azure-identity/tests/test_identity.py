# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import os
import time
import uuid

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

import pytest
import requests
from azure.identity import (
    AuthenticationError,
    ClientSecretCredential,
    EnvironmentCredential,
    TokenCredentialChain,
    ManagedIdentityCredential,
    CertificateCredential,
)
from azure.identity.constants import EnvironmentVariables


def test_client_secret_credential_cache(monkeypatch):
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

    # monkeypatch requests so we can test pipeline configuration
    mock_response = Mock(text=json.dumps(token_payload), headers={"content-type": "application/json"}, status_code=200)
    mock_send = Mock(return_value=mock_response)
    monkeypatch.setattr(requests.Session, "send", value=mock_send)

    credential = ClientSecretCredential("client_id", "secret", tenant_id=str(uuid.uuid1()))
    scopes = ("https://foo.bar/.default", "https://bar.qux/.default")
    token = credential.get_token(scopes)
    assert token == expired

    token = credential.get_token(scopes)
    assert token == expired
    assert mock_send.call_count == 2


def test_client_secret_environment_credential(monkeypatch):
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

    credential = EnvironmentCredential(transport=Mock(send=validate_request))
    with pytest.raises(AuthenticationError) as ex:
        credential.get_token(("",))
    assert str(ex.value) == success_message


def test_cert_environment_credential(monkeypatch):
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

    credential = EnvironmentCredential(transport=Mock(send=validate_request))
    with pytest.raises(AuthenticationError) as ex:
        credential.get_token(("",))
    assert str(ex.value) == success_message


def test_environment_credential_error():
    with pytest.raises(AuthenticationError):
        EnvironmentCredential().get_token(("",))


def test_credential_chain_error_message():
    def raise_authn_error(message):
        raise AuthenticationError(message)

    first_error = "first_error"
    first_credential = Mock(spec=ClientSecretCredential, get_token=lambda _: raise_authn_error(first_error))
    second_error = "second_error"
    second_credential = Mock(name="second_credential", get_token=lambda _: raise_authn_error(second_error))

    with pytest.raises(AuthenticationError) as ex:
        TokenCredentialChain([first_credential, second_credential]).get_token(("scope",))

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


def test_chain_attempts_all_credentials():
    def raise_authn_error(message="it didn't work"):
        raise AuthenticationError(message)

    credentials = [
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(wraps=raise_authn_error)),
        Mock(get_token=Mock(return_value="token")),
    ]

    TokenCredentialChain(credentials).get_token(("scope",))

    for credential in credentials:
        assert credential.get_token.call_count == 1


def test_chain_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=lambda _: expected_token)
    second_credential = Mock(get_token=Mock())

    aggregate = TokenCredentialChain([first_credential, second_credential])
    credential = aggregate.get_token(("scope",))

    assert credential is expected_token
    assert second_credential.get_token.call_count == 0


def test_msi_credential_cache(monkeypatch):
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

    # monkeypatch requests so we can test pipeline configuration
    mock_response = Mock(text=json.dumps(token_payload), headers={"content-type": "application/json"}, status_code=200)
    mock_send = Mock(return_value=mock_response)
    monkeypatch.setattr(requests.Session, "send", value=mock_send)

    credential = ManagedIdentityCredential()
    token = credential.get_token((scope,))
    assert token == expired
    assert mock_send.call_count == 1

    # calling get_token again should provoke another HTTP request
    good_for_an_hour = "this token's good for an hour"
    token_payload["expires_on"] = int(time.time()) + 3600
    token_payload["expires_in"] = 3600
    token_payload["access_token"] = good_for_an_hour
    mock_response.text = json.dumps(token_payload)
    token = credential.get_token((scope,))
    assert token == good_for_an_hour
    assert mock_send.call_count == 2

    # get_token should return the cached token now
    token = credential.get_token((scope,))
    assert token == good_for_an_hour
    assert mock_send.call_count == 2


def test_msi_credential_retries(monkeypatch):
    # monkeypatch requests so we can test pipeline configuration
    mock_response = Mock(headers={"Retry-After": "0"}, text=b"")
    mock_send = Mock(return_value=mock_response)
    monkeypatch.setattr(requests.Session, "send", value=mock_send)

    retry_total = 1
    credential = ManagedIdentityCredential(retry_total=retry_total)

    for status_code in (404, 429, 500):
        mock_response.status_code = status_code
        try:
            credential.get_token(("",))
        except AuthenticationError:
            pass
        assert mock_send.call_count is 1 + retry_total
        mock_send.reset_mock()
