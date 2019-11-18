# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import KnownAuthorities
from azure.identity.aio import SharedTokenCacheCredential
from azure.identity._internal.shared_token_cache import (
    MULTIPLE_ACCOUNTS,
    MULTIPLE_MATCHING_ACCOUNTS,
    NO_ACCOUNTS,
    NO_MATCHING_ACCOUNTS,
)
from msal import TokenCache
import pytest

from helpers import async_validating_transport, build_aad_response, build_id_token, mock_response, Request


@pytest.mark.asyncio
async def test_empty_cache():
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        await SharedTokenCacheCredential(_cache=TokenCache()).get_token("scope")
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        await SharedTokenCacheCredential(_cache=TokenCache(), username="not@cache").get_token("scope")
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        await SharedTokenCacheCredential(_cache=TokenCache(), tenant_id="not-cached").get_token("scope")
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        await SharedTokenCacheCredential(_cache=TokenCache(), tenant_id="not-cached", username="not@cache").get_token("scope")


@pytest.mark.asyncio
async def test_no_matching_account_for_username():
    """one cached account, username specified, username doesn't match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant, refresh_token="refresh-token")
    cache = populated_cache(account)

    with pytest.raises(ClientAuthenticationError) as ex:
        await SharedTokenCacheCredential(_cache=cache, username="not" + upn).get_token("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert upn in discovered_accounts and tenant in discovered_accounts


@pytest.mark.asyncio
async def test_no_matching_account_for_tenant():
    """one cached account, tenant specified, tenant doesn't match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant, refresh_token="refresh-token")
    cache = populated_cache(account)

    with pytest.raises(ClientAuthenticationError) as ex:
        await SharedTokenCacheCredential(_cache=cache, tenant_id="not-" + tenant).get_token("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert upn in discovered_accounts and tenant in discovered_accounts


@pytest.mark.asyncio
async def test_no_matching_account_for_tenant_and_username():
    """one cached account, tenant and username specified, neither match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant, refresh_token="refresh-token")
    cache = populated_cache(account)

    with pytest.raises(ClientAuthenticationError) as ex:
        await SharedTokenCacheCredential(_cache=cache, tenant_id="not-" + tenant, username="not" + upn).get_token("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert upn in discovered_accounts and tenant in discovered_accounts


@pytest.mark.asyncio
async def test_no_matching_account_for_tenant_or_username():
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
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert all(s in discovered_accounts for s in (upn_a, upn_b, tenant_a, tenant_b))

    credential = SharedTokenCacheCredential(username=upn_b, tenant_id=tenant_a, _cache=cache, transport=transport)
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert all(s in discovered_accounts for s in (upn_a, upn_b, tenant_a, tenant_b))


@pytest.mark.asyncio
async def test_single_account_matching_username():
    """one cached account, username specified, username matches -> credential should auth that account"""

    upn = "spam@eggs"
    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid="utid", username=upn, refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, username=upn)
    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_single_account_matching_tenant():
    """one cached account, tenant specified, tenant matches -> credential should auth that account"""

    tenant_id = "tenant-id"
    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid=tenant_id, username="spam@eggs", refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, tenant_id=tenant_id)
    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_single_account_matching_tenant_and_username():
    """one cached account, tenant and username specified, both match -> credential should auth that account"""

    upn = "spam@eggs"
    tenant_id = "tenant-id"
    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid=tenant_id, username=upn, refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, tenant_id=tenant_id, username=upn)
    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_single_account():
    """one cached account, no username specified -> credential should auth that account"""

    refresh_token = "refresh-token"
    scope = "scope"
    account = get_account_event(uid="uid_a", utid="utid", username="spam@eggs", refresh_token=refresh_token)
    cache = populated_cache(account)

    expected_token = "***"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)

    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_no_refresh_token():
    """one cached account, account has no refresh token -> credential should raise"""

    account = get_account_event(uid="uid_a", utid="utid", username="spam@eggs", refresh_token=None)
    cache = populated_cache(account)

    transport = Mock(side_effect=Exception())  # credential shouldn't use the network

    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        await credential.get_token("scope")

    credential = SharedTokenCacheCredential(_cache=cache, transport=transport, username="not@cache")
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        await credential.get_token("scope")


@pytest.mark.asyncio
async def test_two_accounts_no_username_or_tenant():
    """two cached accounts, no username or tenant specified -> credential should raise"""

    upn_a = "a@foo"
    upn_b = "b@foo"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid="utid")
    account_b = get_account_event(username=upn_b, uid="uid_b", utid="utid")
    cache = populated_cache(account_a, account_b)

    # credential can't select an identity => it shouldn't use the network
    transport = Mock(side_effect=Exception())

    # two users in the cache, no username specified -> ClientAuthenticationError
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")

    # error message should mention multiple accounts and list usernames in the cache
    assert upn_a in ex.value.message and upn_b in ex.value.message
    assert ex.value.message.splitlines()[:-1] == MULTIPLE_ACCOUNTS.splitlines()[:-1]


@pytest.mark.asyncio
async def test_two_accounts_username_specified():
    """two cached accounts, username specified, one account matches -> credential should auth that account"""

    scope = "scope"
    expected_refresh_token = "refresh-token-a"
    upn_a = "a@foo"
    upn_b = "b@foo"
    account_a = get_account_event(username=upn_a, uid="uid_a", utid="utid", refresh_token=expected_refresh_token)
    account_b = get_account_event(username=upn_b, uid="uid_b", utid="utid", refresh_token="refresh_token_b")
    cache = populated_cache(account_a, account_b)

    expected_token = "***"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(username=upn_a, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_two_accounts_tenant_specified():
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
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_id, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_two_accounts_tenant_and_username_specified():
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
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_token))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_id, username=upn_a, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == expected_token


@pytest.mark.asyncio
async def test_same_username_different_tenants():
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
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    # error message should indicate multiple matching accounts, and list discovered accounts
    assert ex.value.message.startswith(MULTIPLE_MATCHING_ACCOUNTS[: MULTIPLE_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert discovered_accounts.count(upn) == 2
    assert tenant_a in discovered_accounts and tenant_b in discovered_accounts

    # with tenant specified, the credential should auth the matching account
    scope = "scope"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_a, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_a, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == access_token_a

    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_b, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_b))],
    )
    credential = SharedTokenCacheCredential(tenant_id=tenant_b, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == access_token_b


@pytest.mark.asyncio
async def test_same_tenant_different_usernames():
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
    with pytest.raises(ClientAuthenticationError) as ex:
        await credential.get_token("scope")
    # error message should indicate multiple matching accounts, and list discovered accounts
    assert ex.value.message.startswith(MULTIPLE_MATCHING_ACCOUNTS[: MULTIPLE_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert discovered_accounts.count(tenant_id) == 2
    assert upn_a in discovered_accounts and upn_b in discovered_accounts

    # with a username specified, the credential should auth the matching account
    scope = "scope"
    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_b, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))],
    )
    credential = SharedTokenCacheCredential(username=upn_b, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == access_token_a

    transport = async_validating_transport(
        requests=[Request(required_data={"refresh_token": refresh_token_a, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))],
    )
    credential = SharedTokenCacheCredential(username=upn_a, _cache=cache, transport=transport)
    token = await credential.get_token(scope)
    assert token.token == access_token_a


def get_account_event(
    username,
    uid,
    utid,
    authority=KnownAuthorities.AZURE_PUBLIC_CLOUD,
    client_id="client-id",
    refresh_token="refresh-token",
    scopes=None,
):
    return {
        "response": build_aad_response(
            uid=uid,
            utid=utid,
            refresh_token=refresh_token,
            id_token=build_id_token(aud=client_id, preferred_username=username),
            foci="1",
        ),
        "client_id": client_id,
        "token_endpoint": "https://" + "/".join((authority, utid, "/path")),
        "scope": scopes or ["scope"],
    }


def populated_cache(*accounts):
    cache = TokenCache()
    for account in accounts:
        cache.add(account)
    return cache
