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
from unittest.mock import AsyncMock, Mock

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.pipeline import AsyncPipeline, PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest
from azure.keyvault.securitydomain._internal import HttpChallenge, HttpChallengeCache
from azure.keyvault.securitydomain._internal.async_challenge_auth_policy import AsyncChallengeAuthPolicy

from test_challenge_auth import (
    BACKSLASH_AUTHORITIES,
    BACKSLASH_CACHE_CASES,
    CHALLENGE,
    TOKEN_TYPES,
    VALID_CACHED_URLS,
    VALID_CHALLENGE_AUTHORITIES,
    get_random_url,
)


def empty_challenge_cache(fn):
    @functools.wraps(fn)
    async def wrapper(**kwargs):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return await fn(**kwargs)

    return wrapper


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("authority,cache_state", BACKSLASH_CACHE_CASES)
@pytest.mark.parametrize("verify_challenge_resource", [True, False])
async def test_rejects_backslash_authority(authority, cache_state, verify_challenge_resource):
    url = f"https://{authority}/securitydomain/canary"
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(side_effect=AssertionError("unexpected token request"))
    )
    transport = Mock(send=AsyncMock(side_effect=AssertionError("unexpected transport send")))
    policy = AsyncChallengeAuthPolicy(credential, verify_challenge_resource=verify_challenge_resource)
    pipeline = AsyncPipeline(policies=[policy], transport=transport)
    if cache_state != "empty":
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, CHALLENGE))
    if cache_state == "token":
        policy._token = AccessToken("cached-token", time.time() + 3600)
    cached = HttpChallengeCache._cache.copy()

    for _ in range(2):
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        with pytest.raises(ValueError, match="backslash"):
            await pipeline.run(request)
        assert "Authorization" not in request.headers
        assert request.body == b"secret"
        assert HttpChallengeCache._cache == cached

    credential.get_token.assert_not_called()
    transport.send.assert_not_called()


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("authority", BACKSLASH_AUTHORITIES)
@pytest.mark.parametrize("verify_challenge_resource", [True, False])
async def test_rejects_backslash_authority_on_challenge(authority, verify_challenge_resource):
    url = f"https://{authority}/securitydomain/canary"
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(side_effect=AssertionError("unexpected token request"))
    )
    policy = AsyncChallengeAuthPolicy(credential, verify_challenge_resource=verify_challenge_resource)
    transport = Mock()
    response = Mock(http_response=Mock(status_code=401, headers={"WWW-Authenticate": CHALLENGE}))

    for _ in range(2):
        request = PipelineRequest(HttpRequest("GET", url), PipelineContext(transport))
        with pytest.raises(ValueError, match="backslash"):
            await policy.on_challenge(request, response)
        assert "Authorization" not in request.http_request.headers
        assert not HttpChallengeCache._cache

    credential.get_token.assert_not_called()
    transport.send.assert_not_called()


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("url", VALID_CACHED_URLS)
async def test_request_url_validation_preserves_cached_urls(url):
    challenge = HttpChallenge(url, CHALLENGE)
    HttpChallengeCache.set_challenge_for_url(url, challenge)
    credential = Mock(spec_set=["get_token"], get_token=AsyncMock())
    # These URL-only fixtures deliberately use an unrelated challenge resource.
    policy = AsyncChallengeAuthPolicy(credential, verify_challenge_resource=False)
    policy._token = AccessToken("cached-token", time.time() + 3600)

    for _ in range(2):
        request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
        await policy.on_request(request)
        assert request.http_request.url == url
        assert request.http_request.headers["Authorization"] == "Bearer cached-token"
        assert HttpChallengeCache.get_challenge_for_url(url) is challenge

    credential.get_token.assert_not_called()


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("authority,resource,tenant", VALID_CHALLENGE_AUTHORITIES)
async def test_request_url_validation_preserves_challenge_flow(authority, resource, tenant):
    url = f"https://{authority}/securitydomain/item"
    challenge = Mock(
        status_code=401,
        headers={
            "WWW-Authenticate": f'Bearer authorization="https://authority.net/{tenant}", resource=https://{resource}'
        },
    )

    async def send(request):
        assert request.url == url
        if "Authorization" not in request.headers:
            assert not request.body
            assert request.headers["Content-Length"] == "0"
            return challenge
        assert request.headers["Authorization"] == "Bearer expected-token"
        assert request.body == b"secret"
        return Mock(status_code=200)

    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("expected-token", time.time() + 3600))
    )
    transport = Mock(send=AsyncMock(wraps=send))
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential)], transport=transport)
    for _ in range(2):
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        assert (await pipeline.run(request)).http_response.status_code == 200

    assert transport.send.await_count == 3
    credential.get_token.assert_awaited_once()
    assert credential.get_token.call_args.args == (f"https://{resource}/.default",)
    if tenant == "adfs":
        assert "tenant_id" not in credential.get_token.call_args.kwargs
    else:
        assert credential.get_token.call_args.kwargs["tenant_id"] == tenant
    assert HttpChallengeCache.get_challenge_for_url(url).get_resource() == f"https://{resource}"


@pytest.mark.asyncio
@empty_challenge_cache
async def test_rejected_challenge_is_not_cached():
    url = "https://example.net/securitydomain/canary"
    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'},
    )

    class Requests:
        count = 0

    async def send(request):
        Requests.count += 1
        assert "Authorization" not in request.headers
        assert not request.body
        assert request.headers["Content-Length"] == "0"
        return challenge

    credential = Mock(spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request")))
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))

    for _ in range(2):
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        with pytest.raises(ValueError):
            await pipeline.run(request)

    assert Requests.count == 2
    assert not HttpChallengeCache.get_challenge_for_url(url)
    assert credential.get_token.call_count == 0


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
