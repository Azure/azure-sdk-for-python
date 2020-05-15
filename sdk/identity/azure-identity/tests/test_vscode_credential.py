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
except ImportError:  # python < 3.3
    import mock
from azure.identity._credentials.vscode_credential import VSCodeCredential, get_credentials


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = VSCodeCredential()
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(policies=[policy], transport=mock.Mock(send=send))
        credential.get_token("scope")
        assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(transport=transport)
        credential.get_token("scope")


def test_credential_unavailable_error():
    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value=None):
        credential = VSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            token = credential.get_token("scope")


def test_redeem_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        mock_client.obtain_token_by_refresh_token.assert_called_with("VALUE", ("scope",))
        assert mock_client.obtain_token_by_refresh_token.call_count == 1


def test_cache_refresh_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)
    mock_get_credentials = mock.Mock(return_value="VALUE")

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", mock_get_credentials):
        credential = VSCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_get_credentials.call_count == 1
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_get_credentials.call_count == 1


def test_no_obtain_token_if_cached():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value="VALUE")

    with mock.patch(VSCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VSCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert mock_client.obtain_token_by_refresh_token.call_count == 0


@pytest.mark.skipif(not sys.platform.startswith("darwin"), reason="This test only runs on MacOS")
def test_mac_keychain_valid_value():
    with mock.patch("msal_extensions.osx.Keychain.get_generic_password", return_value="VALUE"):
        assert get_credentials() == "VALUE"


@pytest.mark.skipif(not sys.platform.startswith("darwin"), reason="This test only runs on MacOS")
def test_mac_keychain_error():
    from msal_extensions.osx import Keychain, KeychainError

    with mock.patch.object(Keychain, "get_generic_password", side_effect=KeychainError(-1)):
        credential = VSCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            token = credential.get_token("scope")


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="This test only runs on Linux")
def test_get_token():
    with mock.patch("azure.identity._credentials.linux_vscode_adapter._get_refresh_token", return_value="VALUE"):
        assert get_credentials() == "VALUE"
