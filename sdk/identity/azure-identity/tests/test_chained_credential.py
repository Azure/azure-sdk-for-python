# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, MagicMock, patch

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity._credentials.imds import IMDS_TOKEN_PATH, IMDS_AUTHORITY
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity import (
    ChainedTokenCredential,
    ClientSecretCredential,
    ManagedIdentityCredential,
    CredentialUnavailableError,
)
import pytest

from helpers import validating_transport, Request, mock_response


def test_close():
    credentials = [MagicMock(close=Mock()) for _ in range(5)]
    chain = ChainedTokenCredential(*credentials)

    for credential in credentials:
        assert credential.__exit__.call_count == 0

    chain.close()

    for credential in credentials:
        assert credential.__exit__.call_count == 1


def test_context_manager():
    credentials = [MagicMock() for _ in range(5)]
    chain = ChainedTokenCredential(*credentials)

    for credential in credentials:
        assert credential.__enter__.call_count == 0
        assert credential.__exit__.call_count == 0

    with chain:
        for credential in credentials:
            assert credential.__enter__.call_count == 1
            assert credential.__exit__.call_count == 0

    for credential in credentials:
        assert credential.__enter__.call_count == 1
        assert credential.__exit__.call_count == 1


def test_error_message():
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


def test_attempts_all_credentials():
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


def test_raises_for_unexpected_error():
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


def test_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=lambda _, **__: expected_token)
    second_credential = Mock(get_token=Mock())

    aggregate = ChainedTokenCredential(first_credential, second_credential)
    credential = aggregate.get_token("scope")

    assert credential is expected_token
    assert second_credential.get_token.call_count == 0


def test_managed_identity_imds_probe():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    transport = validating_transport(
        requests=[
            Request(base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH),
            Request(
                base_url=IMDS_AUTHORITY + IMDS_TOKEN_PATH,
                method="GET",
                required_headers={"Metadata": "true", "User-Agent": USER_AGENT},
                required_params={"api-version": "2018-02-01", "resource": scope},
            ),
        ],
        responses=[
            # probe receives error response
            mock_response(status_code=400, json_payload={"error": "this is an error message"}),
            mock_response(
                json_payload={
                    "access_token": access_token,
                    "expires_in": 42,
                    "expires_on": expires_on,
                    "ext_expires_in": 42,
                    "not_before": int(time.time()),
                    "resource": scope,
                    "token_type": "Bearer",
                }
            ),
        ],
    )

    with patch.dict("os.environ", clear=True):
        credentials = [
            Mock(get_token=Mock(side_effect=CredentialUnavailableError(message=""))),
            ManagedIdentityCredential(transport=transport),
        ]
        token = ChainedTokenCredential(*credentials).get_token(scope)
    assert token == expected_token


def test_managed_identity_failed_probe():
    mock_send = Mock(side_effect=Exception("timeout"))
    transport = Mock(send=mock_send)
    expected_token = Mock()

    credentials = [
        Mock(get_token=Mock(side_effect=CredentialUnavailableError(message=""))),
        ManagedIdentityCredential(transport=transport),
        Mock(get_token=Mock(return_value=expected_token)),
    ]

    with patch.dict("os.environ", clear=True):
        token = ChainedTokenCredential(*credentials).get_token("scope")

    assert token is expected_token
    # ManagedIdentityCredential should be tried and skipped with the last credential in the chain
    # being used.
    assert credentials[-1].get_token.call_count == 1
