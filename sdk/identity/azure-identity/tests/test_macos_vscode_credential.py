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
    from azure.identity._credentials.macos_vscode_credential import MacOSVSCodeCredential
    from msal_extensions.osx import Keychain
except (ImportError, OSError):
    pass
try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = MacOSVSCodeCredential()
    with pytest.raises(ValueError):
        credential.get_token()


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch('Keychain.get_generic_password', return_value="VALUE"):
        credential = MacOSVSCodeCredential(policies=[policy], transport=mock.Mock(send=send))
        credential.get_token("scope")
        assert policy.on_request.called


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch('Keychain.get_generic_password', return_value="VALUE"):
        credential = MacOSVSCodeCredential(transport=transport)
        credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_credential_unavailable_error():
    with mock.patch('Keychain.get_generic_password', return_value=None):
        credential = MacOSVSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason="This test only runs on MacOS")
def test_get_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)

    with mock.patch('Keychain.get_generic_password', return_value="VALUE"):
        credential = MacOSVSCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_client.obtain_token_by_refresh_token.call_count == 1
