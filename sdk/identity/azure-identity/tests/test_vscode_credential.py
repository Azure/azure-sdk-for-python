# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys

from azure.core.credentials import AccessToken
from azure.identity import CredentialUnavailableError, VisualStudioCodeCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity._credentials.vscode import get_credentials
import pytest
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, mock_response, Request, validating_transport

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        VisualStudioCodeCredential(tenant_id=tenant)

    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            VisualStudioCodeCredential(tenant_id=tenant)


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = VisualStudioCodeCredential()
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = mock.Mock(spec_set=SansIOHTTPPolicy, on_request=mock.Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VisualStudioCodeCredential(policies=[policy], transport=mock.Mock(send=send))
        credential.get_token("scope")
        assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VisualStudioCodeCredential(transport=transport)
        credential.get_token("scope")


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_request_url(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    access_token = "***"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"
    expected_refresh_token = "refresh-token"

    def mock_send(request, **kwargs):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        assert request.body["refresh_token"] == expected_refresh_token
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    credential = VisualStudioCodeCredential(
        tenant_id=tenant_id, transport=mock.Mock(send=mock_send), authority=authority
    )
    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", return_value=expected_refresh_token):
        token = credential.get_token("scope")
    assert token.token == access_token

    # authority can be configured via environment variable
    with mock.patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = VisualStudioCodeCredential(tenant_id=tenant_id, transport=mock.Mock(send=mock_send))
        with mock.patch(
            VisualStudioCodeCredential.__module__ + ".get_credentials", return_value=expected_refresh_token
        ):
            credential.get_token("scope")
    assert token.token == access_token


def test_credential_unavailable_error():
    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", return_value=None):
        credential = VisualStudioCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            token = credential.get_token("scope")


def test_redeem_token():
    expected_token = AccessToken("token", 42)
    expected_value = "value"

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)

    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", return_value=expected_value):
        credential = VisualStudioCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        mock_client.obtain_token_by_refresh_token.assert_called_with(("scope",), expected_value)
        assert mock_client.obtain_token_by_refresh_token.call_count == 1


def test_cache_refresh_token():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value=None)
    mock_get_credentials = mock.Mock(return_value="VALUE")

    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", mock_get_credentials):
        credential = VisualStudioCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_get_credentials.call_count == 1
        token = credential.get_token("scope")
        assert token is expected_token
        assert mock_get_credentials.call_count == 1


def test_no_obtain_token_if_cached():
    expected_token = AccessToken("token", 42)

    mock_client = mock.Mock(should_refresh=lambda _: False)
    mock_client.obtain_token_by_refresh_token = mock.Mock(return_value=expected_token)
    mock_client.get_cached_access_token = mock.Mock(return_value="VALUE")

    with mock.patch(VisualStudioCodeCredential.__module__ + ".get_credentials", return_value="VALUE"):
        credential = VisualStudioCodeCredential(_client=mock_client)
        token = credential.get_token("scope")
        assert mock_client.obtain_token_by_refresh_token.call_count == 0


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="This test only runs on Linux")
def test_segfault():
    from azure.identity._internal.linux_vscode_adapter import _get_refresh_token

    _get_refresh_token("test", "test")


@pytest.mark.skipif(not sys.platform.startswith("darwin"), reason="This test only runs on MacOS")
def test_mac_keychain_valid_value():
    with mock.patch("msal_extensions.osx.Keychain.get_generic_password", return_value="VALUE"):
        assert get_credentials() == "VALUE"


@pytest.mark.skipif(not sys.platform.startswith("darwin"), reason="This test only runs on MacOS")
def test_mac_keychain_error():
    from msal_extensions.osx import Keychain, KeychainError

    with mock.patch.object(Keychain, "get_generic_password", side_effect=KeychainError(-1)):
        credential = VisualStudioCodeCredential()
        with pytest.raises(CredentialUnavailableError):
            token = credential.get_token("scope")


def test_adfs():
    """The credential should raise CredentialUnavailableError when configured for ADFS"""

    credential = VisualStudioCodeCredential(tenant_id="adfs")
    with pytest.raises(CredentialUnavailableError) as ex:
        credential.get_token("scope")
    assert "adfs" in ex.value.message.lower()
