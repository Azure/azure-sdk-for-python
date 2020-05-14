# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import AuthorizationCodeCredential
from azure.identity._internal.user_agent import USER_AGENT
import msal
import pytest

from helpers import build_aad_response, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = AuthorizationCodeCredential("tenant-id", "client-id", "auth-code", "http://localhost")
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", policies=[policy], transport=Mock(send=send)
    )

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = AuthorizationCodeCredential(
        "tenant-id", "client-id", "auth-code", "http://localhost", transport=transport
    )

    credential.get_token("scope")


def test_auth_code_credential():
    client_id = "client id"
    tenant_id = "tenant"
    expected_code = "auth code"
    redirect_uri = "https://localhost"
    expected_access_token = "access"
    expected_refresh_token = "refresh"
    expected_scope = "scope"

    auth_response = build_aad_response(access_token=expected_access_token, refresh_token=expected_refresh_token)
    transport = validating_transport(
        requests=[
            Request(  # first call should redeem the auth code
                url_substring=tenant_id,
                required_data={
                    "client_id": client_id,
                    "code": expected_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "scope": expected_scope,
                },
            ),
            Request(  # third call should redeem the refresh token
                url_substring=tenant_id,
                required_data={
                    "client_id": client_id,
                    "grant_type": "refresh_token",
                    "refresh_token": expected_refresh_token,
                    "scope": expected_scope,
                },
            ),
        ],
        responses=[mock_response(json_payload=auth_response)] * 2,
    )
    cache = msal.TokenCache()

    credential = AuthorizationCodeCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        authorization_code=expected_code,
        redirect_uri=redirect_uri,
        transport=transport,
        cache=cache,
    )

    # first call should redeem the auth code
    token = credential.get_token(expected_scope)
    assert token.token == expected_access_token
    assert transport.send.call_count == 1

    # no auth code -> credential should return cached token
    token = credential.get_token(expected_scope)
    assert token.token == expected_access_token
    assert transport.send.call_count == 1

    # no auth code, no cached token -> credential should redeem refresh token
    cached_access_token = cache.find(cache.CredentialType.ACCESS_TOKEN)[0]
    cache.remove_at(cached_access_token)
    token = credential.get_token(expected_scope)
    assert token.token == expected_access_token
    assert transport.send.call_count == 2
