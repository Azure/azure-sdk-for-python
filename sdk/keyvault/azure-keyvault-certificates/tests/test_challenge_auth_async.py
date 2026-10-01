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
from urllib.parse import urlparse
from uuid import uuid4

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline, PipelineContext, PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncRedirectPolicy, AsyncRetryPolicy, SensitiveHeaderCleanupPolicy
from azure.core.rest import HttpRequest
from azure.keyvault.certificates._shared import AsyncChallengeAuthPolicy, HttpChallenge, HttpChallengeCache

from test_challenge_auth import (
    CACHE_RESOURCE_DOMAINS,
    INVALID_CHALLENGE_HEADERS,
    redirect_replay_case,
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
    url = f"https://{authority}/certificates/canary"
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
    url = f"https://{authority}/certificates/canary"
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
    url = f"https://{authority}/certificates/item"
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
@pytest.mark.parametrize("fresh_policy", [False, True])
async def test_rejected_challenge_is_not_cached(fresh_policy):
    url = "https://example.net/certificates/canary"
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
        assert "Authorization" not in request.headers
        assert not request.body
        assert request.headers["Content-Length"] == "0"
        return challenge

    credential = Mock(spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request")))
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))

    for _ in range(2):
        if fresh_policy:
            pipeline = AsyncPipeline(
                policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send)
            )
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


@pytest.mark.parametrize("token_type", TOKEN_TYPES)
@pytest.mark.parametrize("cached_token", [False, True])
@pytest.mark.parametrize(
    "request_port,resource",
    [
        ("", "https://other.example"),
        ("", "invalid"),
        ("", "https://vault.azure.net:8443"),
        (":8443", "https://vault.azure.net"),
        (":8443", "https://vault.azure.net:443"),
        (":443", "https://vault.azure.net:8443"),
    ],
)
@pytest.mark.asyncio
async def test_cached_challenge_resource_is_verified(token_type, cached_token, request_port, resource):
    url = get_random_url().replace(".vault.azure.net/", f".vault.azure.net{request_port}/")
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", resource={resource}')
    )
    credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(side_effect=AssertionError("unexpected token request")),
        get_token_info=Mock(side_effect=AssertionError("unexpected token request")),
    )
    policy = AsyncChallengeAuthPolicy(credential)
    if cached_token:
        policy._token = token_type("cached-token", time.time() + 3600)
    transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport call")))
    request = HttpRequest("POST", url, content=b"secret")

    with pytest.raises(ValueError):
        await AsyncPipeline(policies=[policy], transport=transport).run(request)

    assert "Authorization" not in request.headers
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()
    transport.send.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None

    follow_up = PipelineRequest(HttpRequest("POST", url, content=b"next secret"), PipelineContext(None))
    await policy.on_request(follow_up)
    response = PipelineResponse(
        follow_up.http_request, Mock(status_code=401, headers={"WWW-Authenticate": "Bearer"}), follow_up.context
    )
    assert await policy.on_challenge(follow_up, response) is False
    assert "Authorization" not in follow_up.http_request.headers
    assert not follow_up.http_request.body
    assert follow_up.http_request.headers["Content-Length"] == "0"
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()


@pytest.mark.parametrize("cached_token", [False, True])
@pytest.mark.asyncio
async def test_opt_out_cache_is_not_trusted_by_strict_policy(cached_token):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://other.example'
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("opt-out", time.time() + 3600))
    )
    transport = Mock(
        send=AsyncMock(
            side_effect=[
                Mock(status_code=401, headers={"WWW-Authenticate": header}),
                Mock(status_code=200),
                Mock(status_code=200),
            ]
        )
    )
    pipeline = AsyncPipeline(
        policies=[AsyncChallengeAuthPolicy(credential, verify_challenge_resource=False)], transport=transport
    )
    await pipeline.run(HttpRequest("GET", url))
    await pipeline.run(HttpRequest("GET", url))
    assert transport.send.call_count == 3
    credential.get_token.assert_called_once()
    assert HttpChallengeCache.get_challenge_for_url(url)

    strict_credential = Mock(
        spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request"))
    )
    strict_policy = AsyncChallengeAuthPolicy(strict_credential)
    if cached_token:
        strict_policy._token = AccessToken("strict-token", time.time() + 3600)
    strict_transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport call")))
    with pytest.raises(ValueError):
        await AsyncPipeline(policies=[strict_policy], transport=strict_transport).run(HttpRequest("GET", url))
    strict_credential.get_token.assert_not_called()
    strict_transport.send.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("header", INVALID_CHALLENGE_HEADERS)
@pytest.mark.asyncio
async def test_rejected_response_preserves_concurrent_challenge(header):
    url = get_random_url()
    credential = Mock(spec_set=["get_token"])
    policy = AsyncChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("POST", url, content=b"secret"), PipelineContext(None))
    await policy.on_request(request)
    assert not request.http_request.body
    replacement = HttpChallenge(
        url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    )
    HttpChallengeCache.set_challenge_for_url(url, replacement)
    response = PipelineResponse(
        request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
    )
    if header and "authorization=" in header:
        with pytest.raises(ValueError):
            await policy.on_challenge(request, response)
    else:
        assert await policy.on_challenge(request, response) is False
    assert HttpChallengeCache.get_challenge_for_url(url) is replacement
    assert "Authorization" not in request.http_request.headers
    assert not request.http_request.body
    credential.get_token.assert_not_called()

    async def send(fresh_request):
        assert "Authorization" not in fresh_request.headers
        assert not fresh_request.body
        assert fresh_request.headers["Content-Length"] == "0"
        return Mock(status_code=401, headers={})

    # Start a separate cold-discovery scenario, independent of the concurrent cache entry.
    HttpChallengeCache.remove_challenge_for_url(url)
    fresh = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential)], transport=Mock(send=send))
    assert (await fresh.run(HttpRequest("POST", url, content=b"new secret"))).http_response.status_code == 401
    credential.get_token.assert_not_called()


@pytest.mark.parametrize("header", ["", " ", "Bearer", "Bearer resource=https://vault.azure.net"])
@pytest.mark.parametrize("consecutive", [False, True])
@pytest.mark.asyncio
async def test_malformed_challenge_flow_clears_cache(header, consecutive):
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net')
    )
    credential = Mock(spec_set=["get_token"])
    policy = AsyncChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    policy._token = AccessToken("token", time.time() + 3600)
    await policy.on_request(request)
    response = PipelineResponse(
        request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
    )
    assert await policy.handle_challenge_flow(request, response, consecutive_challenge=consecutive) is response
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    credential.get_token.assert_not_called()


@pytest.mark.asyncio
async def test_cae_invalid_inherited_scope_clears_cache():
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url,
        HttpChallenge(url, 'Bearer authorization="https://authority.net/tenant", scope=https://other.example/.default'),
    )
    credential = Mock(spec_set=["get_token"])
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    response = PipelineResponse(
        request.http_request,
        Mock(
            status_code=401,
            headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/", claims="e30="'},
        ),
        request.context,
    )
    with pytest.raises(ValueError):
        await AsyncChallengeAuthPolicy(credential).on_challenge(request, response)
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    credential.get_token.assert_not_called()


@pytest.mark.parametrize("domain", CACHE_RESOURCE_DOMAINS)
@pytest.mark.parametrize("parameter", ["resource", "scope"])
@pytest.mark.parametrize(
    "request_port,resource_port", [("", ""), (":443", ""), ("", ":443"), (":443", ":443"), (":8443", ":8443")]
)
@pytest.mark.asyncio
async def test_valid_challenge_cache_reuse(domain, parameter, request_port, resource_port):
    host = f"{uuid4().hex}.{domain}"
    url = f"https://{host}{request_port}/first"
    alias_port = "" if request_port == ":443" else ":443" if not request_port else request_port
    alias = f"https://{host.upper()}{alias_port}/next"
    resource = f"https://{domain.upper()}{resource_port}"
    scope = resource + "/.default"
    header = f'Bearer authorization="https://authority.example/ADFS", {parameter}={scope if parameter == "scope" else resource}'
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    requests = []

    async def send(request):
        requests.append(request)
        if len(requests) == 1:
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(status_code=401, headers={"WWW-Authenticate": header})
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == b"body"
        return Mock(status_code=200)

    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential)], transport=Mock(send=send))
    await pipeline.run(HttpRequest("POST", url, content=b"body"))
    await pipeline.run(HttpRequest("POST", alias, content=b"body"))
    assert len(requests) == 3
    credential.get_token.assert_called_once_with(scope, claims=None, enable_cae=True)
    # A new policy must also use the cached challenge directly, without another unauthenticated request.
    await AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential)], transport=Mock(send=send)).run(
        HttpRequest("POST", alias, content=b"body")
    )
    assert len(requests) == 4
    assert credential.get_token.call_count == 2
    assert credential.get_token.call_args.kwargs == {"enable_cae": True}
    assert HttpChallengeCache.get_challenge_for_url(alias) is HttpChallengeCache.get_challenge_for_url(url)


@pytest.mark.asyncio
async def test_cached_cae_scope_and_tenant_refresh():
    url = get_random_url()
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    policy = AsyncChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    scope = "https://vault.azure.net/.default"
    for header, tenant, claims in [
        (f'Bearer authorization="https://authority.net/first", scope={scope}', "first", None),
        ('Bearer authorization="https://authority.net/", claims="e30="', "first", "{}"),
        (f'Bearer authorization="https://authority.net/second", scope={scope}', "second", None),
    ]:
        response = PipelineResponse(
            request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
        )
        assert await policy.on_challenge(request, response)
        credential.get_token.assert_called_with(scope, claims=claims, tenant_id=tenant, enable_cae=True)
    policy._token = None
    await policy.on_request(request)
    credential.get_token.assert_called_with(scope, tenant_id="second", enable_cae=True)


@pytest.mark.parametrize(
    "resource",
    [
        "http://vault.azure.net",
        "http://vault.azure.net:443",
        "spn://vault.azure.net",
        "//vault.azure.net",
        "https://vault.azure.net/scope",
    ],
)
@pytest.mark.asyncio
async def test_cached_resource_syntax_is_preserved(resource):
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", resource={resource}')
    )
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    await AsyncChallengeAuthPolicy(credential).on_request(request)
    credential.get_token.assert_called_once_with(resource + "/.default", tenant_id="tenant", enable_cae=True)
    assert request.http_request.headers["Authorization"] == "Bearer token"


@pytest.mark.parametrize("method,body", [("PUT", b"payload"), ("HEAD", None), ("HEAD", b"payload")])
@pytest.mark.parametrize("warm_cache", [False, True])
@pytest.mark.parametrize("refill_cache", [False, True])
@pytest.mark.asyncio
async def test_retry_cache_eviction_preserves_request(method, body, warm_cache, refill_cache):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    if warm_cache:
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    policy = AsyncChallengeAuthPolicy(credential)
    other_credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("other", time.time() + 3600))
    )
    other = AsyncPipeline(
        policies=[AsyncChallengeAuthPolicy(other_credential)],
        transport=Mock(
            send=AsyncMock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))
        ),
    )
    stages = (
        [(True, 503, "evict"), (False, 503, "refill"), (True, 200, None)]
        if refill_cache
        else [
            (True, 503, "evict"),
            (False, 503, None),
            (False, 401, None),
            (True, 503, "evict"),
            (False, 401, None),
            (True, 200, None),
        ]
    )
    if not warm_cache:
        stages.insert(0, (False, 401, None))

    async def send(request):
        if not stages:
            assert (request.method, request.url, request.body) == ("GET", url + "/next", None)
            return Mock(status_code=200, headers={})
        authenticated, status, action = stages.pop(0)
        assert (request.method, request.url) == (method, url)
        if authenticated:
            assert request.headers["Authorization"] == "Bearer token"
            assert request.body == body
        else:
            assert "Authorization" not in request.headers
            assert not request.body
            if body:
                assert request.headers["Content-Length"] == "0"
        if action == "evict":
            assert (await other.run(HttpRequest("GET", url + "/other"))).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
        elif action == "refill":
            HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
        return Mock(status_code=status, headers={"WWW-Authenticate": header} if status == 401 else {})

    pipeline = AsyncPipeline(
        policies=[AsyncRetryPolicy(retry_total=5, retry_status=5, retry_backoff_factor=0), policy],
        transport=Mock(send=send),
    )
    assert (await pipeline.run(HttpRequest(method, url, content=body))).http_response.status_code == 200
    assert not stages
    assert (await pipeline.run(HttpRequest("GET", url + "/next"))).http_response.status_code == 200


@pytest.mark.parametrize("initial", ["cached", "fresh", "refresh", "refresh-tenantless"])
@pytest.mark.parametrize("cache_change", ["evict", "replace-valid", "replace-invalid"])
@pytest.mark.parametrize(
    "new_tenant,new_scope",
    [
        (None, None),
        ("new-tenant", None),
        (None, "https://vault.azure.net/new-scope"),
        ("new-tenant", "https://vault.azure.net/new-scope"),
    ],
)
@pytest.mark.asyncio
async def test_cae_request_snapshot_survives_cache_changes(initial, cache_change, new_tenant, new_scope):
    url = get_random_url()
    old_scope = "https://vault.azure.net/.default"
    if initial != "fresh":
        HttpChallengeCache.set_challenge_for_url(
            url, HttpChallenge(url, f'Bearer authorization="https://authority.net/old-tenant", scope={old_scope}')
        )
    active_scope = "https://vault.azure.net/refreshed-scope" if initial.startswith("refresh") else old_scope
    active_tenant = (
        None if initial == "refresh-tenantless" else "refreshed-tenant" if initial == "refresh" else "old-tenant"
    )
    full_header = f'Bearer authorization="https://authority.net/{active_tenant or ""}", scope={active_scope}'
    claims_header = f'Bearer authorization="https://authority.net/{new_tenant or ""}", claims="e30="'
    if new_scope:
        claims_header += f", scope={new_scope}"
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    other_credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("other", time.time() + 3600))
    )
    other = AsyncPipeline(
        policies=[AsyncChallengeAuthPolicy(other_credential)],
        transport=Mock(
            send=AsyncMock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))
        ),
    )
    full_challenge_pending = initial != "cached"
    claims_pending = True

    async def send(request):
        nonlocal full_challenge_pending, claims_pending
        if full_challenge_pending:
            full_challenge_pending = False
            assert bool(request.headers.get("Authorization")) == initial.startswith("refresh")
            return Mock(status_code=401, headers={"WWW-Authenticate": full_header})
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == b"payload"
        if claims_pending:
            claims_pending = False
            assert (await other.run(HttpRequest("GET", url + "/other"))).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
            if cache_change != "evict":
                replacement = "https://other.example/.default" if cache_change == "replace-invalid" else old_scope
                HttpChallengeCache.set_challenge_for_url(
                    url,
                    HttpChallenge(
                        url, f'Bearer authorization="https://authority.net/other-tenant", scope={replacement}'
                    ),
                )
            return Mock(status_code=401, headers={"WWW-Authenticate": claims_header})
        return Mock(status_code=200, headers={})

    pipeline = AsyncPipeline(
        policies=[AsyncRetryPolicy(retry_backoff_factor=0), AsyncChallengeAuthPolicy(credential)],
        transport=Mock(send=send),
    )
    assert (await pipeline.run(HttpRequest("PUT", url, content=b"payload"))).http_response.status_code == 200
    credential.get_token.assert_called_with(active_scope, tenant_id=active_tenant, claims="{}", enable_cae=True)
    cached = HttpChallengeCache.get_challenge_for_url(url)
    assert cached.get_scope() == active_scope
    assert cached.tenant_id == active_tenant


@pytest.mark.parametrize(
    "target", ["same-path", "same-case", "default-port", "other-host", "other-port", "other-scheme"]
)
@pytest.mark.asyncio
async def test_cae_request_snapshot_is_origin_bound(target):
    url = get_random_url()
    parsed = urlparse(url)
    targets = {
        "same-path": url + "/redirected",
        "same-case": f"https://{parsed.netloc.upper()}{parsed.path}",
        "default-port": f"https://{parsed.netloc.upper()}:443{parsed.path}",
        "other-host": get_random_url(),
        "other-port": f"https://{parsed.netloc}:8443{parsed.path}",
        "other-scheme": url.replace("https://", "http://", 1),
    }
    redirect_url = targets[target]
    scope = "https://vault.azure.net/.default"
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", scope={scope}')
    )
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    requests = []

    async def send(request):
        requests.append(request.url)
        if len(requests) == 1:
            if target != "other-scheme":
                HttpChallengeCache.remove_challenge_for_url(url)
            return Mock(status_code=307, headers={"location": redirect_url})
        assert request.url == redirect_url
        if len(requests) == 2:
            return Mock(
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/", claims="e30="'},
            )
        return Mock(status_code=200, headers={})

    pipeline = AsyncPipeline(
        policies=[AsyncRetryPolicy(retry_total=0), AsyncChallengeAuthPolicy(credential), AsyncRedirectPolicy()],
        transport=Mock(send=send),
    )
    if target.startswith("other"):
        with pytest.raises(ServiceRequestError if target == "other-scheme" else ValueError):
            await pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1
    else:
        assert (await pipeline.run(HttpRequest("GET", url))).http_response.status_code == 200
        credential.get_token.assert_called_with(scope, tenant_id="tenant", claims="{}", enable_cae=True)
        assert credential.get_token.call_count == 2


@pytest.mark.asyncio
async def test_cae_does_not_inherit_tenant_from_invalid_cache():
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url,
        HttpChallenge(url, 'Bearer authorization="https://authority.net/untrusted", resource=https://other.example'),
    )
    credential = Mock(spec_set=["get_token"])
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    response = PipelineResponse(
        request.http_request,
        Mock(
            status_code=401,
            headers={
                "WWW-Authenticate": 'Bearer authorization="https://authority.net/", scope=https://vault.azure.net/.default, claims="e30="'
            },
        ),
        request.context,
    )
    with pytest.raises(ValueError):
        await AsyncChallengeAuthPolicy(credential).on_challenge(request, response)
    credential.get_token.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("redirect_status", [303, 307])
@pytest.mark.asyncio
async def test_discovery_replay_preserves_redirect_target(redirect_status):
    url = get_random_url()
    redirect_url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    other = AsyncPipeline(
        policies=[AsyncChallengeAuthPolicy(credential)],
        transport=Mock(
            send=AsyncMock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))
        ),
    )
    requests = []

    async def send(request):
        requests.append(request.url)
        if len(requests) == 1:
            assert (request.method, request.url, request.body) == ("PUT", url, b"payload")
            assert request.headers["Authorization"] == "Bearer token"
            assert (await other.run(HttpRequest("GET", url + "/other"))).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
            return Mock(status_code=503, headers={})
        if len(requests) == 2:
            assert (request.method, request.url) == ("PUT", url)
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(status_code=redirect_status, headers={"location": redirect_url})
        assert request.url == redirect_url
        assert request.method == ("GET" if redirect_status == 303 else "PUT")
        if len(requests) == 3:
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(
                status_code=401,
                headers={
                    "WWW-Authenticate": 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
                },
            )
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == (None if redirect_status == 303 else b"payload")
        return Mock(status_code=200, headers={})

    pipeline = AsyncPipeline(
        policies=[
            AsyncRetryPolicy(retry_total=1, retry_backoff_factor=0),
            AsyncChallengeAuthPolicy(credential),
            AsyncRedirectPolicy(),
        ],
        transport=Mock(send=send),
    )
    assert (await pipeline.run(HttpRequest("PUT", url, content=b"payload"))).http_response.status_code == 200
    assert len(requests) == 4


@pytest.mark.parametrize("warm_cache", [False, True])
@pytest.mark.parametrize("target_cache", [False, True])
@pytest.mark.parametrize("redirect_status", [303, 307])
@pytest.mark.asyncio
async def test_discovery_replay_preserves_redirect_headers(warm_cache, target_cache, redirect_status):
    request, send, requests = redirect_replay_case(warm_cache, target_cache, redirect_status)
    credential = Mock(
        spec_set=["get_token"], get_token=AsyncMock(return_value=AccessToken("token", time.time() + 3600))
    )
    pipeline = AsyncPipeline(
        policies=[
            AsyncRedirectPolicy(redirect_remove_headers=["x-sensitive"]),
            AsyncRetryPolicy(retry_total=1, retry_backoff_factor=0),
            AsyncChallengeAuthPolicy(credential),
            SensitiveHeaderCleanupPolicy(),
        ],
        transport=Mock(send=AsyncMock(side_effect=send)),
    )
    assert (await pipeline.run(request)).http_response.status_code == 200
    assert len(requests) == 2 + int(warm_cache) + int(not target_cache)
