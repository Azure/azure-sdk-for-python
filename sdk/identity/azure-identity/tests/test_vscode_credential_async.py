# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.identity import CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import VSCodeCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
import pytest

from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future


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
@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
async def test_request_url(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected_tenant"
    access_token = "***"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"
    expected_refresh_token = "refresh-token"

    async def mock_send(request, **kwargs):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        assert request.body["refresh_token"] == expected_refresh_token
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    credential = VSCodeCredential(tenant_id=tenant_id, transport=mock.Mock(send=mock_send), authority=authority)
    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value=expected_refresh_token):
        token = await credential.get_token("scope")
    assert token.token == access_token

    # authority can be configured via environment variable
    with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = VSCodeCredential(tenant_id=tenant_id, transport=mock.Mock(send=mock_send))
        with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value=expected_refresh_token):
            await credential.get_token("scope")
    assert token.token == access_token


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

    mock_client = mock.Mock(should_refresh=lambda _: False)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)
    mock_client.get_cached_access_token = mock.Mock(return_value="VALUE")

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(_client=mock_client)
        token = await credential.get_token("scope")
        assert token_by_refresh_token.call_count == 0
