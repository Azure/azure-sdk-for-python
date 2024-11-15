# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, MagicMock, patch

from azure.core.credentials import AccessToken, AccessTokenInfo
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

from helpers import validating_transport, Request, mock_response, GET_TOKEN_METHODS


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


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_error_message(get_token_method):
    first_error = "first_error"
    first_credential = Mock(
        spec=ClientSecretCredential,
        get_token=Mock(side_effect=CredentialUnavailableError(first_error)),
        get_token_info=Mock(side_effect=CredentialUnavailableError(first_error)),
    )
    second_error = "second_error"
    second_credential = Mock(
        name="second_credential",
        get_token=Mock(side_effect=ClientAuthenticationError(second_error)),
        get_token_info=Mock(side_effect=ClientAuthenticationError(second_error)),
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        chained_cred = ChainedTokenCredential(first_credential, second_credential)
        getattr(chained_cred, get_token_method)("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_attempts_all_credentials(get_token_method):
    expected_token = "expected_token"
    expires_on = 42

    credentials = [
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=CredentialUnavailableError(message="")),
            get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=CredentialUnavailableError(message="")),
            get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(return_value=AccessToken(expected_token, expires_on)),
            get_token_info=Mock(return_value=AccessTokenInfo(expected_token, expires_on)),
        ),
    ]

    token = getattr(ChainedTokenCredential(*credentials), get_token_method)("scope")
    assert token.token == expected_token

    for credential in credentials:
        assert getattr(credential, get_token_method).call_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_raises_for_unexpected_error(get_token_method):
    """the chain should not continue after an unexpected error (i.e. anything but CredentialUnavailableError)"""

    expected_message = "it can't be done"

    credentials = [
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=CredentialUnavailableError(message="")),
            get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=ValueError(expected_message)),
            get_token_info=Mock(side_effect=ValueError(expected_message)),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(return_value=AccessToken("**", 42)),
            get_token_info=Mock(return_value=AccessTokenInfo("**", 42)),
        ),
    ]

    with pytest.raises(ClientAuthenticationError) as ex:
        getattr(ChainedTokenCredential(*credentials), get_token_method)("scope")

    assert expected_message in ex.value.message
    assert getattr(credentials[-1], get_token_method).call_count == 0


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_returns_first_token(get_token_method):
    expected_token = Mock()
    first_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=lambda _, **__: expected_token,
        get_token_info=lambda _, **__: expected_token,
    )
    second_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(),
        get_token_info=Mock(),
    )

    aggregate = ChainedTokenCredential(first_credential, second_credential)
    token = getattr(aggregate, get_token_method)("scope")

    assert token.token == expected_token.token
    assert getattr(second_credential, get_token_method).call_count == 0


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_managed_identity_imds_probe(get_token_method):
    expected_token = "****"
    expires_on = 42
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
                    "access_token": expected_token,
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
            Mock(
                spec_set=["get_token", "get_token_info"],
                get_token=Mock(side_effect=CredentialUnavailableError(message="")),
                get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
            ),
            ManagedIdentityCredential(transport=transport),
        ]
        token = getattr(ChainedTokenCredential(*credentials), get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_managed_identity_failed_probe(get_token_method):
    mock_send = Mock(side_effect=Exception("timeout"))
    transport = Mock(send=mock_send)
    expected_token = Mock()

    credentials = [
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=CredentialUnavailableError(message="")),
            get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
        ),
        ManagedIdentityCredential(transport=transport),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(return_value=expected_token),
            get_token_info=Mock(return_value=expected_token),
        ),
    ]

    with patch.dict("os.environ", clear=True):
        token = getattr(ChainedTokenCredential(*credentials), get_token_method)("scope")

    assert token.token == expected_token.token
    # ManagedIdentityCredential should be tried and skipped with the last credential in the chain
    # being used.
    assert getattr(credentials[-1], get_token_method).call_count == 1


def test_credentials_with_no_get_token_info():
    """ChainedTokenCredential should work with credentials that don't implement get_token_info."""

    access_token = "****"
    credential1 = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
    )
    credential2 = Mock(
        spec_set=["get_token"],
        get_token=Mock(return_value=AccessToken(access_token, 42)),
    )
    credential3 = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(return_value=AccessToken("foo", 42)),
        get_token_info=Mock(return_value=AccessTokenInfo("bar", 42)),
    )
    chain = ChainedTokenCredential(credential1, credential2, credential3)  # type: ignore
    token_info = chain.get_token_info("scope")
    assert token_info.token == access_token


def test_credentials_with_no_get_token():
    """ChainedTokenCredential should work with credentials that only implement get_token_info."""

    access_token = "****"
    credential1 = Mock(
        spec_set=["get_token"],
        get_token=Mock(side_effect=CredentialUnavailableError(message="")),
    )
    credential2 = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(return_value=AccessTokenInfo(access_token, 42)),
    )
    credential3 = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(return_value=AccessToken("foo", 42)),
        get_token_info=Mock(return_value=AccessTokenInfo("bar", 42)),
    )
    chain = ChainedTokenCredential(credential1, credential2, credential3)  # type: ignore
    token_info = chain.get_token("scope")
    assert token_info.token == access_token


def test_credentials_with_pop_option():
    """ChainedTokenCredential should skip credentials that don't support get_token_info and the pop option is set."""

    access_token = "****"
    credential1 = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
    )
    credential2 = Mock(
        spec_set=["get_token"],
        get_token=Mock(return_value=AccessToken("foo", 42)),
    )
    credential3 = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(return_value=AccessToken("bar", 42)),
        get_token_info=Mock(return_value=AccessTokenInfo(access_token, 42)),
    )
    chain = ChainedTokenCredential(credential1, credential2, credential3)  # type: ignore
    token_info = chain.get_token_info("scope", options={"pop": True})  # type: ignore
    assert token_info.token == access_token
