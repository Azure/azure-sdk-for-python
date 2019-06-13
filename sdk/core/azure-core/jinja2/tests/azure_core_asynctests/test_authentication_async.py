# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import AsyncPipeline, PipelineResponse
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, HTTPPolicy
from azure.core.pipeline.transport import HttpRequest, AsyncHttpTransport
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock

@pytest.mark.asyncio
async def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock(spec=PipelineResponse)

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    async def get_token(_):
        return ""

    fake_credential = Mock(get_token=get_token)
    policies = [
        AsyncBearerTokenCredentialPolicy(fake_credential, "scope"),
        Mock(spec=HTTPPolicy, send=verify_request),
    ]
    response = await AsyncPipeline(transport=Mock(spec=AsyncHttpTransport), policies=policies).run(expected_request)

    assert response is expected_response