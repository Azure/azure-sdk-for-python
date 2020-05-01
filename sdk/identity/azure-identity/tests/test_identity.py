# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import json
import time

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    ChainedTokenCredential,
    ClientSecretCredential,
    CredentialUnavailableError,
    DefaultAzureCredential,
    EnvironmentCredential,
)
from azure.identity._credentials.managed_identity import ImdsCredential
from azure.identity._constants import EnvironmentVariables, KnownAuthorities
from azure.identity._internal import get_default_authority, normalize_authority
import pytest

from helpers import mock_response, Request, validating_transport


def test_get_default_authority():
    """get_default_authority should return public cloud or the value of $AZURE_AUTHORITY_HOST, with 'https' scheme"""

    # default scheme is https
    for authority in ("localhost", "https://localhost"):
        with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
            assert get_default_authority() == "https://localhost"

    # default to public cloud
    for environ in ({}, {EnvironmentVariables.AZURE_AUTHORITY_HOST: KnownAuthorities.AZURE_PUBLIC_CLOUD}):
        with patch.dict("os.environ", environ, clear=True):
            assert get_default_authority() == "https://" + KnownAuthorities.AZURE_PUBLIC_CLOUD

    # require https
    with pytest.raises(ValueError):
        with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: "http://localhost"}, clear=True):
            get_default_authority()


def test_normalize_authority():
    """normalize_authority should return a URI with a scheme and no trailing spaces or forward slashes"""

    localhost = "localhost"
    localhost_tls = "https://" + localhost

    # accept https if specified, default to it when no scheme specified
    for uri in (localhost, localhost_tls):
        assert normalize_authority(uri) == localhost_tls

        # remove trailing characters
        for string in ("/", " ", "/ ", " /"):
            assert normalize_authority(uri + string) == localhost_tls

    # raise for other schemes
    for scheme in ("http", "file"):
        with pytest.raises(ValueError):
            normalize_authority(scheme + "://localhost")


def test_client_secret_environment_credential():
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

    environment = {
        EnvironmentVariables.AZURE_CLIENT_ID: client_id,
        EnvironmentVariables.AZURE_CLIENT_SECRET: secret,
        EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
    }
    with patch("os.environ", environment):
        token = EnvironmentCredential(transport=transport).get_token("scope")

    # not validating expires_on because doing so requires monkeypatching time, and this is tested elsewhere
    assert token.token == access_token


def test_credential_chain_error_message():
    first_error = "first_error"
    first_credential = Mock(
        spec=ClientSecretCredential, get_token=Mock(side_effect=CredentialUnavailableError(first_error))
    )
    second_error = "second_error"
    second_credential = Mock(
        name="second_credential", get_token=Mock(side_effect=ClientAuthenticationError(second_error))
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        ChainedTokenCredential(first_credential, second_credential).get_token("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


def test_chain_attempts_all_credentials():
    expected_token = AccessToken("expected_token", 0)

    credentials = [
        Mock(get_token=Mock(side_effect=CredentialUnavailableError(message=""))),
        Mock(get_token=Mock(side_effect=CredentialUnavailableError(message=""))),
        Mock(get_token=Mock(return_value=expected_token)),
    ]

    token = ChainedTokenCredential(*credentials).get_token("scope")
    assert token is expected_token

    for credential in credentials:
        assert credential.get_token.call_count == 1


def test_chain_raises_for_unexpected_error():
    """the chain should not continue after an unexpected error (i.e. anything but CredentialUnavailableError)"""

    expected_message = "it can't be done"

    credentials = [
        Mock(get_token=Mock(side_effect=CredentialUnavailableError(message=""))),
        Mock(get_token=Mock(side_effect=ValueError(expected_message))),
        Mock(get_token=Mock(return_value=AccessToken("**", 42))),
    ]

    with pytest.raises(ClientAuthenticationError) as ex:
        ChainedTokenCredential(*credentials).get_token("scope")

    assert expected_message in ex.value.message
    assert credentials[-1].get_token.call_count == 0


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
        text=lambda encoding=None: json.dumps(token_payload),
        headers={"content-type": "application/json"},
        status_code=200,
        content_type="application/json",
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
        text=lambda encoding=None: b"{}",
        headers={"content-type": "application/json", "Retry-After": "0"},
        content_type="application/json",
    )
    mock_send = Mock(return_value=mock_response)

    total_retries = ImdsCredential._create_config().retry_policy.total_retries

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


@patch("azure.identity._credentials.default.SharedTokenCacheCredential")
def test_default_credential_shared_cache_use(mock_credential):
    mock_credential.supported = Mock(return_value=False)

    # unsupported platform -> default credential shouldn't use shared cache
    credential = DefaultAzureCredential()
    assert mock_credential.call_count == 0
    assert mock_credential.supported.call_count == 1
    mock_credential.supported.reset_mock()

    mock_credential.supported = Mock(return_value=True)

    # supported platform -> default credential should use shared cache
    credential = DefaultAzureCredential()
    assert mock_credential.call_count == 1
    assert mock_credential.supported.call_count == 1
    mock_credential.supported.reset_mock()
