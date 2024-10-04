# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest.mock import Mock, patch

from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError, ClientSecretCredential
from azure.identity.aio import ChainedTokenCredential, ManagedIdentityCredential
from azure.identity._credentials.imds import IMDS_TOKEN_PATH, IMDS_AUTHORITY
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import mock_response, Request, GET_TOKEN_METHODS
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
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_credential_chain_error_message(get_token_method):
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
        await getattr(ChainedTokenCredential(first_credential, second_credential), get_token_method)("scope")

    assert "ClientSecretCredential" in ex.value.message
    assert first_error in ex.value.message
    assert second_error in ex.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_chain_attempts_all_credentials(get_token_method):
    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    access_token = "expected_token"
    credentials = [
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(wraps=credential_unavailable),
            get_token_info=Mock(wraps=credential_unavailable),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(wraps=credential_unavailable),
            get_token_info=Mock(wraps=credential_unavailable),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=wrap_in_future(lambda _, **__: AccessToken(access_token, 42)),
            get_token_info=wrap_in_future(lambda _, **__: AccessTokenInfo(access_token, 42)),
        ),
    ]

    token = await getattr(ChainedTokenCredential(*credentials), get_token_method)("scope")
    assert token.token == access_token

    for credential in credentials[:-1]:
        assert getattr(credential, get_token_method).call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_chain_raises_for_unexpected_error(get_token_method):
    """the chain should not continue after an unexpected error (i.e. anything but CredentialUnavailableError)"""

    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    expected_message = "it can't be done"

    credentials = [
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(wraps=credential_unavailable),
            get_token_info=Mock(wraps=credential_unavailable),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(side_effect=ValueError(expected_message)),
            get_token_info=Mock(side_effect=ValueError(expected_message)),
        ),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken("**", 42))),
            get_token_info=Mock(wraps=wrap_in_future(lambda _, **__: AccessTokenInfo("**", 42))),
        ),
    ]

    with pytest.raises(ClientAuthenticationError) as ex:
        await getattr(ChainedTokenCredential(*credentials), get_token_method)("scope")

    assert expected_message in ex.value.message
    assert getattr(credentials[-1], get_token_method).call_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_returns_first_token(get_token_method):
    access_token = "expected_token"
    first_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=wrap_in_future(lambda _, **__: AccessToken(access_token, 42)),
        get_token_info=wrap_in_future(lambda _, **__: AccessTokenInfo(access_token, 42)),
    )
    second_credential = Mock(spec_set=["get_token", "get_token_info"], get_token=Mock(), get_token_info=Mock())

    aggregate = ChainedTokenCredential(first_credential, second_credential)
    token = await getattr(aggregate, get_token_method)("scope")

    assert token.token == access_token
    assert getattr(second_credential, get_token_method).call_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_managed_identity_imds_probe(get_token_method):
    access_token = "****"
    expires_on = 42
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
            Mock(
                spec_set=["get_token", "get_token_info"],
                get_token=Mock(side_effect=CredentialUnavailableError(message="")),
                get_token_info=Mock(side_effect=CredentialUnavailableError(message="")),
            ),
            ManagedIdentityCredential(transport=transport),
        ]
        token = await getattr(ChainedTokenCredential(*credentials), get_token_method)(scope)
    assert token.token == access_token


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_managed_identity_failed_probe(get_token_method):
    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    mock_send = Mock(side_effect=Exception("timeout"))
    transport = Mock(send=wrap_in_future(mock_send))

    expected_token = "***"
    credentials = [
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(wraps=credential_unavailable),
            get_token_info=Mock(wraps=credential_unavailable),
        ),
        ManagedIdentityCredential(transport=transport),
        Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken(expected_token, 42))),
            get_token_info=Mock(wraps=wrap_in_future(lambda _, **__: AccessTokenInfo(expected_token, 42))),
        ),
    ]

    with patch.dict("os.environ", clear=True):
        token = await getattr(ChainedTokenCredential(*credentials), get_token_method)("scope")

    assert token.token == expected_token
    # ManagedIdentityCredential should be tried and skipped with the last credential in the chain
    # being used.
    assert getattr(credentials[-1], get_token_method).call_count == 1


@pytest.mark.asyncio
async def test_credentials_with_no_get_token_info():
    """ChainedTokenCredential should work with credentials that don't implement get_token_info."""

    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    access_token = "****"
    credential1 = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(wraps=credential_unavailable),
    )
    credential2 = Mock(
        spec_set=["get_token"],
        get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken(access_token, 42))),
    )
    credential3 = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken("foo", 42))),
        get_token_info=Mock(wraps=wrap_in_future(lambda _, **__: AccessTokenInfo("bar", 42))),
    )
    chain = ChainedTokenCredential(credential1, credential2, credential3)  # type: ignore
    token_info = await chain.get_token_info("scope")
    assert token_info.token == access_token


@pytest.mark.asyncio
async def test_credentials_with_no_get_token():
    """ChainedTokenCredential should work with credentials that only implement get_token_info."""

    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    access_token = "****"
    credential1 = Mock(
        spec_set=["get_token"],
        get_token=Mock(wraps=credential_unavailable),
    )
    credential2 = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(wraps=wrap_in_future(lambda _, **__: AccessTokenInfo(access_token, 42))),
    )
    credential3 = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken("foo", 42))),
        get_token_info=Mock(wraps=wrap_in_future(lambda _, **__: AccessTokenInfo("bar", 42))),
    )
    chain = ChainedTokenCredential(credential1, credential2, credential3)  # type: ignore
    token_info = await chain.get_token("scope")
    assert token_info.token == access_token


@pytest.mark.asyncio
async def test_credentials_with_pop_option():
    """ChainedTokenCredential should skip credentials that don't support get_token_info and the pop option is set."""

    async def credential_unavailable(message="it didn't work", **_):
        raise CredentialUnavailableError(message)

    access_token = "****"
    credential1 = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(wraps=credential_unavailable),
    )
    credential2 = Mock(
        spec_set=["get_token"],
        get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken("foo", 42))),
    )
    credential3 = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(wraps=wrap_in_future(lambda _, **__: AccessToken("bar", 42))),
        get_token_info=Mock(wraps=wrap_in_future(lambda _, **__: AccessTokenInfo(access_token, 42))),
    )
    chain = ChainedTokenCredential(credential1, credential2, credential3)  # type: ignore
    token_info = await chain.get_token_info("scope", options={"pop": True})  # type: ignore
    assert token_info.token == access_token
