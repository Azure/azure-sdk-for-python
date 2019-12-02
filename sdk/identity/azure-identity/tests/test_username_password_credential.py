# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import UsernamePasswordCredential
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
