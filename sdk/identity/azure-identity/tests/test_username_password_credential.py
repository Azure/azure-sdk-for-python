# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.identity import UsernamePasswordCredential
from azure.identity._internal.user_agent import USER_AGENT
import pytest

from helpers import (
    build_aad_response,
    build_id_token,
    get_discovery_response,
    mock_response,
    Request,
    validating_transport,
)

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        UsernamePasswordCredential("client-id", "username", "password", tenant_id=tenant)

    invalid_ids = {"my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            UsernamePasswordCredential("client-id", "username", "password", tenant_id=tenant)


def test_no_scopes():
    """The credential should raise when get_token is called with no scopes"""

    credential = UsernamePasswordCredential("client-id", "username", "password")
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = validating_transport(
        requests=[Request()] * 3,
        responses=[get_discovery_response()] * 2
        + [mock_response(json_payload=build_aad_response(access_token="**", id_token=build_id_token()))],
    )
    credential = UsernamePasswordCredential("client-id", "username", "password", policies=[policy], transport=transport)

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[get_discovery_response()] * 2
        + [mock_response(json_payload=build_aad_response(access_token="**", id_token=build_id_token()))],
    )

    credential = UsernamePasswordCredential("client-id", "username", "password", transport=transport)

    credential.get_token("scope")


def test_username_password_credential():
    expected_token = "access-token"
    client_id = "client-id"
    transport = validating_transport(
        requests=[Request()] * 3,  # not validating requests because they're formed by MSAL
        responses=[
            # tenant discovery
            mock_response(json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}),
            # user realm discovery, interests MSAL only when the response body contains account_type == "Federated"
            mock_response(json_payload={}),
            # token request
            mock_response(
                json_payload=build_aad_response(access_token=expected_token, id_token=build_id_token(aud=client_id))
            ),
        ],
    )

    credential = UsernamePasswordCredential(
        client_id=client_id,
        username="user@azure",
        password="secret_password",
        transport=transport,
        instance_discovery=False,  # kwargs are passed to MSAL; this one prevents an AAD verification request
    )

    token = credential.get_token("scope")
    assert token.token == expected_token


def test_authenticate():
    client_id = "client-id"
    environment = "localhost"
    issuer = "https://" + environment
    tenant_id = "some-tenant"
    authority = issuer + "/" + tenant_id

    access_token = "***"
    scope = "scope"

    # mock AAD response with id token
    object_id = "object-id"
    home_tenant = "home-tenant-id"
    username = "me@work.com"
    id_token = build_id_token(aud=client_id, iss=issuer, object_id=object_id, tenant_id=home_tenant, username=username)
    auth_response = build_aad_response(
        uid=object_id, utid=home_tenant, access_token=access_token, refresh_token="**", id_token=id_token
    )

    transport = validating_transport(
        requests=[Request(url_substring=issuer)] * 4,
        responses=[
            get_discovery_response(authority),  # instance discovery
            get_discovery_response(authority),  # tenant discovery
            mock_response(status_code=404),  # user realm discovery
            mock_response(json_payload=auth_response),  # token request following authenticate()
        ],
    )

    credential = UsernamePasswordCredential(
        username=username,
        password="1234",
        authority=environment,
        client_id=client_id,
        tenant_id=tenant_id,
        transport=transport,
    )
    record = credential._authenticate(scopes=(scope,))
    assert record.authority == environment
    assert record.home_account_id == object_id + "." + home_tenant
    assert record.tenant_id == home_tenant
    assert record.username == username

    # credential should have a cached access token for the scope passed to authenticate
    token = credential.get_token(scope)
    assert token.token == access_token
