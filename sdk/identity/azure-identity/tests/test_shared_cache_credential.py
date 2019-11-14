# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import KnownAuthorities, SharedTokenCacheCredential
from azure.identity._credentials.shared_cache import (
    MULTIPLE_ACCOUNTS,
    MULTIPLE_MATCHING_ACCOUNTS,
    NO_ACCOUNTS,
    NO_MATCHING_ACCOUNTS,
    NO_TOKEN,
)
from msal import TokenCache
import pytest

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from helpers import build_aad_response, build_id_token, mock_response, Request, validating_transport


def test_empty_cache():
    with pytest.raises(ClientAuthenticationError, match=NO_ACCOUNTS):
        SharedTokenCacheCredential(_cache=TokenCache()).get_token("scope")


def test_no_matching_account():
    """one cached account, username specified, username doesn't match -> credential should raise"""

    upn = "spam@eggs"
    tenant = "some-guid"
    account = get_account_event(username=upn, uid="uid", utid=tenant)
    cache = populated_cache(account)

    with pytest.raises(ClientAuthenticationError) as ex:
        SharedTokenCacheCredential(_cache=cache, username="not" + upn).get_token("scope")

    assert ex.value.message.startswith(NO_MATCHING_ACCOUNTS[: NO_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert upn in discovered_accounts and tenant in discovered_accounts


def test_single_matching_account():
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
    token = credential.get_token(scope)
    assert token.token == expected_token


def test_single_account():
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

    token = credential.get_token(scope)
    assert token.token == expected_token


def test_no_refresh_token():
    """one cached account, account has no refresh token -> credential should raise"""

    account = get_account_event(uid="uid_a", utid="utid", username="spam@eggs", refresh_token=None)
    cache = populated_cache(account)

    # credential has no refresh token to redeem => it shouldn't use the network
    transport = Mock(side_effect=Exception())
    credential = SharedTokenCacheCredential(_cache=cache, transport=transport)

    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")
    assert ex.value.message.startswith(NO_TOKEN[: NO_TOKEN.index("{")])


def test_two_accounts_username_unspecified():
    """two cached accounts, no username specified -> credential should raise"""

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
        credential.get_token("scope")

    # error message should mention multiple accounts and list usernames in the cache
    assert upn_a in ex.value.message and upn_b in ex.value.message
    assert ex.value.message.splitlines()[:-1] == MULTIPLE_ACCOUNTS.splitlines()[:-1]


def test_two_accounts_username_specified():
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
    token = credential.get_token(scope)
    assert token.token == expected_token


def test_same_username_different_tenants():
    """two cached accounts, same username, different tenants"""

    expected_access_token = "***"
    expected_refresh_token = "refresh-token"

    upn = "spam@eggs"
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    uid = "some-guid"
    account_a = get_account_event(username=upn, uid=uid, utid=tenant_a, refresh_token="refresh_token")
    account_b = get_account_event(username=upn, uid=uid, utid=tenant_b, refresh_token=expected_refresh_token)
    cache = populated_cache(account_a, account_b)

    # with no tenant specified the credential can't select an identity
    transport = Mock(side_effect=Exception())  # (so it shouldn't use the network)
    credential = SharedTokenCacheCredential(username=upn, _cache=cache, transport=transport)
    with pytest.raises(ClientAuthenticationError) as ex:
        credential.get_token("scope")
    # error message should indicate multiple matching accounts, and list discovered accounts
    assert ex.value.message.startswith(MULTIPLE_MATCHING_ACCOUNTS[: MULTIPLE_MATCHING_ACCOUNTS.index("{")])
    discovered_accounts = ex.value.message.splitlines()[-1]
    assert discovered_accounts.count(upn) == 2
    assert tenant_a in discovered_accounts and tenant_b in discovered_accounts

    # with username and tenant_id specified, the credential should auth the matching account
    expected_access_token = "***"
    scope = "scope"
    transport = validating_transport(
        requests=[Request(required_data={"refresh_token": expected_refresh_token, "scope": scope})],
        responses=[mock_response(json_payload=build_aad_response(access_token=expected_access_token))],
    )
    credential = SharedTokenCacheCredential(username=upn, tenant_id=tenant_b, _cache=cache, transport=transport)
    token = credential.get_token(scope)
    assert token.token == expected_access_token


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
        ),
        "client_id": client_id,
        "token_endpoint": "https://" + authority + "/some/path",
        "scope": scopes or ["scope"],
    }


def populated_cache(*accounts):
    cache = TokenCache()
    for account in accounts:
        cache.add(account)
    return cache

if __name__ == "__main__":
    test_single_account()