# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import DeviceCodeCredential
from helpers import build_aad_response, get_discovery_response, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = validating_transport(
        requests=[Request()] * 3,
        responses=[
            # expected requests: discover tenant, start device code flow, poll for completion
            get_discovery_response(),
            mock_response(
                json_payload={
                    "device_code": "_",
                    "user_code": "user-code",
                    "verification_uri": "verification-uri",
                    "expires_in": 42,
                }
            ),
            mock_response(json_payload=dict(build_aad_response(access_token="**"), scope="scope")),
        ],
    )

    credential = DeviceCodeCredential(
        client_id="client-id", prompt_callback=Mock(), policies=[policy], transport=transport
    )

    credential.get_token("scope")

    assert policy.on_request.called
