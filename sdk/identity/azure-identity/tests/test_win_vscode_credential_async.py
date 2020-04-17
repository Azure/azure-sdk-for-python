# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity import CredentialUnavailableError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from helpers import build_aad_response, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport, wrap_in_future
from unittest.mock import Mock
if sys.platform.startswith('win'):
    from azure.identity.aio._credentials.win_vscode_credential import WinVSCodeCredential
    from azure.identity._credentials.win_vscode_credential import _cred_write, _cred_delete


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = WinVSCodeCredential()
    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_policies_configurable():
    service_name = "VS Code Azure"
    account_name = "Azure"
    target = "{}/{}".format(service_name, account_name)
    comment = "comment"
    token_written = "test_refresh_token"
    user_name = "Azure"
    credential = {"Type": 0x1,
                  "TargetName": target,
                  "UserName": user_name,
                  "CredentialBlob": token_written,
                  "Comment": comment,
                  "Persist": 0x2}
    _cred_write(credential)

    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = WinVSCodeCredential(policies=[policy], transport=Mock(send=send))

    await credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_user_agent():
    service_name = "VS Code Azure"
    account_name = "Azure"
    target = "{}/{}".format(service_name, account_name)
    comment = "comment"
    token_written = "test_refresh_token"
    user_name = "Azure"
    credential = {"Type": 0x1,
                  "TargetName": target,
                  "UserName": user_name,
                  "CredentialBlob": token_written,
                  "Comment": comment,
                  "Persist": 0x2}
    _cred_write(credential)

    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = WinVSCodeCredential(transport=transport)

    await credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_credential_unavailable_error():
    service_name = "VS Code Azure"
    account_name = "Azure"
    _cred_delete(service_name, account_name)
    credential = WinVSCodeCredential()
    with pytest.raises(CredentialUnavailableError):
        token = await credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_get_token():
    service_name = "VS Code Azure"
    account_name = "Azure"
    target = "{}/{}".format(service_name, account_name)
    comment = "comment"
    token_written = "test_refresh_token"
    user_name = "Azure"
    credential = {"Type": 0x1,
                  "TargetName": target,
                  "UserName": user_name,
                  "CredentialBlob": token_written,
                  "Comment": comment,
                  "Persist": 0x2}
    _cred_write(credential)

    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    token_by_refresh_token = Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)

    credential = WinVSCodeCredential(
        _client=mock_client,
    )

    token = await credential.get_token("scope")
    assert token is expected_token
