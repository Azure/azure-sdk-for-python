# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpRequest
import pytest


@pytest.mark.asyncio
async def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    expected_token = AccessToken("expected_token", 0)

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)

    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    fake_credential = Mock(get_token=get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"), context=None)
    assert get_token_calls == 1


@pytest.mark.asyncio
async def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken("", 0)))
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


@pytest.mark.asyncio
async def test_bearer_policy_token_caching():
    good_for_one_hour = AccessToken("token", time.time() + 3600)
    expected_token = good_for_one_hour
    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    credential = Mock(get_token=get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), Mock(send=asyncio.coroutine(lambda _: Mock()))]
    pipeline = AsyncPipeline(transport=Mock, policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # policy has no token at first request -> it should call get_token

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    get_token_calls = 0
    expected_token = expired_token
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), Mock(send=asyncio.coroutine(lambda _: Mock()))]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 2  # token expired -> policy should call get_token
