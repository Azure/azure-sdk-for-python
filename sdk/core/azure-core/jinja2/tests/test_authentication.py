# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, HTTPPolicy
from azure.core.pipeline.transport import HttpRequest, HttpTransport
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock


def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock(spec=PipelineResponse)

    def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    def get_token(_):
        return ""

    fake_credential = Mock(get_token=get_token)
    policies = [
        BearerTokenCredentialPolicy(fake_credential, "scope"),
        Mock(spec=HTTPPolicy, send=verify_request),
    ]
    response = Pipeline(transport=Mock(spec=HttpTransport), policies=policies).run(expected_request)

    assert response is expected_response