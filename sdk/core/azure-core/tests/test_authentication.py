# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, HTTPPolicy
from azure.core.pipeline.transport import HttpRequest, HttpTransport

try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock


def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    expected_token = "expected_token"

    def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token)

    fake_credential = Mock(get_token=Mock(return_value=expected_token))
    policies = [
        BearerTokenCredentialPolicy(fake_credential, "scope"),
        Mock(spec=HTTPPolicy, send=verify_authorization_header),
    ]

    Pipeline(transport=Mock(spec=HttpTransport), policies=policies).run(HttpRequest("GET", "https://spam.eggs"))

    assert fake_credential.get_token.call_count == 1


def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock(spec=PipelineResponse)

    def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda _: "")
    policies = [
        BearerTokenCredentialPolicy(fake_credential, "scope"),
        Mock(spec=HTTPPolicy, send=verify_request),
    ]
    response = Pipeline(transport=Mock(spec=HttpTransport), policies=policies).run(expected_request)

    assert response is expected_response
