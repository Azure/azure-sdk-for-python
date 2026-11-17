# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity._internal.msal_credentials import MsalCredential

from helpers import get_discovery_response, mock_response, Request, validating_transport


def test_instance_discovery():
    credential = MsalCredential(
        client_id="CLIENT_ID",
        disable_instance_discovery=True,
    )
    app = credential._get_app()
    assert not app._instance_discovery

    credential = MsalCredential(
        client_id="CLIENT_ID",
        disable_instance_discovery=False,
    )
    app = credential._get_app()
    assert app._instance_discovery


def test_unknown_authority():
    transport = validating_transport(
        [
            Request(
                method="GET",
                authority="login.microsoftonline.com",
                url_substring="/common/discovery/instance",
                required_params={
                    "authorization_endpoint": "https://unknown.authority/organizations/oauth2/v2.0/authorize"
                },
            )
        ],
        [mock_response(status_code=400, json_payload={"error": "invalid_instance"})],
    )
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        transport=transport,
    )
    with pytest.raises(ValueError, match="disable_instance_discovery"):
        credential._get_app()
    transport.send.assert_called_once()

    transport = validating_transport(
        [Request(method="GET", url="https://unknown.authority/organizations/v2.0/.well-known/openid-configuration")],
        [get_discovery_response(endpoint="https://unknown.authority/organizations")],
    )
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        disable_instance_discovery=True,
        transport=transport,
    )

    app = credential._get_app()
    assert not app._instance_discovery
    transport.send.assert_called_once()
