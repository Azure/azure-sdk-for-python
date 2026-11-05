# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity._internal.msal_credentials import MsalCredential
from azure.core.exceptions import ServiceRequestError

from helpers import get_discovery_response, mock, mock_response, Request, validating_transport


def test_instance_discovery():
    transport = mock.Mock(send=mock.Mock(return_value=get_discovery_response()))
    credential = MsalCredential(
        client_id="CLIENT_ID",
        disable_instance_discovery=True,
        transport=transport,
    )
    app = credential._get_app()
    assert not app._instance_discovery

    credential = MsalCredential(
        client_id="CLIENT_ID",
        disable_instance_discovery=False,
        transport=transport,
    )
    app = credential._get_app()
    assert app._instance_discovery


def test_unknown_authority():
    transport = validating_transport(
        requests=[
            Request(authority="login.microsoftonline.com", url_substring="/common/discovery/instance", method="GET")
        ],
        responses=[mock_response(status_code=400, json_payload={"error": "invalid_instance"})],
    )
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        transport=transport,
    )
    with pytest.raises(ValueError, match="disable_instance_discovery"):
        credential._get_app()
    transport.send.assert_called_once()

    transport = mock.Mock(send=mock.Mock(side_effect=ServiceRequestError("Simulated connection failure")))
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        disable_instance_discovery=True,
        transport=transport,
        retry_total=0,
    )

    with pytest.raises(ServiceRequestError, match="Simulated connection failure"):
        credential._get_app()
    transport.send.assert_called_once()
    assert (
        transport.send.call_args[0][0].url
        == "https://unknown.authority/organizations/v2.0/.well-known/openid-configuration"
    )
