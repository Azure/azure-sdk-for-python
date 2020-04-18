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
    from azure.identity.aio._credentials.linux_vscode_credential import LinuxVSCodeCredential
except (ImportError, OSError):
    pass


@pytest.mark.skipif(sys.platform.startswith('darwin') or sys.platform.startswith('win') , reason="This test only runs on Linux")
@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = LinuxVSCodeCredential()
    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.skipif(sys.platform.startswith('darwin') or sys.platform.startswith('win') , reason="This test only runs on Linux")
@pytest.mark.asyncio
async def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch('azure.identity._credentials.linux_vscode_credential._get_refresh_token', return_value="VALUE"):
        credential = LinuxVSCodeCredential(policies=[policy], transport=mock.Mock(send=send))
        await credential.get_token("scope")
        assert policy.on_request.called


@pytest.mark.skipif(sys.platform.startswith('darwin') or sys.platform.startswith('win') , reason="This test only runs on Linux")
@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch('azure.identity._credentials.linux_vscode_credential._get_refresh_token', return_value="VALUE"):
        credential = LinuxVSCodeCredential(transport=transport)
        await credential.get_token("scope")

@pytest.mark.skipif(sys.platform.startswith('darwin') or sys.platform.startswith('win') , reason="This test only runs on Linux")
@pytest.mark.asyncio
async def test_credential_unavailable_error():
    with mock.patch('azure.identity._credentials.linux_vscode_credential._get_refresh_token', return_value=None):
        credential = LinuxVSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            await credential.get_token("scope")


@pytest.mark.skipif(sys.platform.startswith('darwin') or sys.platform.startswith('win') , reason="This test only runs on Linux")
@pytest.mark.asyncio
async def test_get_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)

    with mock.patch('azure.identity._credentials.linux_vscode_credential._get_refresh_token', return_value="VALUE"):
        credential = LinuxVSCodeCredential(_client=mock_client)
        token = await credential.get_token("scope")
        assert token is expected_token
