# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import UsernamePasswordCredential
from azure.identity._internal.user_agent import USER_AGENT
from helpers import build_aad_response, get_discovery_response, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = validating_transport(
        requests=[Request()] * 3,
        responses=[get_discovery_response()] * 2 + [mock_response(json_payload=build_aad_response(access_token="**"))],
    )
    credential = UsernamePasswordCredential("client-id", "username", "password", policies=[policy], transport=transport)

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[get_discovery_response()] * 2 + [mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = UsernamePasswordCredential("client-id", "username", "password", transport=transport)

    credential.get_token("scope")


def test_username_password_credential():
    expected_token = "access-token"
    transport = validating_transport(
        requests=[Request()] * 3,  # not validating requests because they're formed by MSAL
        responses=[
            # tenant discovery
            mock_response(json_payload={"authorization_endpoint": "https://a/b", "token_endpoint": "https://a/b"}),
            # user realm discovery, interests MSAL only when the response body contains account_type == "Federated"
            mock_response(json_payload={}),
            # token request
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 42,
                    "token_type": "Bearer",
                    "ext_expires_in": 42,
                }
            ),
        ],
    )

    credential = UsernamePasswordCredential(
        client_id="some-guid",
        username="user@azure",
        password="secret_password",
        transport=transport,
        instance_discovery=False,  # kwargs are passed to MSAL; this one prevents an AAD verification request
    )

    token = credential.get_token("scope")
    assert token.token == expected_token
