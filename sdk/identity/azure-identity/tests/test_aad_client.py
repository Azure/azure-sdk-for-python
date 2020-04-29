# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from azure.core.exceptions import ClientAuthenticationError
from azure.identity._constants import EnvironmentVariables
from azure.identity._internal.aad_client import AadClient
import pytest
from six.moves.urllib_parse import urlparse

from helpers import mock_response

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


class MockClient(AadClient):
    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop("session")
        super(MockClient, self).__init__(*args, **kwargs)

    def _get_client_session(self, **kwargs):
        return self.session


def test_uses_msal_correctly():
    session = Mock()
    transport = Mock()
    session.get = session.post = transport

    client = MockClient("tenant id", "client id", session=session)

    # MSAL will raise on each call because the mock transport returns nothing useful.
    # That's okay because we only want to verify the transport was called, i.e. that
    # the client used the MSAL API correctly, such that MSAL tried to send a request.
    with pytest.raises(ClientAuthenticationError):
        client.obtain_token_by_authorization_code("code", "redirect uri", "scope")
    assert transport.call_count == 1

    transport.reset_mock()

    with pytest.raises(ClientAuthenticationError):
        client.obtain_token_by_refresh_token("refresh token", "scope")
    assert transport.call_count == 1


def test_error_reporting():
    error_name = "everything's sideways"
    error_description = "something went wrong"
    error_response = {"error": error_name, "error_description": error_description}

    response = Mock(status_code=403, json=lambda: error_response)
    transport = Mock(return_value=response)
    session = Mock(get=transport, post=transport)
    client = MockClient("tenant id", "client id", session=session)

    fns = [
        functools.partial(client.obtain_token_by_authorization_code, "code", "uri", "scope"),
        functools.partial(client.obtain_token_by_refresh_token, {"secret": "refresh token"}, "scope"),
    ]

    # exceptions raised for AAD errors should contain AAD's error description
    for fn in fns:
        with pytest.raises(ClientAuthenticationError) as ex:
            fn()
        message = str(ex.value)
        assert error_name in message and error_description in message


def test_exceptions_do_not_expose_secrets():
    secret = "secret"
    body = {"error": "bad thing", "access_token": secret, "refresh_token": secret}
    response = Mock(status_code=403, json=lambda: body)
    transport = Mock(return_value=response)
    session = Mock(get=transport, post=transport)
    client = MockClient("tenant id", "client id", session=session)

    fns = [
        functools.partial(client.obtain_token_by_authorization_code, "code", "uri", "scope"),
        functools.partial(client.obtain_token_by_refresh_token, {"secret": "refresh token"}, "scope"),
    ]

    def assert_secrets_not_exposed():
        for fn in fns:
            with pytest.raises(ClientAuthenticationError) as ex:
                fn()
        assert secret not in str(ex.value)
        assert secret not in repr(ex.value)

    # AAD errors shouldn't provoke exceptions exposing secrets
    assert_secrets_not_exposed()

    # neither should unexpected AAD responses
    del body["error"]
    assert_secrets_not_exposed()


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_request_url(authority):
    tenant_id = "expected_tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def send(request, **_):
        actual = urlparse(request.url)
        assert actual.scheme == "https"
        assert actual.netloc == expected_netloc
        assert actual.path.startswith("/" + tenant_id)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": "***"})

    client = AadClient(tenant_id, "client id", transport=Mock(send=send), authority=authority)

    client.obtain_token_by_authorization_code("code", "uri", "scope")
    client.obtain_token_by_refresh_token("refresh token", "scope")

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        client = AadClient(tenant_id=tenant_id, client_id="client id", transport=Mock(send=send))
    client.obtain_token_by_authorization_code("code", "uri", "scope")
    client.obtain_token_by_refresh_token("refresh token", "scope")
