# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""
import asyncio

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import HttpRequest
from azure.keyvault.certificates._shared import AsyncChallengeAuthPolicy, HttpChallenge, HttpChallengeCache
import pytest

from certificates_helpers import async_validating_transport, mock_response, Request


@pytest.mark.asyncio
async def test_policy():
    # ensure the test starts with an empty cache
    HttpChallengeCache.clear()

    expected_scope = "https://challenge.resource/.default"
    expected_token = "expected_token"
    challenge = Mock(
        status_code=401,
        headers={
            "WWW-Authenticate": 'Bearer authorization="https://login.authority.net/tenant", resource={}'.format(
                expected_scope
            )
        },
    )
    success = Mock(status_code=200)
    data = {"spam": "eggs"}

    responses = (r for r in (challenge, success))

    async def send(request):
        response = next(responses)
        if response is challenge:
            # this is the first request
            assert not request.body
            assert request.headers["Content-Length"] == "0"
        elif response is success:
            # this is the second request
            assert request.body == data
            assert expected_token in request.headers["Authorization"]
        return response

    async def get_token(*scopes):
        print("get token")
        assert len(scopes) is 1
        assert scopes[0] == expected_scope
        return AccessToken(expected_token, 0)

    credential = Mock(get_token=get_token)
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
    await pipeline.run(HttpRequest("POST", "https://azure.service", data=data))


@pytest.mark.asyncio
async def test_policy_updates_cache():
    """
    It's possible for the challenge returned for a request to change, e.g. when a vault is moved to a new tenant.
    When the policy receives a 401, it should update the cached challenge for the requested URL, if one exists.
    """

    # ensure the test starts with an empty cache
    HttpChallengeCache.clear()

    url = "https://azure.service/path"
    first_scope = "https://first-scope"
    first_token = "first-scope-token"
    second_scope = "https://second-scope"
    second_token = "second-scope-token"
    challenge_fmt = 'Bearer authorization="https://login.authority.net/tenant", resource={}'

    # mocking a tenant change:
    # 1. first request -> respond with challenge
    # 2. second request should be authorized according to the challenge -> respond with success
    # 3. third request should match the second -> respond with a new challenge
    # 4. fourth request should be authorized according to the new challenge -> respond with success
    # 5. fifth request should match the fourth -> respond with success
    transport = async_validating_transport(
        requests=(
            Request(url),
            Request(url, required_headers={"Authorization": "Bearer {}".format(first_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(first_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(second_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(second_token)}),
        ),
        responses=(
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt.format(first_scope)}),
            mock_response(status_code=200),
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt.format(second_scope)}),
            mock_response(status_code=200),
            mock_response(status_code=200),
        ),
    )

    tokens = (t for t in [first_token] * 2 + [second_token] * 2)
    credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken(next(tokens), 0)))
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=transport)

    # policy should complete and cache the first challenge
    await pipeline.run(HttpRequest("GET", url))

    # The next request will receive a challenge. The policy should handle it and update the cache entry.
    await pipeline.run(HttpRequest("GET", url))
