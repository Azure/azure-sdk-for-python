# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity._internal.msal_credentials import MsalCredential
from azure.core.exceptions import ServiceRequestError

from helpers import mock, mock_response, Request, validating_transport


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
        requests=[
            Request(
                authority="login.microsoftonline.com",
                required_params={
                    "authorization_endpoint": "https://unknown.authority/organizations/oauth2/v2.0/authorize"
                },
            )
        ],
        responses=[mock_response(400, json_payload={"error": "invalid_instance"})],
    )
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        transport=transport,
    )
    with pytest.raises(ValueError, match="disable_instance_discovery"):
        credential._get_app()
    transport.send.assert_called_once()

    error = ServiceRequestError("unknown.authority is not resolvable")
    transport = mock.Mock(send=mock.Mock(side_effect=error))
    credential = MsalCredential(
        client_id="CLIENT_ID",
        authority="unknown.authority",
        disable_instance_discovery=True,
        transport=transport,
        retry_total=0,
    )

    with pytest.raises(ServiceRequestError) as ex:
        credential._get_app()
    assert ex.value is error
    transport.send.assert_called_once()
    request = transport.send.call_args.args[0]
    assert request.url == "https://unknown.authority/organizations/v2.0/.well-known/openid-configuration"
