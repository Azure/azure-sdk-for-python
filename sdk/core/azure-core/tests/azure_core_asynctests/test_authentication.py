# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest.mock import Mock
from azure.core.pipeline import AsyncPipeline, PipelineResponse
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, HTTPPolicy
from azure.core.pipeline.transport import HttpRequest, AsyncHttpTransport
import pytest


@pytest.mark.asyncio
async def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    expected_token = "expected_token"

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token)

    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    fake_credential = Mock(get_token=get_token)
    policies = [
        AsyncBearerTokenCredentialPolicy(fake_credential, "scope"),
        Mock(spec=HTTPPolicy, send=verify_authorization_header),
    ]
    pipeline = AsyncPipeline(transport=Mock(spec=AsyncHttpTransport), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"), context=None)
    assert get_token_calls == 1


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
    pipeline = AsyncPipeline(transport=Mock(spec=AsyncHttpTransport), policies=policies)

    response = await pipeline.run(expected_request)

    assert response is expected_response
