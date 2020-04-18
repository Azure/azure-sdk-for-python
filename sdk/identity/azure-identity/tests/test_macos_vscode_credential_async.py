# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.identity import CredentialUnavailableError
from azure.core.credentials import AccessToken
from azure.identity._internal.user_agent import USER_AGENT
from azure.core.pipeline.policies import SansIOHTTPPolicy
from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future
from unittest import mock
try:
    from azure.identity.aio._credentials.macos_vscode_credential import MacOSVSCodeCredential
    from msal_extensions.osx import Keychain
except (ImportError, OSError):
    pass


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = MacOSVSCodeCredential()
    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
@pytest.mark.asyncio
async def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch('Keychain.get_generic_password', return_value="VALUE"):
        credential = MacOSVSCodeCredential(policies=[policy], transport=mock.Mock(send=send))
        await credential.get_token("scope")
        assert policy.on_request.called


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch('Keychain.get_generic_password', return_value="VALUE"):
        credential = MacOSVSCodeCredential(transport=transport)
        await credential.get_token("scope")

@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
@pytest.mark.asyncio
async def test_credential_unavailable_error():
    with mock.patch('Keychain.get_generic_password', return_value=None):
        credential = MacOSVSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            await credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
@pytest.mark.asyncio
async def test_get_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)

    with mock.patch('Keychain.get_generic_password', return_value="VALUE"):
        credential = MacOSVSCodeCredential(_client=mock_client)
        token = await credential.get_token("scope")
        assert token is expected_token
