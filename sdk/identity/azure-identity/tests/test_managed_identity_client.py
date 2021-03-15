# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

from azure.core.pipeline.transport import HttpRequest
from azure.identity._internal.managed_identity_client import ManagedIdentityClient

from helpers import mock_response, Request, validating_transport


def test_caching():
    scope = "scope"
    expected_expires_on = int(time.time() + 3600)
    expected_token = "*"
    transport = validating_transport(
        requests=[Request(url="http://localhost")],
        responses=[
            mock_response(
                json_payload={
                    "access_token": expected_token,
                    "expires_in": 3600,
                    "expires_on": expected_expires_on,
                    "resource": scope,
                    "token_type": "Bearer",
                }
            )
        ],
    )
    client = ManagedIdentityClient(
        request_factory=lambda _, __: HttpRequest("GET", "http://localhost"), transport=transport
    )

    token = client.get_cached_token(scope)
    assert not token

    token = client.request_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token

    token = client.get_cached_token(scope)
    assert token.expires_on == expected_expires_on
    assert token.token == expected_token
