# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    AuthenticationRequiredError,
    AuthenticationRecord,
    KnownAuthorities,
    CredentialUnavailableError,
    TokenCachePersistenceOptions,
)
from azure.identity._internal import EnvironmentVariables, InteractiveCredential
import pytest
from six.moves.urllib_parse import urlparse

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from helpers import build_aad_response, get_discovery_response, id_token_claims


# fake object for tests which need to exercise request_token but don't care about its return value
REQUEST_TOKEN_RESULT = build_aad_response(
    access_token="***",
    id_token_claims=id_token_claims(
        aud="...",
        iss="http://localhost/tenant",
        sub="subject",
        preferred_username="...",
        tenant_id="...",
        object_id="...",
    ),
)


class MockCredential(InteractiveCredential):
    """Test class to drive InteractiveCredential.

    Default instances have an empty in-memory cache, and raise rather than send an HTTP request.
    """

    def __init__(self, client_id="...", request_token=None, transport=None, **kwargs):
        self._request_token_impl = request_token or Mock()
        transport = transport or Mock(send=Mock(side_effect=Exception("credential shouldn't send a request")))
        super(MockCredential, self).__init__(client_id=client_id, transport=transport, **kwargs)

    def _request_token(self, *scopes, **kwargs):
        return self._request_token_impl(*scopes, **kwargs)


def test_no_scopes():
    """The credential should raise when get_token is called with no scopes"""

    request_token = Mock(side_effect=Exception("credential shouldn't begin interactive authentication"))
    with pytest.raises(ValueError):
        MockCredential(request_token=request_token).get_token()


def test_authentication_record_argument():
    """The credential should initialize its msal.ClientApplication with values from a given record"""

    record = AuthenticationRecord("tenant-id", "client-id", "localhost", "object.tenant", "username")

    def validate_app_parameters(authority, client_id, **_):
        # the 'authority' argument to msal.ClientApplication should be a URL of the form https://authority/tenant
        assert authority == "https://{}/{}".format(record.authority, record.tenant_id)
        assert client_id == record.client_id
        return Mock(get_accounts=Mock(return_value=[]))

    mock_client_application = Mock(wraps=validate_app_parameters)
    credential = MockCredential(authentication_record=record, disable_automatic_authentication=True)
    with pytest.raises(AuthenticationRequiredError):
        with patch("msal.PublicClientApplication", mock_client_application):
            credential.get_token("scope")

    assert mock_client_application.call_count == 1, "credential didn't create an msal application"


def test_tenant_argument_overrides_record():
    """The 'tenant_ic' keyword argument should override a given record's value"""

    tenant_id = "some-guid"
    authority = "localhost"
    record = AuthenticationRecord(tenant_id, "client-id", authority, "object.tenant", "username")

    expected_tenant = tenant_id[::-1]
    expected_authority = "https://{}/{}".format(authority, expected_tenant)

    def validate_authority(authority, **_):
        assert authority == expected_authority
        return Mock(get_accounts=Mock(return_value=[]))

    credential = MockCredential(
        authentication_record=record, tenant_id=expected_tenant, disable_automatic_authentication=True
    )
    with pytest.raises(AuthenticationRequiredError):
        with patch("msal.PublicClientApplication", validate_authority):
            credential.get_token("scope")


def test_disable_automatic_authentication():
    """When silent auth fails the credential should raise, if it's configured not to authenticate automatically"""

    expected_details = "something went wrong"
    record = AuthenticationRecord("tenant-id", "client-id", "localhost", "object.tenant", "username")
    msal_app = Mock(
        acquire_token_silent_with_error=Mock(return_value={"error_description": expected_details}),
        get_accounts=Mock(return_value=[{"home_account_id": record.home_account_id}]),
    )

    credential = MockCredential(
        authentication_record=record,
        disable_automatic_authentication=True,
        request_token=Mock(side_effect=Exception("credential shouldn't begin interactive authentication")),
    )

    scope = "scope"
    expected_claims = "..."
    with pytest.raises(AuthenticationRequiredError) as ex:
        with patch("msal.PublicClientApplication", lambda *_, **__: msal_app):
            credential.get_token(scope, claims=expected_claims)

    # the exception should carry the requested scopes and claims, and any error message from AAD
    assert ex.value.scopes == (scope,)
    assert ex.value.claims == expected_claims


def test_scopes_round_trip():
    """authenticate should accept the value of AuthenticationRequiredError.scopes"""

    scope = "scope"

    def validate_scopes(*scopes, **_):
        assert scopes == (scope,)
        return REQUEST_TOKEN_RESULT

    request_token = Mock(wraps=validate_scopes)
    credential = MockCredential(disable_automatic_authentication=True, request_token=request_token)
    with pytest.raises(AuthenticationRequiredError) as ex:
        credential.get_token(scope)

    credential.authenticate(scopes=ex.value.scopes)

    assert request_token.call_count == 1, "validation method wasn't called"


@pytest.mark.parametrize(
    "authority,expected_scope",
    (
        (KnownAuthorities.AZURE_CHINA, "https://management.core.chinacloudapi.cn//.default"),
        (KnownAuthorities.AZURE_GERMANY, "https://management.core.cloudapi.de//.default"),
        (KnownAuthorities.AZURE_GOVERNMENT, "https://management.core.usgovcloudapi.net//.default"),
        (KnownAuthorities.AZURE_PUBLIC_CLOUD, "https://management.core.windows.net//.default"),
    ),
)
def test_authenticate_default_scopes(authority, expected_scope):
    """when given no scopes, authenticate should default to the ARM scope appropriate for the configured authority"""

    def validate_scopes(*scopes):
        assert scopes == (expected_scope,)
        return REQUEST_TOKEN_RESULT

    request_token = Mock(wraps=validate_scopes)
    MockCredential(authority=authority, request_token=request_token).authenticate()
    assert request_token.call_count == 1


def test_authenticate_unknown_cloud():
    """authenticate should raise when given no scopes in an unknown cloud"""

    with pytest.raises(CredentialUnavailableError):
        MockCredential(authority="localhost").authenticate()


@pytest.mark.parametrize("option", (True, False))
def test_authenticate_ignores_disable_automatic_authentication(option):
    """authenticate should prompt for authentication regardless of the credential's configuration"""

    request_token = Mock(return_value=REQUEST_TOKEN_RESULT)
    MockCredential(request_token=request_token, disable_automatic_authentication=option).authenticate()
    assert request_token.call_count == 1, "credential didn't begin interactive authentication"


def test_get_token_wraps_exceptions():
    """get_token shouldn't propagate exceptions from MSAL"""

    class CustomException(Exception):
        pass

    expected_message = "something went wrong"
    record = AuthenticationRecord("tenant-id", "client-id", "localhost", "object.tenant", "username")
    msal_app = Mock(
        acquire_token_silent_with_error=Mock(side_effect=CustomException(expected_message)),
        get_accounts=Mock(return_value=[{"home_account_id": record.home_account_id}]),
    )
    credential = MockCredential(authentication_record=record)
    with pytest.raises(ClientAuthenticationError) as ex:
        with patch("msal.PublicClientApplication", lambda *_, **__: msal_app):
            credential.get_token("scope")

    assert expected_message in ex.value.message
    assert msal_app.acquire_token_silent_with_error.call_count == 1, "credential didn't attempt silent auth"


def test_token_cache():
    """the credential should default to an in memory cache, and optionally use a persistent cache"""

    class TestCredential(InteractiveCredential):
        def __init__(self, **kwargs):
            super(TestCredential, self).__init__(client_id="...", **kwargs)

        def _request_token(self, *_, **__):
            pass

    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as load_persistent_cache:
        with patch("azure.identity._internal.msal_credentials.msal") as mock_msal:
            TestCredential()
        assert not load_persistent_cache.called
        assert mock_msal.TokenCache.call_count == 1

        TestCredential(cache_persistence_options=TokenCachePersistenceOptions())
        assert load_persistent_cache.call_count == 1


def test_home_account_id_client_info():
    """when MSAL returns client_info, the credential should decode it to get the home_account_id"""

    object_id = "object-id"
    home_tenant = "home-tenant-id"
    msal_response = build_aad_response(uid=object_id, utid=home_tenant, access_token="***", refresh_token="**")
    msal_response["id_token_claims"] = {
        "aud": "client-id",
        "iss": "https://localhost",
        "object_id": object_id,
        "tid": home_tenant,
        "preferred_username": "me",
        "sub": "subject",
    }

    class TestCredential(InteractiveCredential):
        def __init__(self, **kwargs):
            super(TestCredential, self).__init__(client_id="...", **kwargs)

        def _request_token(self, *_, **__):
            return msal_response

    record = TestCredential().authenticate()
    assert record.home_account_id == "{}.{}".format(object_id, home_tenant)


def test_adfs():
    """the credential should be able to construct an AuthenticationRecord from an ADFS response returned by MSAL"""

    authority = "localhost"
    subject = "subject"
    tenant = "adfs"
    username = "username"
    msal_response = build_aad_response(access_token="***", refresh_token="**")
    msal_response["id_token_claims"] = id_token_claims(
        aud="client-id",
        iss="https://{}/{}".format(authority, tenant),
        sub=subject,
        tenant_id=tenant,
        object_id="object-id",
        upn=username,
    )

    class TestCredential(InteractiveCredential):
        def __init__(self, **kwargs):
            super(TestCredential, self).__init__(client_id="...", **kwargs)

        def _request_token(self, *_, **__):
            return msal_response

    record = TestCredential().authenticate()
    assert record.authority == authority
    assert record.home_account_id == subject
    assert record.tenant_id == tenant
    assert record.username == username


def test_multitenant_authentication():
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def request_token(*args, **kwargs):
        tenant_id = kwargs.get("tenant_id")
        return build_aad_response(
            access_token=second_token if tenant_id == second_tenant else first_token,
            id_token_claims=id_token_claims(
                aud="...",
                iss="http://localhost/tenant",
                sub="subject",
                preferred_username="...",
                tenant_id="...",
                object_id="...",
            ),
        )

    def send(request, **_):
        assert "/oauth2/v2.0/token" not in request.url, 'mock "request_token" should prevent sending a token request'
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

    credential = MockCredential(
        tenant_id=first_tenant,
        request_token=request_token,
        transport=Mock(send=send),
    )
    token = credential.get_token("scope")
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=first_tenant)
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=second_tenant)
    assert token.token == second_token

    # should still default to the first tenant
    token = credential.get_token("scope")
    assert token.token == first_token

def test_multitenant_authentication_not_allowed():
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def request_token(*_, **__):
        return build_aad_response(
            access_token=expected_token,
            id_token_claims=id_token_claims(
                aud="...",
                iss="http://localhost/tenant",
                sub="subject",
                preferred_username="...",
                tenant_id="...",
                object_id="...",
            ),
        )

    def send(request, **_):
        assert "/oauth2/v2.0/token" not in request.url, 'mock "request_token" should prevent sending a token request'
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

    credential = MockCredential(tenant_id=expected_tenant, transport=Mock(send=send), request_token=request_token)

    token = credential.get_token("scope")
    assert token.token == expected_token

    token = credential.get_token("scope", tenant_id=expected_tenant)
    assert token.token == expected_token

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
        token = credential.get_token("scope", tenant_id="un" + expected_tenant)
        assert token.token == expected_token
