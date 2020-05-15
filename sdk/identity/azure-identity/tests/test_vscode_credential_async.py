# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.core.credentials import AccessToken
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity import CredentialUnavailableError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future
from unittest import mock
from azure.identity.aio._credentials.vscode_credential import VSCodeCredential


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = VSCodeCredential()
    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(policies=[policy], transport=mock.Mock(send=send))
        await credential.get_token("scope")
        assert policy.on_request.called


@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(transport=transport)
        await credential.get_token("scope")


@pytest.mark.asyncio
async def test_credential_unavailable_error():
    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value=None):
        credential = VSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            token = await credential.get_token("scope")


@pytest.mark.asyncio
async def test_redeem_token():
    expected_token = AccessToken("token", 42)
    expected_value = "value"

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value=expected_value):
        credential = VSCodeCredential(_client=mock_client)
        token = await credential.get_token("scope")
        assert token is expected_token
        token_by_refresh_token.assert_called_with(("scope",), expected_value)


@pytest.mark.asyncio
async def test_cache_refresh_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)
    mock_get_credentials = mock.Mock(return_value="VALUE")

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", mock_get_credentials):
        credential = VSCodeCredential(_client=mock_client)
        token = await credential.get_token("scope")
        assert mock_get_credentials.call_count == 1
        token = await credential.get_token("scope")
        assert mock_get_credentials.call_count == 1


@pytest.mark.asyncio
async def test_no_obtain_token_if_cached():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)
    mock_client.get_cached_access_token = mock.Mock(return_value="VALUE")

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(_client=mock_client)
        token = await credential.get_token("scope")
        assert token_by_refresh_token.call_count == 0
