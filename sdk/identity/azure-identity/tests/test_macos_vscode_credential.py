# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity._internal.user_agent import USER_AGENT
from helpers import build_aad_response, mock_response, Request, validating_transport
try:
    from azure.identity._credentials.macos_vscode_credential import MacOSVSCodeCredential
    from msal_extensions.osx import Keychain
except (ImportError, OSError):
    pass
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = MacOSVSCodeCredential()
    with pytest.raises(ValueError):
        credential.get_token()


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_policies_configurable():
    key_chain = Keychain()
    key_chain.set_generic_password("VS Code Azure", "Azure", "value")

    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = MacOSVSCodeCredential(policies=[policy], transport=Mock(send=send))

    credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_user_agent():
    key_chain = Keychain()
    key_chain.set_generic_password("VS Code Azure", "Azure", "value")

    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = MacOSVSCodeCredential(transport=transport)

    credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_get_token():
    key_chain = Keychain()
    key_chain.set_generic_password("VS Code Azure", "Azure", "value")

    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = Mock(return_value=expected_token)

    credential = MacOSVSCodeCredential(
        _client=mock_client,
    )

    token = credential.get_token("scope")
    assert token is expected_token
    assert mock_client.obtain_token_by_refresh_token.call_count == 1
