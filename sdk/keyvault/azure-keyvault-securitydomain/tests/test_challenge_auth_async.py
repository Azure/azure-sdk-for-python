# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""

import functools
import time
from unittest.mock import Mock

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.pipeline import AsyncPipeline
from azure.core.rest import HttpRequest
from azure.keyvault.securitydomain._internal import HttpChallengeCache
from azure.keyvault.securitydomain._internal.async_challenge_auth_policy import AsyncChallengeAuthPolicy

from test_challenge_auth import get_random_url, TOKEN_TYPES


def empty_challenge_cache(fn):
    @functools.wraps(fn)
    async def wrapper(**kwargs):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return await fn(**kwargs)

    return wrapper


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_request_body_not_reused_across_requests(token_type):
    """A request's body must not leak into a later request made by the same client.

    Regression test for the replay bug: the original request used to be stashed on the policy instance and was
    never cleared, so a subsequent bodiless request (e.g. a polling GET) that triggered its own challenge would
    have the earlier request's body (and method/URL) replayed onto it. The copy is now stored per-request on the
    pipeline context, so it cannot leak across requests. See
    https://github.com/Azure/azure-sdk-for-python/pull/48537.
    """

    expected_token = "expected_token"
    first_content = b"a duck"
    first_url = get_random_url()
    second_url = get_random_url()
    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'},
    )

    class Requests:
        count = 0

    async def send(request):
        Requests.count += 1
        if Requests.count == 1:
            # first request (POST with body): the body is stripped to elicit a challenge
            assert not request.body
            assert request.headers["Content-Length"] == "0"
            return challenge
        elif Requests.count == 2:
            # first request is retried with its original body and authorization
            assert request.body == first_content
            assert expected_token in request.headers["Authorization"]
            return Mock(status_code=200)
        elif Requests.count == 3:
            # second request (bodiless GET): elicits its own challenge and must have no body
            assert not request.body
            return challenge
        elif Requests.count == 4:
            # second request is retried: it must remain a bodiless GET, i.e. the first request's body and
            # method/URL must NOT be replayed onto it
            assert not request.body
            assert request.method == "GET"
            assert request.url == second_url
            assert expected_token in request.headers["Authorization"]
            return Mock(status_code=200)
        raise ValueError("unexpected request")

    async def get_token(*_, **__):
        return token_type(expected_token, time.time() + 3600)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    # a single policy instance handles both requests; the fix prevents state from one request leaking into the next
    policy = AsyncChallengeAuthPolicy(credential=credential)
    pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))

    first_request = HttpRequest("POST", first_url)
    first_request.set_bytes_body(first_content)
    await pipeline.run(first_request)

    await pipeline.run(HttpRequest("GET", second_url))
