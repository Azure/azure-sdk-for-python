# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    KnownAuthorities,
    CredentialUnavailableError,
)
from azure.identity._auth_record import AuthenticationRecord
from azure.identity._exceptions import AuthenticationRequiredError
from azure.identity._internal import InteractiveCredential
from msal import TokenCache
import pytest

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from helpers import build_aad_response, build_id_token, id_token_claims


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

    def __init__(
        self, client_id="...", request_token=None, cache=None, msal_app_factory=None, transport=None, **kwargs
    ):
        self._msal_app_factory = msal_app_factory
        self._request_token_impl = request_token or Mock()
        transport = transport or Mock(send=Mock(side_effect=Exception("credential shouldn't send a request")))
        super(MockCredential, self).__init__(
            client_id=client_id, _cache=cache or TokenCache(), transport=transport, **kwargs
        )

    def _request_token(self, *scopes, **kwargs):
        return self._request_token_impl(*scopes, **kwargs)

    def _get_app(self):
        if self._msal_app_factory:
            return self._create_app(self._msal_app_factory)
        return super(MockCredential, self)._get_app()


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

    app_factory = Mock(wraps=validate_app_parameters)
    credential = MockCredential(
        _authentication_record=record, _disable_automatic_authentication=True, msal_app_factory=app_factory,
    )
    with pytest.raises(AuthenticationRequiredError):
        credential.get_token("scope")

    assert app_factory.call_count == 1, "credential didn't create an msal application"


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
        _authentication_record=record,
        tenant_id=expected_tenant,
        _disable_automatic_authentication=True,
        msal_app_factory=validate_authority,
    )
    with pytest.raises(AuthenticationRequiredError):
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
        _authentication_record=record,
        _disable_automatic_authentication=True,
        msal_app_factory=lambda *_, **__: msal_app,
        request_token=Mock(side_effect=Exception("credential shouldn't begin interactive authentication")),
    )

    scope = "scope"
    with pytest.raises(AuthenticationRequiredError) as ex:
        credential.get_token(scope)

    # the exception should carry the requested scopes and any error message from AAD
    assert ex.value.scopes == (scope,)
    assert ex.value.error_details == expected_details


def test_scopes_round_trip():
    """authenticate should accept the value of AuthenticationRequiredError.scopes"""

    scope = "scope"

    def validate_scopes(*scopes, **_):
        assert scopes == (scope,)
        return REQUEST_TOKEN_RESULT

    request_token = Mock(wraps=validate_scopes)
    credential = MockCredential(_disable_automatic_authentication=True, request_token=request_token)
    with pytest.raises(AuthenticationRequiredError) as ex:
        credential.get_token(scope)

    credential._authenticate(scopes=ex.value.scopes)

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
    MockCredential(authority=authority, request_token=request_token)._authenticate()
    assert request_token.call_count == 1


def test_authenticate_unknown_cloud():
    """authenticate should raise when given no scopes in an unknown cloud"""

    with pytest.raises(CredentialUnavailableError):
        MockCredential(authority="localhost")._authenticate()


@pytest.mark.parametrize("option", (True, False))
def test_authenticate_ignores_disable_automatic_authentication(option):
    """authenticate should prompt for authentication regardless of the credential's configuration"""

    request_token = Mock(return_value=REQUEST_TOKEN_RESULT)
    MockCredential(request_token=request_token, _disable_automatic_authentication=option)._authenticate()
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
    credential = MockCredential(msal_app_factory=lambda *_, **__: msal_app, _authentication_record=record)
    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")

    assert expected_message in ex.value.message
    assert msal_app.acquire_token_silent_with_error.call_count == 1, "credential didn't attempt silent auth"


def test_enable_persistent_cache():
    """the credential should use the persistent cache only when given _enable_persistent_cache=True"""

    class TestCredential(InteractiveCredential):
        def __init__(self, **kwargs):
            super(TestCredential, self).__init__(client_id="...", **kwargs)

        def _request_token(self, *_, **__):
            pass

    in_memory_cache = Mock()

    persistent_cache = "azure.identity._internal.persistent_cache"

    # credential should default to an in memory cache
    raise_when_called = Mock(side_effect=Exception("credential shouldn't attempt to load a persistent cache"))
    with patch(persistent_cache + "._load_persistent_cache", raise_when_called):
        with patch(InteractiveCredential.__module__ + ".msal.TokenCache", lambda: in_memory_cache):
            credential = TestCredential()
            assert credential._cache is in_memory_cache

            # allowing an unencrypted cache doesn't count as opting in to the persistent cache
            credential = TestCredential(_allow_unencrypted_cache=True)
            assert credential._cache is in_memory_cache

    # keyword argument opts in to persistent cache
    with patch(persistent_cache + ".msal_extensions") as mock_extensions:
        TestCredential(_enable_persistent_cache=True)
    assert mock_extensions.PersistedTokenCache.call_count == 1

    # opting in on an unsupported platform raises an exception
    with patch(persistent_cache + ".sys.platform", "commodore64"):
        with pytest.raises(NotImplementedError):
            TestCredential(_enable_persistent_cache=True)
        with pytest.raises(NotImplementedError):
            TestCredential(_enable_persistent_cache=True, _allow_unencrypted_cache=True)


@patch("azure.identity._internal.persistent_cache.sys.platform", "linux2")
@patch("azure.identity._internal.persistent_cache.msal_extensions")
def test_persistent_cache_linux(mock_extensions):
    """The credential should use an unencrypted cache when encryption is unavailable and the user explicitly opts in.

    This test was written when Linux was the only platform on which encryption may not be available.
    """

    class TestCredential(InteractiveCredential):
        def __init__(self, **kwargs):
            super(TestCredential, self).__init__(client_id="...", **kwargs)

        def _request_token(self, *_, **__):
            pass

    # the credential should prefer an encrypted cache even when the user allows an unencrypted one
    TestCredential(_enable_persistent_cache=True, _allow_unencrypted_cache=True)
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.LibsecretPersistence)
    mock_extensions.PersistedTokenCache.reset_mock()

    # (when LibsecretPersistence's dependencies aren't available, constructing it raises ImportError)
    mock_extensions.LibsecretPersistence = Mock(side_effect=ImportError)

    # encryption unavailable, no opt in to unencrypted cache -> credential should raise
    with pytest.raises(ValueError):
        TestCredential(_enable_persistent_cache=True)

    TestCredential(_enable_persistent_cache=True, _allow_unencrypted_cache=True)
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.FilePersistence)


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

    record = TestCredential()._authenticate()
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

    record = TestCredential()._authenticate()
    assert record.authority == authority
    assert record.home_account_id == subject
    assert record.tenant_id == tenant
    assert record.username == username
