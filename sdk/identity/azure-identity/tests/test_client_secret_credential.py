# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import ClientSecretCredential
from helpers import build_aad_response, mock_response

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    credential = ClientSecretCredential(
        "tenant-id",
        "client-id",
        "client-secret",
        policies=[ContentDecodePolicy(), policy],
        transport=Mock(send=lambda *_, **__: mock_response(json_payload=build_aad_response(access_token="**"))),
    )

    credential.get_token("scope")

    assert policy.on_request.called
