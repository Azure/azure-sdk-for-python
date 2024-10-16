# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import (
    AuthenticationRecord,
    AzureAuthorityHosts,
    CredentialUnavailableError,
    SharedTokenCacheCredential,
    TokenCachePersistenceOptions,
)
from azure.identity._constants import DEVELOPER_SIGN_ON_CLIENT_ID, EnvironmentVariables
from azure.identity._internal.shared_token_cache import (
    KNOWN_ALIASES,
    MULTIPLE_ACCOUNTS,
    MULTIPLE_MATCHING_ACCOUNTS,
    NO_ACCOUNTS,
    NO_MATCHING_ACCOUNTS,
)
from azure.identity._internal import get_default_authority, within_dac
from azure.identity._internal.user_agent import USER_AGENT
from msal import TokenCache
import pytest
from urllib.parse import urlparse
from unittest.mock import MagicMock, Mock, patch

from helpers import (
    build_aad_response,
    build_id_token,
    get_discovery_response,
    id_token_claims,
    mock_response,
    msal_validating_transport,
    Request,
    validating_transport,
    GET_TOKEN_METHODS,
)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_close(get_token_method):
    transport = MagicMock()
    credential = SharedTokenCacheCredential(transport=transport, _cache=TokenCache())
    with pytest.raises(CredentialUnavailableError):
        getattr(credential, get_token_method)("scope")

    assert not transport.__enter__.called
    assert not transport.__exit__.called

    credential.close()
    assert not transport.__enter__.called
    assert transport.__exit__.call_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_context_manager(get_token_method):
    transport = MagicMock()
    credential = SharedTokenCacheCredential(transport=transport, _cache=TokenCache())
    with pytest.raises(CredentialUnavailableError):
        getattr(credential, get_token_method)("scope")

    assert not transport.__enter__.called
    assert not transport.__exit__.called

    with credential:
        assert transport.__enter__.call_count == 1
        assert not transport.__exit__.called

    assert transport.__enter__.call_count == 1
    assert transport.__exit__.call_count == 1


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        record = AuthenticationRecord(tenant, "client-id", "authority", "home.account.id", "username")
        SharedTokenCacheCredential(authentication_record=record)
        SharedTokenCacheCredential(authentication_record=record, tenant_id=tenant)

    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        record = AuthenticationRecord(tenant, "client-id", "authority", "home.account.id", "username")
        with pytest.raises(ValueError):
            SharedTokenCacheCredential(authentication_record=record)
        with pytest.raises(ValueError):
            SharedTokenCacheCredential(authentication_record=record, tenant_id=tenant)


def test_supported():
    """the cache is supported on Linux, macOS, Windows, so this should pass unless you're developing on e.g. FreeBSD"""
    assert SharedTokenCacheCredential.supported()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_scopes(get_token_method):
    """The credential should raise when get_token is called with no scopes"""

    credential = SharedTokenCacheCredential(_cache=TokenCache())
    with pytest.raises(ValueError):
        getattr(credential, get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_policies_configurable(get_token_method):
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    def send(*_, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = SharedTokenCacheCredential(
        _cache=populated_cache(get_account_event("test@user", "uid", "utid")),
        policies=[policy],
        transport=Mock(send=send),
    )

    getattr(credential, get_token_method)("scope")

    assert policy.on_request.called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_user_agent(get_token_method):
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = SharedTokenCacheCredential(
        _cache=populated_cache(get_account_event("test@user", "uid", "utid")), transport=transport
    )

    getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_tenant_id(get_token_method):
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = SharedTokenCacheCredential(
        _cache=populated_cache(get_account_event("test@user", "uid", "utid")),
        transport=transport,
        additionally_allowed_tenants=["*"],
    )

    kwargs = {"tenant_id": "tenant_id"}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}

    getattr(credential, get_token_method)("scope", **kwargs)


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    class MockCredential(SharedTokenCacheCredential):
        def _get_auth_client(self, authority=None, **kwargs):
            actual = urlparse(authority)
            assert actual.scheme == "https"
            assert actual.netloc == expected_netloc

    transport = Mock(send=Mock(side_effect=Exception("credential shouldn't send a request")))
    MockCredential(_cache=TokenCache(), authority=authority, transport=transport)

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        MockCredential(_cache=TokenCache(), authority=authority, transport=transport)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_empty_cache(get_token_method):
    """the credential should raise CredentialUnavailableError when the cache is empty"""

    with pytest.raises(CredentialUnavailableError, match=NO_ACCOUNTS):
        getattr(SharedTokenCacheCredential(_cache=TokenCache()), get_token_method)("scope")
    with pytest.raises(CredentialUnavailableError, match=NO_ACCOUNTS):
        getattr(SharedTokenCacheCredential(_cache=TokenCache(), username="not@cache"), get_token_method)("scope")
    with pytest.raises(CredentialUnavailableError, match=NO_ACCOUNTS):
        getattr(SharedTokenCacheCredential(_cache=TokenCache(), tenant_id="not-cached"), get_token_method)("scope")
    with pytest.raises(CredentialUnavailableError, match=NO_ACCOUNTS):
        getattr(
            SharedTokenCacheCredential(_cache=TokenCache(), tenant_id="not-cached", username="not@cache"),
            get_token_method,
        )("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_matching_account_for_username(get_token_method):
    """one cached account, username specified, username doesn't match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant, refresh_token="refresh-token")
    cache = populated_cache(account)

    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(SharedTokenCacheCredential(_cache=cache, username="not" + upn), get_token_method)("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    assert "not" + upn in ex.value.message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_matching_account_for_tenant(get_token_method):
    """one cached account, tenant specified, tenant doesn't match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant, refresh_token="refresh-token")
    cache = populated_cache(account)

    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(SharedTokenCacheCredential(_cache=cache, tenant_id="not-" + tenant), get_token_method)("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    assert "not-" + tenant in ex.value.message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_matching_account_for_tenant_and_username(get_token_method):
    """one cached account, tenant and username specified, neither match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant, refresh_token="refresh-token")
    cache = populated_cache(account)

    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(
            SharedTokenCacheCredential(_cache=cache, tenant_id="not-" + tenant, username="not" + upn), get_token_method
        )("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    assert "not" + upn in ex.value.message and "not-" + tenant in ex.value.message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_matching_account_for_tenant_or_username(get_token_method):
    """two cached accounts, username and tenant specified, one account matches each -> credential should raise"""

    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"
    upn_a = "a@foo"
    upn_b = "b@foo"
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid=tenant_a, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn_b, uid="uid_b", utid=tenant_b, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    transport = Mock(side_effect=Exception())  # credential shouldn't use the network

    credential = SharedTokenCacheCredential(username=upn_a, tenant_id=tenant_b, _cache=cache, transport=transport)
    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(credential, get_token_method)("scope")
    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    assert upn_a in ex.value.message and tenant_b in ex.value.message

    credential = SharedTokenCacheCredential(username=upn_b, tenant_id=tenant_a, _cache=cache, transport=transport)
    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(credential, get_token_method)("scope")
    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    assert upn_b in ex.value.message and tenant_a in ex.value.message


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_single_account_matching_username(get_token_method):
    """one cached account, username specified, username matches -> credential should auth that account"""

    upn = "spam@eggs"
    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid="utid", username=upn, refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, username=upn)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_single_account_matching_tenant(get_token_method):
    """one cached account, tenant specified, tenant matches -> credential should auth that account"""

    tenant_id = "tenant-id"
    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid=tenant_id, username="spam@eggs", refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, tenant_id=tenant_id)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_single_account_matching_tenant_and_username(get_token_method):
    """one cached account, tenant and username specified, both match -> credential should auth that account"""

    upn = "spam@eggs"
    tenant_id = "tenant-id"
    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid=tenant_id, username=upn, refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, tenant_id=tenant_id, username=upn)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_single_account(get_token_method):
    """one cached account, no username specified -> credential should auth that account"""

    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid="utid", username="spam@eggs", refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)

    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_refresh_token(get_token_method):
    """one cached account, account has no refresh token -> credential should raise"""

    account = get_account_event(uid="uid_a", utid="utid", username="spam@eggs", refresh_token=None)
    cache = populated_cache(account)

    transport = Mock(side_effect=Exception())  # credential shouldn't use the network

    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)
    with pytest.raises(CredentialUnavailableError, match=NO_ACCOUNTS):
        getattr(credential, get_token_method)("scope")

    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, username="not@cache")
    with pytest.raises(CredentialUnavailableError, match=NO_ACCOUNTS):
        getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_two_accounts_no_username_or_tenant(get_token_method):
    """two cached accounts, no username or tenant specified -> credential should raise"""

    upn_a = "a@foo"
    upn_b = "b@foo"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid="utid")
    account_b = get_account_event(username=upn_b, uid="uid_b", utid="utid")
    cache = populated_cache(account_a, account_b)

    # credential can't select an identity => it shouldn't use the network
    transport = Mock(side_effect=Exception())

    # two users in the cache, no username specified -> CredentialUnavailableError
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)
    with pytest.raises(ClientAuthenticationError, match=MULTIPLE_ACCOUNTS) as ex:
        getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_two_accounts_username_specified(get_token_method):
    """two cached accounts, username specified, one account matches -> credential should auth that account"""

    scope = "scope"
    expected_refresh_token = "refresh-token-a"
    upn_a = "a@foo"
    upn_b = "b@foo"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid="utid", refresh_token=expected_refresh_token)
    account_b = get_account_event(username=upn_b, uid="uid_b", utid="utid", refresh_token="refresh_token_b")
    cache = populated_cache(account_a, account_b)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(username=upn_a, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_two_accounts_tenant_specified(get_token_method):
    """two cached accounts, tenant specified, one account matches -> credential should auth that account"""

    scope = "scope"
    expected_refresh_token = "refresh-token-a"
    upn_a = "a@foo"
    upn_b = "b@foo"
    tenant_id = "tenant-id"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid=tenant_id, refresh_token=expected_refresh_token)
    account_b = get_account_event(username=upn_b, uid="uid_b", utid="utid", refresh_token="refresh_token_b")
    cache = populated_cache(account_a, account_b)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_id, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_two_accounts_tenant_and_username_specified(get_token_method):
    """two cached accounts, tenant and username specified, one account matches both -> credential should auth that account"""

    scope = "scope"
    expected_refresh_token = "refresh-token-a"
    upn_a = "a@foo"
    upn_b = "b@foo"
    tenant_id = "tenant-id"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid=tenant_id, refresh_token=expected_refresh_token)
    account_b = get_account_event(username=upn_b, uid="uid_b", utid="utid", refresh_token="refresh_token_b")
    cache = populated_cache(account_a, account_b)

    expected_token = "***"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_id, username=upn_a, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_same_username_different_tenants(get_token_method):
    """two cached accounts, same username, different tenants"""

    access_token_a = "access-token-a"
    access_token_b = "access-token-b"
    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"

    upn = "spam@eggs"
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    account_a = get_account_event(username=upn, uid="another-guid", utid=tenant_a, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn, uid="more-guid", utid=tenant_b, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    # with no tenant specified the credential can't select an identity
    transport = Mock(side_effect=Exception())  # (so it shouldn't use the network)
    credential = SharedTokenCacheCredential(username=upn, _cache=cache, transport=transport)
    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(credential, get_token_method)("scope")

    assert ex.value.message.startswith(MULTIPLE_MATCHING_ACCOUNTS[: MULTIPLE_MATCHING_ACCOUNTS.index("{")])
    assert upn in ex.value.message

    # with tenant specified, the credential should auth the matching account
    scope = "scope"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_a, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_a, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == access_token_a

    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_b, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_b))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_b, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == access_token_b


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_same_tenant_different_usernames(get_token_method):
    """two cached accounts, same tenant, different usernames"""

    access_token_a = "access-token-a"
    access_token_b = "access-token-b"
    refresh_token_a = "refresh-token-a"
    refresh_token_b = "refresh-token-b"

    upn_a = "spam@eggs"
    upn_b = "eggs@spam"
    tenant_id = "the-tenant"
    account_a = get_account_event(username=upn_a, uid="another-guid", utid=tenant_id, refresh_token=refresh_token_a)
    account_b = get_account_event(username=upn_b, uid="more-guid", utid=tenant_id, refresh_token=refresh_token_b)
    cache = populated_cache(account_a, account_b)

    # with no username specified the credential can't select an identity
    transport = Mock(side_effect=Exception())  # (so it shouldn't use the network)
    credential = SharedTokenCacheCredential(tenant_id=tenant_id, _cache=cache, transport=transport)
    with pytest.raises(CredentialUnavailableError) as ex:
        getattr(credential, get_token_method)("scope")

    assert ex.value.message.startswith(MULTIPLE_MATCHING_ACCOUNTS[: MULTIPLE_MATCHING_ACCOUNTS.index("{")])
    assert tenant_id in ex.value.message

    # with a username specified, the credential should auth the matching account
    scope = "scope"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_b, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))],
    )
    credential = SharedTokenCacheCredential(username=upn_b, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == access_token_a

    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_a, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))],
    )
    credential = SharedTokenCacheCredential(username=upn_a, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == access_token_a


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authority_aliases(get_token_method):
    """the credential should use a refresh token valid for any known alias of its authority"""

    expected_access_token = "access-token"

    for authority in KNOWN_ALIASES:
        # cache a token for this authority
        expected_refresh_token = authority.replace(".", "")
        account = get_account_event(
            "spam@eggs", "uid", "tenant", authority=authority, refresh_token=expected_refresh_token
        )
        cache = populated_cache(account)

        # the token should be acceptable for this authority itself
        transport = validating_transport(
            requests=[Request(authority=authority, required_data={"refresh_token": expected_refresh_token})],
            responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
        )
        credential = SharedTokenCacheCredential(authority=authority, _cache=cache, transport=transport)
        token = getattr(credential, get_token_method)("scope")
        assert token.token == expected_access_token

        # it should be acceptable for every known alias of this authority
        for alias in KNOWN_ALIASES[authority]:
            transport = validating_transport(
                requests=[Request(authority=alias, required_data={"refresh_token": expected_refresh_token})],
                responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
            )
            credential = SharedTokenCacheCredential(authority=alias, _cache=cache, transport=transport)
            token = getattr(credential, get_token_method)("scope")
            assert token.token == expected_access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authority_with_no_known_alias(get_token_method):
    """given an appropriate token, an authority with no known aliases should work"""

    authority = "unknown.authority"
    expected_access_token = "access-token"
    expected_refresh_token = "refresh-token"
    account = get_account_event("spam@eggs", "uid", "tenant", authority=authority, refresh_token=expected_refresh_token)
    cache = populated_cache(account)
    transport = validating_transport(
        requests=[Request(authority=authority, required_data={"refresh_token": expected_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )
    credential = SharedTokenCacheCredential(authority=authority, _cache=cache, transport=transport)
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authority_environment_variable(get_token_method):
    """the credential should accept an authority by environment variable when none is otherwise specified"""

    authority = "localhost"
    expected_access_token = "access-token"
    expected_refresh_token = "refresh-token"
    account = get_account_event("spam@eggs", "uid", "tenant", authority=authority, refresh_token=expected_refresh_token)
    cache = populated_cache(account)
    transport = validating_transport(
        requests=[Request(authority=authority, required_data={"refresh_token": expected_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = SharedTokenCacheCredential(transport=transport, _cache=cache)
    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authentication_record_empty_cache(get_token_method):
    record = AuthenticationRecord("tenant-id", "client_id", "authority", "home_account_id", "username")

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        # expecting only MSAL discovery requests
        assert request.method == "GET"
        return get_discovery_response()

    credential = SharedTokenCacheCredential(
        authentication_record=record, transport=Mock(send=send), _cache=TokenCache()
    )

    with pytest.raises(CredentialUnavailableError):
        getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authentication_record_no_match(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    authority = "localhost"
    object_id = "object-id"
    home_account_id = object_id + "." + tenant_id
    username = "me"
    record = AuthenticationRecord(tenant_id, client_id, authority, home_account_id, username)

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        # expecting only MSAL discovery requests
        assert request.method == "GET"
        return get_discovery_response()

    cache = populated_cache(
        get_account_event(
            "not-" + username,
            "not-" + object_id,
            "different-" + tenant_id,
            client_id="not-" + client_id,
        ),
    )
    credential = SharedTokenCacheCredential(authentication_record=record, transport=Mock(send=send), _cache=cache)

    with pytest.raises(CredentialUnavailableError):
        getattr(credential, get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authentication_record(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    authority = "localhost"
    object_id = "object-id"
    home_account_id = object_id + "." + tenant_id
    username = "me"
    record = AuthenticationRecord(tenant_id, client_id, authority, home_account_id, username)

    expected_access_token = "****"
    expected_refresh_token = "**"
    account = get_account_event(
        username, object_id, tenant_id, authority=authority, client_id=client_id, refresh_token=expected_refresh_token
    )
    cache = populated_cache(account)

    transport = msal_validating_transport(
        endpoint="https://{}/{}".format(authority, tenant_id),
        requests=[Request(authority=authority, required_data={"refresh_token": expected_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )
    credential = SharedTokenCacheCredential(authentication_record=record, transport=transport, _cache=cache)

    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_auth_record_multiple_accounts_for_username(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    authority = "localhost"
    object_id = "object-id"
    home_account_id = object_id + "." + tenant_id
    username = "me"
    record = AuthenticationRecord(tenant_id, client_id, authority, home_account_id, username)

    expected_access_token = "****"
    expected_refresh_token = "**"
    expected_account = get_account_event(
        username, object_id, tenant_id, authority=authority, client_id=client_id, refresh_token=expected_refresh_token
    )
    cache = populated_cache(
        expected_account,
        get_account_event(  # this account matches all but the record's tenant
            username,
            object_id,
            "different-" + tenant_id,
            authority=authority,
            client_id=client_id,
            refresh_token="not-" + expected_refresh_token,
        ),
    )

    transport = msal_validating_transport(
        endpoint="https://{}/{}".format(authority, tenant_id),
        requests=[Request(authority=authority, required_data={"refresh_token": expected_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )
    credential = SharedTokenCacheCredential(authentication_record=record, transport=transport, _cache=cache)

    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_access_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_writes_to_cache(get_token_method):
    """the credential should write tokens it acquires to the cache"""

    scope = "scope"
    expected_access_token = "access token"
    first_refresh_token = "first refresh token"
    second_refresh_token = "second refresh token"

    username = "me"
    uid = "uid"
    utid = "utid"
    account = get_account_event(username=username, uid=uid, utid=utid, refresh_token=first_refresh_token)
    cache = TokenCache()
    cache.add(account)

    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": first_refresh_token})],  # credential redeems refresh token
        responses=[
            mock_response(
                json_payload=build_aad_response(  # Microsoft Entra ID responds with an access token and new refresh token
                    uid=uid,
                    utid=utid,
                    access_token=expected_access_token,
                    refresh_token=second_refresh_token,
                    id_token=build_id_token(
                        aud=DEVELOPER_SIGN_ON_CLIENT_ID, object_id=uid, tenant_id=utid, username=username
                    ),
                )
            )
        ],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_access_token

    # access token should be in the cache, and another instance should retrieve it
    credential = SharedTokenCacheCredential(
        _cache=cache, transport=Mock(send=Mock(side_effect=Exception("the credential should return a cached token")))
    )
    token = getattr(credential, get_token_method)(scope)
    assert token.token == expected_access_token

    # and the credential should have updated the cached refresh token
    second_access_token = "second access token"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": second_refresh_token})],
        responses=[mock_response(json_payload=build_aad_response(access_token=second_access_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)
    token = getattr(credential, get_token_method)("some other " + scope)
    assert token.token == second_access_token

    # verify the credential didn't add a new cache entry
    assert len(list(cache.search(TokenCache.CredentialType.REFRESH_TOKEN))) == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_initialization(get_token_method):
    """the credential should attempt to load the cache when it's needed and no cache has been established."""

    with patch("azure.identity._internal.shared_token_cache._load_persistent_cache") as mock_cache_loader:
        mock_cache_loader.side_effect = Exception("it didn't work")

        credential = SharedTokenCacheCredential()
        assert mock_cache_loader.call_count == 0

        with pytest.raises(CredentialUnavailableError, match="Shared token cache unavailable"):
            getattr(credential, get_token_method)("scope")
        assert mock_cache_loader.call_count == 1

        with pytest.raises(CredentialUnavailableError, match="Shared token cache unavailable"):
            getattr(credential, get_token_method)("scope")
        assert mock_cache_loader.call_count == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_initialization_with_cache_options(get_token_method):
    """the credential should use user-supplied persistence options"""

    with patch("azure.identity._internal.shared_token_cache._load_persistent_cache") as mock_cache_loader:
        options = TokenCachePersistenceOptions(name="foo.cache")
        credential = SharedTokenCacheCredential(cache_persistence_options=options)

        with pytest.raises(CredentialUnavailableError):
            getattr(credential, get_token_method)("scope")
        assert mock_cache_loader.call_count == 1
        args, _ = mock_cache_loader.call_args
        assert args[0] == options
        assert args[1] is False  # is_cae is False.

        with pytest.raises(CredentialUnavailableError):
            kwargs = {"enable_cae": True}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            getattr(credential, get_token_method)("scope", **kwargs)
        assert mock_cache_loader.call_count == 2
        args, _ = mock_cache_loader.call_args
        assert args[0] == options
        assert args[1] is True  # is_cae is True.


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_authentication_record_authenticating_tenant(get_token_method):
    """when given a record and 'tenant_id', the credential should authenticate in the latter"""

    expected_tenant_id = "tenant-id"
    record = AuthenticationRecord("not- " + expected_tenant_id, "...", "localhost", "...", "...")

    def mock_send(request, **_):
        if not request.body:
            return get_discovery_response()
        assert request.url.startswith("https://localhost/" + expected_tenant_id)
        return mock_response(json_payload=build_aad_response(access_token="*"))

    transport = Mock(send=Mock(wraps=mock_send))
    credential = SharedTokenCacheCredential(
        authentication_record=record, _cache=TokenCache(), tenant_id=expected_tenant_id, transport=transport
    )
    with pytest.raises(CredentialUnavailableError):
        getattr(credential, get_token_method)("scope")  # this raises because the cache is empty

    assert transport.send.called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_client_capabilities(get_token_method):
    """the credential should configure MSAL for capability CP1 only if enable_cae is passed."""

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        # expecting only the discovery requests triggered by creating an msal.PublicClientApplication
        # because the cache is empty--the credential shouldn't send a token request
        return get_discovery_response("https://localhost/tenant")

    record = AuthenticationRecord("tenant-id", "client_id", "authority", "home_account_id", "username")
    transport = Mock(send=send)
    credential = SharedTokenCacheCredential(transport=transport, authentication_record=record, _cache=TokenCache())

    with patch("azure.identity._credentials.silent.PublicClientApplication") as PublicClientApplication:
        with pytest.raises(ClientAuthenticationError):  # (cache is empty)
            getattr(credential, get_token_method)("scope")

        assert PublicClientApplication.call_count == 1
        _, kwargs = PublicClientApplication.call_args
        assert kwargs["client_capabilities"] is None

        with pytest.raises(ClientAuthenticationError):
            kwargs = {"enable_cae": True}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            getattr(credential, get_token_method)("scope", **kwargs)
        assert PublicClientApplication.call_count == 2
        _, kwargs = PublicClientApplication.call_args
        assert kwargs["client_capabilities"] == ["CP1"]


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_within_dac_error(get_token_method):
    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        # expecting only the discovery requests triggered by creating an msal.PublicClientApplication
        # because the cache is empty--the credential shouldn't send a token request
        return get_discovery_response("https://localhost/tenant")

    record = AuthenticationRecord("tenant-id", "client_id", "authority", "home_account_id", "username")
    transport = Mock(send=send)
    credential = SharedTokenCacheCredential(transport=transport, authentication_record=record, _cache=TokenCache())
    within_dac.set(True)
    with patch("azure.identity._credentials.silent.PublicClientApplication") as PublicClientApplication:
        with pytest.raises(CredentialUnavailableError):  # (cache is empty)
            getattr(credential, get_token_method)("scope")
    within_dac.set(False)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_claims_challenge(get_token_method):
    """get_token should pass any claims challenge to MSAL token acquisition APIs"""

    expected_claims = '{"access_token": {"essential": "true"}'

    record = AuthenticationRecord("tenant-id", "client_id", "authority", "home_account_id", "username")

    msal_app = Mock()
    msal_app.get_accounts.return_value = [{"home_account_id": record.home_account_id}]
    msal_app.acquire_token_silent_with_error.return_value = dict(
        build_aad_response(access_token="**", id_token=build_id_token())
    )

    transport = Mock(send=Mock(side_effect=Exception("this test mocks MSAL, so no request should be sent")))
    credential = SharedTokenCacheCredential(transport=transport, authentication_record=record, _cache=TokenCache())
    with patch("azure.identity._credentials.silent.PublicClientApplication", lambda *_, **__: msal_app):
        kwargs = {"claims": expected_claims}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        getattr(credential, get_token_method)("scope", **kwargs)

    assert msal_app.acquire_token_silent_with_error.call_count == 1
    args, kwargs = msal_app.acquire_token_silent_with_error.call_args
    assert kwargs["claims_challenge"] == expected_claims


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication(get_token_method):
    default_tenant = "organizations"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant_id = parsed.path.split("/")[1]
        assert tenant_id in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant_id)
        return mock_response(
            json_payload=build_aad_response(
                access_token=second_token if tenant_id == second_tenant else first_token,
                id_token_claims=id_token_claims(aud="...", iss="...", sub="..."),
            )
        )

    authority = AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    expected_account = get_account_event(
        "user", "object-id", "tenant-id", authority=authority, client_id="client-id", refresh_token="**"
    )
    cache = populated_cache(expected_account)

    credential = SharedTokenCacheCredential(
        authority=authority, transport=Mock(send=send), _cache=cache, additionally_allowed_tenants=["*"]
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == first_token

    kwargs = {"tenant_id": default_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == first_token

    kwargs = {"tenant_id": second_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == second_token

    # should still default to the first tenant
    token = getattr(credential, get_token_method)("scope")
    assert token.token == first_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication_auth_record(get_token_method):
    default_tenant = "organizations"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    authority = AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
    object_id = "object-id"
    home_account_id = object_id + "." + default_tenant
    record = AuthenticationRecord(default_tenant, "client-id", authority, home_account_id, "user")

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant_id = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in request.url:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant_id))

        assert tenant_id in (default_tenant, second_tenant), 'unexpected tenant "{}"'.format(tenant_id)
        return mock_response(
            json_payload=build_aad_response(
                access_token=second_token if tenant_id == second_tenant else first_token,
                id_token_claims=id_token_claims(aud="...", iss="...", sub="..."),
            )
        )

    expected_account = get_account_event(
        record.username, object_id, record.tenant_id, client_id=record.client_id, refresh_token="**"
    )
    cache = populated_cache(expected_account)

    credential = SharedTokenCacheCredential(
        authority=authority,
        transport=Mock(send=send),
        authentication_record=record,
        _cache=cache,
        additionally_allowed_tenants=["*"],
    )
    token = getattr(credential, get_token_method)("scope")
    assert token.token == first_token

    kwargs = {"tenant_id": default_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == first_token

    kwargs = {"tenant_id": second_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == second_token

    # should still default to the first tenant
    token = getattr(credential, get_token_method)("scope")
    assert token.token == first_token


def get_account_event(
    username, uid, utid, authority=None, client_id="client-id", refresh_token="refresh-token", scopes=None, **kwargs
):
    if authority:
        endpoint = "https://" + "/".join((authority, utid, "path"))
    else:
        endpoint = get_default_authority() + "/{}/{}".format(utid, "path")

    return {
        "response": build_aad_response(
            uid=uid,
            utid=utid,
            refresh_token=refresh_token,
            id_token=build_id_token(aud=client_id, username=username),
            foci="1",
            **kwargs
        ),
        "client_id": client_id,
        "token_endpoint": endpoint,
        "scope": scopes or ["scope"],
    }


def populated_cache(*accounts):
    cache = TokenCache()
    for account in accounts:
        cache.add(account)
    cache.add = lambda *_, **__: None  # prevent anything being added to the cache
    return cache


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication_not_allowed(get_token_method):
    default_tenant = "organizations"
    expected_token = "***"

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant_id = parsed.path.split("/")[1]
        assert tenant_id == default_tenant
        return mock_response(
            json_payload=build_aad_response(
                access_token=expected_token,
                id_token_claims=id_token_claims(aud="...", iss="...", sub="..."),
            )
        )

    tenant_id = "tenant-id"
    client_id = "client-id"
    authority = "localhost"
    object_id = "object-id"
    username = "me"

    expected_account = get_account_event(
        username, object_id, tenant_id, authority=authority, client_id=client_id, refresh_token="**"
    )
    cache = populated_cache(expected_account)

    credential = SharedTokenCacheCredential(authority=authority, transport=Mock(send=send), _cache=cache)

    token = getattr(credential, get_token_method)("scope")
    assert token.token == expected_token

    kwargs = {"tenant_id": default_tenant}
    if get_token_method == "get_token_info":
        kwargs = {"options": kwargs}
    token = getattr(credential, get_token_method)("scope", **kwargs)
    assert token.token == expected_token

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
        kwargs = {"tenant_id": "some_tenant"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)("scope", **kwargs)
        assert token.token == expected_token
