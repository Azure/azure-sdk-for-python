# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
from azure.identity import CredentialUnavailableError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity._internal.user_agent import USER_AGENT
from helpers import build_aad_response, mock_response, Request, validating_transport
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore
if sys.platform.startswith('win'):
    from azure.identity._credentials.win_vscode_credential import (
        WinVSCodeCredential,
        _read_credential,
        _cred_write,
        _cred_delete,
    )

@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_win_vscode_credential():
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
    token_read = _read_credential(service_name, account_name)
    assert token_read == token_written


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = WinVSCodeCredential()
    with pytest.raises(ValueError):
        credential.get_token()


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_policies_configurable():
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

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = WinVSCodeCredential(policies=[policy], transport=Mock(send=send))

    credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_user_agent():
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

    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = WinVSCodeCredential(transport=transport)

    credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_credential_unavailable_error():
    service_name = "VS Code Azure"
    account_name = "Azure"
    _cred_delete(service_name, account_name)
    credential = WinVSCodeCredential()
    with pytest.raises(CredentialUnavailableError):
        token = credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_get_token():
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
    mock_client.obtain_token_by_refresh_token = Mock(return_value=expected_token)

    credential = WinVSCodeCredential(
        _client=mock_client,
    )

    token = credential.get_token("scope")
    assert token is expected_token
    assert mock_client.obtain_token_by_refresh_token.call_count == 1
