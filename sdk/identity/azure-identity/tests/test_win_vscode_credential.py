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
    from unittest import mock
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    import mock
    from mock import Mock  # type: ignore
if sys.platform.startswith('win'):
    from azure.identity._credentials.win_vscode_credential import (
        WinVSCodeCredential,
    )


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = WinVSCodeCredential()
    with pytest.raises(ValueError):
        credential.get_token()


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch('azure.identity._credentials.win_vscode_credential._read_credential', return_value="VALUE"):
        credential = WinVSCodeCredential(policies=[policy], transport=Mock(send=send))
        credential.get_token("scope")
        assert policy.on_request.called


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch('azure.identity._credentials.win_vscode_credential._read_credential', return_value="VALUE"):
        credential = WinVSCodeCredential(transport=transport)
        credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_credential_unavailable_error():
    with mock.patch('azure.identity._credentials.win_vscode_credential._read_credential', return_value=None):
        credential = WinVSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            token = credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_get_token():
    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = Mock(return_value=expected_token)

    with mock.patch('azure.identity._credentials.win_vscode_credential._read_credential', return_value="VALUE"):
        credential = WinVSCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_client.obtain_token_by_refresh_token.call_count == 1
