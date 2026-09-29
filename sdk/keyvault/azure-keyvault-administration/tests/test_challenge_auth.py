# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation.
"""

import functools
from itertools import product
import time
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.pipeline import AsyncPipeline, Pipeline
from azure.core.rest import HttpRequest
from azure.keyvault.administration._internal import ChallengeAuthPolicy, HttpChallengeCache
from azure.keyvault.administration._internal.async_challenge_auth_policy import AsyncChallengeAuthPolicy, await_result

TOKEN_TYPES = [AccessToken, AccessTokenInfo]


@pytest.fixture
def isolated_challenge_cache():
    HttpChallengeCache.clear()
    yield
    HttpChallengeCache.clear()


@pytest.mark.asyncio
@pytest.mark.usefixtures("isolated_challenge_cache")
@pytest.mark.parametrize("producer_async,consumer_async", product([False, True], repeat=2))
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
@pytest.mark.parametrize("parameter", ["resource", "scope"])
@pytest.mark.parametrize("producer_fails", [False, True])
@pytest.mark.parametrize("verify", [None, True, False])
@pytest.mark.parametrize("resource", ["https://other.test", "https://example.test"])
async def test_cached_challenge_respects_consumer_verification(
    producer_async, consumer_async, token_type, parameter, producer_fails, verify, resource
):
    url = "https://cache.example.test/items"
    scope = resource + "/.default"
    value = resource if parameter == "resource" else scope
    header = f'Bearer authorization="https://authority.test/tenant", {parameter}="{value}"'
    method = "get_token" if token_type is AccessToken else "get_token_info"
    producer_token = (AsyncMock if producer_async else Mock)(
        return_value=token_type("producer-token", time.time() + 3600),
        side_effect=ValueError("producer credential failed") if producer_fails else None,
    )
    producer = (AsyncChallengeAuthPolicy if producer_async else ChallengeAuthPolicy)(
        Mock(spec_set=[method], **{method: producer_token}), verify_challenge_resource=False
    )
    producer_send = (AsyncMock if producer_async else Mock)(
        side_effect=[
            Mock(status_code=401, headers={"WWW-Authenticate": header}),
            Mock(status_code=200),
        ]
    )
    producer_pipeline = (AsyncPipeline if producer_async else Pipeline)(
        policies=[producer], transport=Mock(send=producer_send)
    )
    if producer_fails:
        with pytest.raises(ValueError, match="producer credential failed"):
            await await_result(producer_pipeline.run, HttpRequest("GET", url))
    else:
        await await_result(producer_pipeline.run, HttpRequest("GET", url))
    assert producer_token.call_count == 1
    assert HttpChallengeCache.get_challenge_for_url(url) is not None

    consumer_token = (AsyncMock if consumer_async else Mock)(
        return_value=token_type("consumer-token", time.time() + 3600)
    )
    options = {} if verify is None else {"verify_challenge_resource": verify}
    consumer = (AsyncChallengeAuthPolicy if consumer_async else ChallengeAuthPolicy)(
        Mock(spec_set=[method], **{method: consumer_token}), **options
    )
    consumer_send = (AsyncMock if consumer_async else Mock)(return_value=Mock(status_code=200))
    consumer_pipeline = (AsyncPipeline if consumer_async else Pipeline)(
        policies=[consumer], transport=Mock(send=consumer_send)
    )
    request = HttpRequest("GET", url)
    if verify is False or resource == "https://example.test":
        await await_result(consumer_pipeline.run, request)
        assert consumer_token.call_args.args == (scope,)
        assert request.headers["Authorization"] == "Bearer consumer-token"
        assert consumer_send.call_count == 1
        assert HttpChallengeCache.get_challenge_for_url(url) is not None
    else:
        with pytest.raises(ValueError, match="does not match the requested domain"):
            await await_result(consumer_pipeline.run, request)
        consumer_token.assert_not_called()
        consumer_send.assert_not_called()
        assert "Authorization" not in request.headers
        assert HttpChallengeCache.get_challenge_for_url(url) is None
        assert consumer._token is None


def empty_challenge_cache(fn):
    @functools.wraps(fn)
    def wrapper(**kwargs):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return fn(**kwargs)

    return wrapper


def async_empty_challenge_cache(fn):
    @functools.wraps(fn)
    async def wrapper(**kwargs):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return await fn(**kwargs)

    return wrapper


def get_random_url():
    """The challenge cache is keyed on URLs. Random URLs defend against tests interfering with each other."""

    return f"https://{uuid4()}.vault.azure.net/{uuid4()}".replace("-", "")


@empty_challenge_cache
def test_rejected_challenge_is_not_cached():
    url = "https://example.net/backup/canary"
    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'},
    )

    class Requests:
        count = 0

    def send(request):
        Requests.count += 1
        assert "Authorization" not in request.headers
        assert not request.body
        assert request.headers["Content-Length"] == "0"
        return challenge

    credential = Mock(spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request")))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))

    for _ in range(2):
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        with pytest.raises(ValueError):
            pipeline.run(request)

    assert Requests.count == 2
    assert not HttpChallengeCache.get_challenge_for_url(url)
    assert credential.get_token.call_count == 0


@pytest.mark.asyncio
@async_empty_challenge_cache
async def test_rejected_challenge_is_not_cached_async():
    url = "https://example.net/backup/canary"
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


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_request_body_not_reused_across_requests(token_type):
    """A request's body must not leak into a later request made by the same client.

    Regression test for the replay bug: the original request used to be stashed on the policy instance and was
    never cleared, so a subsequent bodiless request (e.g. a polling GET during a backup/restore operation) that
    triggered its own challenge would have the earlier request's body (and method/URL) replayed onto it. The copy
    is now stored per-request on the pipeline context, so it cannot leak across requests. See
    https://github.com/Azure/azure-sdk-for-python/pull/47742.
    """

    expected_token = "expected_token"
    first_content = b"a duck"
    first_url = get_random_url()
    second_url = get_random_url()
    challenge = Mock(
        status_code=401,
        headers={
            "WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
        },
    )

    class Requests:
        count = 0

    def send(request):
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

    def get_token(*_, **__):
        return token_type(expected_token, time.time() + 3600)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    # a single policy instance handles both requests; the fix prevents state from one request leaking into the next
    policy = ChallengeAuthPolicy(credential=credential)
    pipeline = Pipeline(policies=[policy], transport=Mock(send=send))

    first_request = HttpRequest("POST", first_url)
    first_request.set_bytes_body(first_content)
    pipeline.run(first_request)

    pipeline.run(HttpRequest("GET", second_url))


@pytest.mark.asyncio
@async_empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_request_body_not_reused_across_requests_async(token_type):
    """A request's body must not leak into a later request made by the same client (async).

    Regression test for the replay bug: the original request used to be stashed on the policy instance and was
    never cleared, so a subsequent bodiless request (e.g. a polling GET during a backup/restore operation) that
    triggered its own challenge would have the earlier request's body (and method/URL) replayed onto it. The copy
    is now stored per-request on the pipeline context, so it cannot leak across requests. See
    https://github.com/Azure/azure-sdk-for-python/pull/47742.
    """

    expected_token = "expected_token"
    first_content = b"a duck"
    first_url = get_random_url()
    second_url = get_random_url()
    challenge = Mock(
        status_code=401,
        headers={
            "WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
        },
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
