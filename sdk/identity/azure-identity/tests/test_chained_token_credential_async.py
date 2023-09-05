# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, patch

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError, ClientSecretCredential
from azure.identity.aio import ChainedTokenCredential, ManagedIdentityCredential
from azure.identity._credentials.imds import IMDS_TOKEN_PATH, IMDS_AUTHORITY
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import mock_response, Request
from helpers_async import get_completed_future, wrap_in_future, async_validating_transport


@pytest.mark.asyncio
async def test_close():
    credentials = [Mock(close=Mock(wraps=get_completed_future)) for _ in range(5)]
    chain = ChainedTokenCredential(*credentials)

    await chain.close()

    for credential in credentials:
        assert credential.close.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    credentials = [Mock(close=Mock(wraps=get_completed_future)) for _ in range(5)]
    chain = ChainedTokenCredential(*credentials)

    async with chain:
        pass

    for credential in credentials:
        assert credential.close.call_count == 1


@pytest.mark.asyncio
async def test_credential_chain_error_message():
    first_error = "first_error"
    first_credential = Mock(
        spec=ClientSecretCredential, get_token=Mock(side_effect=CredentialUnavailableError(first_error))
    )
    second_error = "second_error"
    second_credential = Mock(
        name="second_credential", get_token=Mock(side_effect=ClientAuthenticationError(second_error))
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        await ChainedTokenCredential(first_credential, second_credential).get_token("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


@pytest.mark.asyncio
async def test_chain_attempts_all_credentials():
    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    expected_token = AccessToken("expected_token", 0)
    credentials = [
        Mock(get_token=Mock(wraps=credential_unavailable)),
        Mock(get_token=Mock(wraps=credential_unavailable)),
        Mock(get_token=wrap_in_future(lambda _, **__: expected_token)),
    ]

    token = await ChainedTokenCredential(*credentials).get_token("scope")
    assert token is expected_token

    for credential in credentials[:-1]:
        assert credential.get_token.call_count == 1


@pytest.mark.asyncio
async def test_chain_raises_for_unexpected_error():
    """the chain should not continue after an unexpected error (i.e. anything but CredentialUnavailableError)"""

    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    expected_message = "it can't be done"

    credentials = [
        Mock(get_token=Mock(wraps=credential_unavailable)),
        Mock(get_token=Mock(side_effect=ValueError(expected_message))),
        Mock(get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken("**", 42)))),
    ]

    with pytest.raises(ClientAuthenticationError) as ex:
        await ChainedTokenCredential(*credentials).get_token("scope")

    assert expected_message in ex.value.message
    assert credentials[-1].get_token.call_count == 0


@pytest.mark.asyncio
async def test_returns_first_token():
    expected_token = Mock()
    first_credential = Mock(get_token=wrap_in_future(lambda _, **__: expected_token))
    second_credential = Mock(get_token=Mock())

    aggregate = ChainedTokenCredential(first_credential, second_credential)
    credential = await aggregate.get_token("scope")

    assert credential is expected_token
    assert second_credential.get_token.call_count == 0


@pytest.mark.asyncio
async def test_managed_identity_imds_probe():
    access_token = "****"
    expires_on = 42
    expected_token = AccessToken(access_token, expires_on)
    scope = "scope"
    transport = async_validating_transport(
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

    # ensure e.g. $MSI_ENDPOINT isn't set, so we get ImdsCredential
    with patch.dict("os.environ", clear=True):
        credentials = [
            Mock(get_token=Mock(side_effect=CredentialUnavailableError(message=""))),
            ManagedIdentityCredential(transport=transport),
        ]
        token = await ChainedTokenCredential(*credentials).get_token(scope)
    assert token == expected_token


@pytest.mark.asyncio
async def test_managed_identity_failed_probe():
    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    mock_send = Mock(side_effect=Exception("timeout"))
    transport = Mock(send=wrap_in_future(mock_send))

    expected_token = AccessToken("**", 42)
    credentials = [
        Mock(get_token=Mock(wraps=credential_unavailable)),
        ManagedIdentityCredential(transport=transport),
        Mock(get_token=Mock(wraps=wrap_in_future(lambda _, **__: expected_token))),
    ]

    with patch.dict("os.environ", clear=True):
        token = await ChainedTokenCredential(*credentials).get_token("scope")

    assert token is expected_token
    # ManagedIdentityCredential should be tried and skipped with the last credential in the chain
    # being used.
    assert credentials[-1].get_token.call_count == 1
