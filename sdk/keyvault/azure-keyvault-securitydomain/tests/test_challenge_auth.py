# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""

import functools
from itertools import product
import time
from unittest.mock import AsyncMock, Mock
from urllib.parse import urlparse
from uuid import uuid4

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline, Pipeline, PipelineContext, PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import (
    AsyncRedirectPolicy,
    AsyncRetryPolicy,
    RedirectPolicy,
    RetryPolicy,
    SensitiveHeaderCleanupPolicy,
)
from azure.core.rest import HttpRequest
from azure.keyvault.securitydomain._internal import ChallengeAuthPolicy, HttpChallenge, HttpChallengeCache
from azure.keyvault.securitydomain._internal.async_challenge_auth_policy import AsyncChallengeAuthPolicy, await_result

TOKEN_TYPES = [AccessToken, AccessTokenInfo]
CHALLENGE = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
BACKSLASH_AUTHORITIES = [
    r"example.net\.vault.azure.net",
    r"example.net\\.vault.azure.net",
    r"example.net\@test.vault.azure.net",
    r"example.net\\@test.vault.azure.net",
]
BACKSLASH_CACHE_CASES = [(authority, "empty") for authority in BACKSLASH_AUTHORITIES] + [
    (BACKSLASH_AUTHORITIES[1], "challenge"),
    (BACKSLASH_AUTHORITIES[3], "token"),
]
VALID_CACHED_URLS = [
    "https://test.vault.azure.net:443/securitydomain/item",
    "https://test.managedhsm.azure.net:8443/securitydomain/item",
    "HTTPS://VAULT.CONTOSO.TEST:8443/securitydomain/item",
    "https://localhost/securitydomain/item",
    "https://[::1]/securitydomain/item",
    "https://[::1]:443/securitydomain/item",
    "https://[2001:db8::1]:8443/securitydomain/item",
    r"https://test.vault.azure.net/securitydomain/a\b",
    r"https://test.vault.azure.net/securitydomain/item?value=a\b",
    r"https://test.vault.azure.net/securitydomain/item#fragment=a\b",
]
VALID_CHALLENGE_AUTHORITIES = [
    (f"test.{domain}", domain, "tenant")
    for domain in [
        "vault.azure.net",
        "vault.usgovcloudapi.net",
        "vault.azure.cn",
        "vault.microsoftazure.de",
        "managedhsm.azure.net",
        "managedhsm.usgovcloudapi.net",
        "managedhsm.azure.cn",
        "managedhsm.microsoftazure.de",
    ]
] + [
    ("vault.contoso.test", "contoso.test", "tenant"),
    ("vault.contoso.test", "contoso.test", "adfs"),
    ("TEST.VAULT.AZURE.NET", "VAULT.AZURE.NET", "tenant"),
    ("user:pass@test.vault.azure.net", "vault.azure.net", "tenant"),
    ("t" + chr(0xE4) + "st.vault.azure.net", "vault.azure.net", "tenant"),
    ("xn--tst-qla.vault.azure.net", "vault.azure.net", "tenant"),
]


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


def get_random_url():
    """The challenge cache is keyed on URLs. Random URLs defend against tests interfering with each other."""

    return f"https://{uuid4()}.vault.azure.net/{uuid4()}".replace("-", "")


@empty_challenge_cache
@pytest.mark.parametrize("authority,cache_state", BACKSLASH_CACHE_CASES)
@pytest.mark.parametrize("verify_challenge_resource", [True, False])
def test_rejects_backslash_authority(authority, cache_state, verify_challenge_resource):
    url = f"https://{authority}/securitydomain/canary"
    credential = Mock(spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request")))
    transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport send")))
    policy = ChallengeAuthPolicy(credential, verify_challenge_resource=verify_challenge_resource)
    pipeline = Pipeline(policies=[policy], transport=transport)
    if cache_state != "empty":
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, CHALLENGE))
    if cache_state == "token":
        policy._token = AccessToken("cached-token", time.time() + 3600)
    cached = HttpChallengeCache._cache.copy()

    for _ in range(2):
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        with pytest.raises(ValueError, match="backslash"):
            pipeline.run(request)
        assert "Authorization" not in request.headers
        assert request.body == b"secret"
        assert HttpChallengeCache._cache == cached

    credential.get_token.assert_not_called()
    transport.send.assert_not_called()


@empty_challenge_cache
@pytest.mark.parametrize("authority", BACKSLASH_AUTHORITIES)
@pytest.mark.parametrize("verify_challenge_resource", [True, False])
def test_rejects_backslash_authority_on_challenge(authority, verify_challenge_resource):
    url = f"https://{authority}/securitydomain/canary"
    credential = Mock(spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request")))
    policy = ChallengeAuthPolicy(credential, verify_challenge_resource=verify_challenge_resource)
    transport = Mock()
    response = Mock(http_response=Mock(status_code=401, headers={"WWW-Authenticate": CHALLENGE}))

    for _ in range(2):
        request = PipelineRequest(HttpRequest("GET", url), PipelineContext(transport))
        with pytest.raises(ValueError, match="backslash"):
            policy.on_challenge(request, response)
        assert "Authorization" not in request.http_request.headers
        assert not HttpChallengeCache._cache

    credential.get_token.assert_not_called()
    transport.send.assert_not_called()


@empty_challenge_cache
@pytest.mark.parametrize("url", VALID_CACHED_URLS)
def test_request_url_validation_preserves_cached_urls(url):
    # These URL-only fixtures deliberately use an unrelated challenge resource.
    challenge = HttpChallenge(url, CHALLENGE)
    HttpChallengeCache.set_challenge_for_url(url, challenge)
    credential = Mock(spec_set=["get_token"])
    policy = ChallengeAuthPolicy(credential, verify_challenge_resource=False)
    policy._token = AccessToken("cached-token", time.time() + 3600)

    for _ in range(2):
        request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
        policy.on_request(request)
        assert request.http_request.url == url
        assert request.http_request.headers["Authorization"] == "Bearer cached-token"
        assert HttpChallengeCache.get_challenge_for_url(url) is challenge

    credential.get_token.assert_not_called()


@empty_challenge_cache
@pytest.mark.parametrize("authority,resource,tenant", VALID_CHALLENGE_AUTHORITIES)
def test_request_url_validation_preserves_challenge_flow(authority, resource, tenant):
    url = f"https://{authority}/securitydomain/item"
    challenge = Mock(
        status_code=401,
        headers={
            "WWW-Authenticate": f'Bearer authorization="https://authority.net/{tenant}", resource=https://{resource}'
        },
    )

    def send(request):
        assert request.url == url
        if "Authorization" not in request.headers:
            assert not request.body
            assert request.headers["Content-Length"] == "0"
            return challenge
        assert request.headers["Authorization"] == "Bearer expected-token"
        assert request.body == b"secret"
        return Mock(status_code=200)

    credential = Mock(
        spec_set=["get_token"], get_token=Mock(return_value=AccessToken("expected-token", time.time() + 3600))
    )
    transport = Mock(send=Mock(wraps=send))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=transport)
    for _ in range(2):
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        assert pipeline.run(request).http_response.status_code == 200

    assert transport.send.call_count == 3
    credential.get_token.assert_called_once()
    assert credential.get_token.call_args.args == (f"https://{resource}/.default",)
    if tenant == "adfs":
        assert "tenant_id" not in credential.get_token.call_args.kwargs
    else:
        assert credential.get_token.call_args.kwargs["tenant_id"] == tenant
    assert HttpChallengeCache.get_challenge_for_url(url).get_resource() == f"https://{resource}"


@empty_challenge_cache
@pytest.mark.parametrize("fresh_policy", [False, True])
def test_rejected_challenge_is_not_cached(fresh_policy):
    url = "https://example.net/securitydomain/canary"
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
        if fresh_policy:
            pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", url)
        request.set_bytes_body(b"secret")
        with pytest.raises(ValueError):
            pipeline.run(request)

    assert Requests.count == 2
    assert not HttpChallengeCache.get_challenge_for_url(url)
    assert credential.get_token.call_count == 0


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_request_body_not_reused_across_requests(token_type):
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


# These domains include the public/China/US Government cloud tables in eng/common/TestResources/clouds,
# Germany, Managed HSM, and arbitrary Azure Stack/custom domains supported by the suffix validator.
CACHE_RESOURCE_DOMAINS = [
    "vault.azure.net",
    "vault.azure.cn",
    "vault.usgovcloudapi.net",
    "vault.microsoftazure.de",
    "managedhsm.azure.net",
    "vault.stack.example",
    "vault.custom.example",
]
INVALID_CHALLENGE_HEADERS = [
    None,
    "",
    " ",
    "Bearer",
    "Bearer resource=https://vault.azure.net",
    'Bearer authorization="https://authority.net/tenant", resource=https://other.example',
    'Bearer authorization="https://authority.net/tenant", scope=invalid',
    'Bearer authorization="https://authority.net/tenant", scope=https://[invalid',
]


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
def test_cached_challenge_resource_is_verified(token_type, cached_token, request_port, resource):
    url = get_random_url().replace(".vault.azure.net/", f".vault.azure.net{request_port}/")
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", resource={resource}')
    )
    credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=Mock(side_effect=AssertionError("unexpected token request")),
        get_token_info=Mock(side_effect=AssertionError("unexpected token request")),
    )
    policy = ChallengeAuthPolicy(credential)
    if cached_token:
        policy._token = token_type("cached-token", time.time() + 3600)
    transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport call")))
    request = HttpRequest("POST", url, content=b"secret")

    with pytest.raises(ValueError):
        Pipeline(policies=[policy], transport=transport).run(request)

    assert "Authorization" not in request.headers
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()
    transport.send.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None

    follow_up = PipelineRequest(HttpRequest("POST", url, content=b"next secret"), PipelineContext(None))
    policy.on_request(follow_up)
    response = PipelineResponse(
        follow_up.http_request, Mock(status_code=401, headers={"WWW-Authenticate": "Bearer"}), follow_up.context
    )
    assert policy.on_challenge(follow_up, response) is False
    assert "Authorization" not in follow_up.http_request.headers
    assert not follow_up.http_request.body
    assert follow_up.http_request.headers["Content-Length"] == "0"
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()


@pytest.mark.parametrize("cached_token", [False, True])
def test_opt_out_cache_is_not_trusted_by_strict_policy(cached_token):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://other.example'
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("opt-out", time.time() + 3600)))
    transport = Mock(
        send=Mock(
            side_effect=[
                Mock(status_code=401, headers={"WWW-Authenticate": header}),
                Mock(status_code=200),
                Mock(status_code=200),
            ]
        )
    )
    pipeline = Pipeline(
        policies=[ChallengeAuthPolicy(credential, verify_challenge_resource=False)], transport=transport
    )
    pipeline.run(HttpRequest("GET", url))
    pipeline.run(HttpRequest("GET", url))
    assert transport.send.call_count == 3
    credential.get_token.assert_called_once()
    assert HttpChallengeCache.get_challenge_for_url(url)

    strict_credential = Mock(
        spec_set=["get_token"], get_token=Mock(side_effect=AssertionError("unexpected token request"))
    )
    strict_policy = ChallengeAuthPolicy(strict_credential)
    if cached_token:
        strict_policy._token = AccessToken("strict-token", time.time() + 3600)
    strict_transport = Mock(send=Mock(side_effect=AssertionError("unexpected transport call")))
    with pytest.raises(ValueError):
        Pipeline(policies=[strict_policy], transport=strict_transport).run(HttpRequest("GET", url))
    strict_credential.get_token.assert_not_called()
    strict_transport.send.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("header", INVALID_CHALLENGE_HEADERS)
def test_rejected_response_preserves_concurrent_challenge(header):
    url = get_random_url()
    credential = Mock(spec_set=["get_token"])
    policy = ChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("POST", url, content=b"secret"), PipelineContext(None))
    policy.on_request(request)
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
            policy.on_challenge(request, response)
    else:
        assert policy.on_challenge(request, response) is False
    assert HttpChallengeCache.get_challenge_for_url(url) is replacement
    assert "Authorization" not in request.http_request.headers
    assert not request.http_request.body
    credential.get_token.assert_not_called()

    def send(fresh_request):
        assert "Authorization" not in fresh_request.headers
        assert not fresh_request.body
        assert fresh_request.headers["Content-Length"] == "0"
        return Mock(status_code=401, headers={})

    # Start a separate cold-discovery scenario, independent of the concurrent cache entry.
    HttpChallengeCache.remove_challenge_for_url(url)
    fresh = Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=Mock(send=send))
    assert fresh.run(HttpRequest("POST", url, content=b"new secret")).http_response.status_code == 401
    credential.get_token.assert_not_called()


@pytest.mark.parametrize("header", ["", " ", "Bearer", "Bearer resource=https://vault.azure.net"])
@pytest.mark.parametrize("consecutive", [False, True])
def test_malformed_challenge_flow_clears_cache(header, consecutive):
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net')
    )
    credential = Mock(spec_set=["get_token"])
    policy = ChallengeAuthPolicy(credential)
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    policy._token = AccessToken("token", time.time() + 3600)
    policy.on_request(request)
    response = PipelineResponse(
        request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": header}), request.context
    )
    assert policy.handle_challenge_flow(request, response, consecutive_challenge=consecutive) is response
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    credential.get_token.assert_not_called()


def test_cae_invalid_inherited_scope_clears_cache():
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
        ChallengeAuthPolicy(credential).on_challenge(request, response)
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    credential.get_token.assert_not_called()


@pytest.mark.parametrize("domain", CACHE_RESOURCE_DOMAINS)
@pytest.mark.parametrize("parameter", ["resource", "scope"])
@pytest.mark.parametrize(
    "request_port,resource_port", [("", ""), (":443", ""), ("", ":443"), (":443", ":443"), (":8443", ":8443")]
)
def test_valid_challenge_cache_reuse(domain, parameter, request_port, resource_port):
    host = f"{uuid4().hex}.{domain}"
    url = f"https://{host}{request_port}/first"
    alias_port = "" if request_port == ":443" else ":443" if not request_port else request_port
    alias = f"https://{host.upper()}{alias_port}/next"
    resource = f"https://{domain.upper()}{resource_port}"
    scope = resource + "/.default"
    header = f'Bearer authorization="https://authority.example/ADFS", {parameter}={scope if parameter == "scope" else resource}'
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    requests = []

    def send(request):
        requests.append(request)
        if len(requests) == 1:
            assert "Authorization" not in request.headers
            assert not request.body
            return Mock(status_code=401, headers={"WWW-Authenticate": header})
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == b"body"
        return Mock(status_code=200)

    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=Mock(send=send))
    pipeline.run(HttpRequest("POST", url, content=b"body"))
    pipeline.run(HttpRequest("POST", alias, content=b"body"))
    assert len(requests) == 3
    credential.get_token.assert_called_once_with(scope, claims=None, enable_cae=True)
    # A new policy must also use the cached challenge directly, without another unauthenticated request.
    Pipeline(policies=[ChallengeAuthPolicy(credential)], transport=Mock(send=send)).run(
        HttpRequest("POST", alias, content=b"body")
    )
    assert len(requests) == 4
    assert credential.get_token.call_count == 2
    assert credential.get_token.call_args.kwargs == {"enable_cae": True}
    assert HttpChallengeCache.get_challenge_for_url(alias) is HttpChallengeCache.get_challenge_for_url(url)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
@pytest.mark.parametrize("cached_token", [False, True])
@pytest.mark.parametrize("challenge_sequence", ["", "kv", "cae", "kv-cae"])
@pytest.mark.parametrize("fresh_policy", [False, True])
@pytest.mark.parametrize("verify_challenge_resource", [False, True])
async def test_missing_challenge_header_clears_cache_and_rediscovers(
    is_async, token_type, cached_token, challenge_sequence, fresh_policy, verify_challenge_resource
):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/old-tenant", resource=' + (
        "https://vault.azure.net" if verify_challenge_resource else "https://other.example"
    )
    new_header = 'Bearer authorization="https://authority.net/new-tenant", resource=https://vault.azure.net'
    claims_header = 'Bearer authorization="https://authority.net/old-tenant", claims="e30="'
    challenges = {"": [], "kv": [header], "cae": [claims_header], "kv-cae": [header, claims_header]}[challenge_sequence]
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    token_method = "get_token" if token_type == AccessToken else "get_token_info"
    token_mock = (AsyncMock if is_async else Mock)(return_value=token_type("accepted-token", time.time() + 3600))
    credential = Mock(spec_set=[token_method], **{token_method: token_mock})
    policy_type = AsyncChallengeAuthPolicy if is_async else ChallengeAuthPolicy
    policy = policy_type(credential, verify_challenge_resource=verify_challenge_resource)
    if cached_token:
        policy._token = token_type("accepted-token", time.time() + 3600)
    recovery_policy = (
        policy_type(credential, verify_challenge_resource=verify_challenge_resource) if fresh_policy else policy
    )
    if fresh_policy:
        recovery_policy._token = token_type("warm-token", time.time() + 3600)
    missing = Mock(status_code=401, headers={})
    sent_requests = []

    def send(request):
        sent_requests.append(request)
        attempt = len(sent_requests)
        if attempt <= 1 + len(challenges):
            assert request.headers["Authorization"] == "Bearer accepted-token"
            assert request.body == b"payload"
            return (
                Mock(status_code=401, headers={"WWW-Authenticate": challenges[attempt - 1]})
                if attempt <= len(challenges)
                else missing
            )
        if attempt == 2 + len(challenges):
            assert "Authorization" not in request.headers
            assert not request.body
            assert request.headers["Content-Length"] == "0"
            assert request.headers["x-current"] == "latest"
            request.headers["x-added"] = "retained"
            return Mock(status_code=401, headers={"WWW-Authenticate": new_header})
        assert request.url == url
        assert request.headers["Authorization"] == "Bearer accepted-token"
        assert request.body == b"payload"
        assert request.headers["Content-Length"] == "7"
        assert request.headers["x-current"] == "latest"
        assert request.headers["x-added"] == "retained"
        return Mock(status_code=200, headers={})

    transport = Mock(send=AsyncMock(wraps=send) if is_async else Mock(wraps=send))

    def pipeline(auth_policy):
        return (AsyncPipeline if is_async else Pipeline)(
            policies=[
                AsyncRedirectPolicy() if is_async else RedirectPolicy(),
                AsyncRetryPolicy(retry_total=0) if is_async else RetryPolicy(retry_total=0),
                auth_policy,
                SensitiveHeaderCleanupPolicy(),
            ],
            transport=transport,
        )

    response = (
        await pipeline(policy).run(HttpRequest("PUT", url, content=b"payload"))
        if is_async
        else pipeline(policy).run(HttpRequest("PUT", url, content=b"payload"))
    )
    assert response.http_response is missing
    assert policy._token is None
    assert len(sent_requests) == 1 + len(challenges)
    assert token_mock.call_count == int(not cached_token) + len(challenges)
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    next_request = HttpRequest(
        "PUT", url, headers={"Authorization": "Bearer stale", "x-current": "latest"}, content=b"payload"
    )
    response = (
        await pipeline(recovery_policy).run(next_request) if is_async else pipeline(recovery_policy).run(next_request)
    )
    assert response.http_response.status_code == 200
    assert len(sent_requests) == 3 + len(challenges)
    assert token_mock.call_count == int(not cached_token) + len(challenges) + 1
    assert token_mock.call_args.args == ("https://vault.azure.net/.default",)
    assert token_mock.call_args.kwargs.get("options", token_mock.call_args.kwargs)["tenant_id"] == "new-tenant"
    assert HttpChallengeCache.get_challenge_for_url(url).tenant_id == "new-tenant"


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
@pytest.mark.parametrize("cache_change", ["evict", "replace-valid", "replace-invalid"])
async def test_missing_challenge_header_preserves_inflight_cae_snapshot(is_async, token_type, cache_change):
    url = get_random_url()
    scope = "https://vault.azure.net/.default"
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/old-tenant", scope={scope}')
    )
    token_method = "get_token" if token_type == AccessToken else "get_token_info"
    token_mock = (AsyncMock if is_async else Mock)(return_value=token_type("token", time.time() + 3600))
    credential = Mock(spec_set=[token_method], **{token_method: token_mock})
    policy_type = AsyncChallengeAuthPolicy if is_async else ChallengeAuthPolicy
    active, other = policy_type(credential), policy_type(credential)
    request = PipelineRequest(HttpRequest("PUT", url, content=b"payload"), PipelineContext(None))
    other_request = PipelineRequest(HttpRequest("GET", url + "/other"), PipelineContext(None))
    if is_async:
        await active.on_request(request)
        await other.on_request(other_request)
    else:
        active.on_request(request)
        other.on_request(other_request)
    missing = PipelineResponse(other_request.http_request, Mock(status_code=401, headers={}), other_request.context)
    result = (
        await other.handle_challenge_flow(other_request, missing)
        if is_async
        else other.handle_challenge_flow(other_request, missing)
    )
    assert result is missing
    assert HttpChallengeCache.get_challenge_for_url(url) is None
    if cache_change != "evict":
        replacement = scope if cache_change == "replace-valid" else "https://other.example/.default"
        HttpChallengeCache.set_challenge_for_url(
            url, HttpChallenge(url, f'Bearer authorization="https://authority.net/other-tenant", scope={replacement}')
        )
    claims = PipelineResponse(
        request.http_request,
        Mock(
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    'Bearer authorization="https://authority.net/new-tenant", '
                    'scope=https://vault.azure.net/new-scope, claims="e30="'
                )
            },
        ),
        request.context,
    )
    authorized = await active.on_challenge(request, claims) if is_async else active.on_challenge(request, claims)
    assert authorized
    assert request.http_request.body == b"payload"
    assert token_mock.call_args.args == (scope,)
    options = token_mock.call_args.kwargs.get("options", token_mock.call_args.kwargs)
    assert options["tenant_id"] == "old-tenant"
    assert options["claims"] == "{}"


def redirect_replay_case(warm_cache, target_cache, redirect_status):
    url = get_random_url()
    target = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    if warm_cache:
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    requests = []

    def send(request):
        requests.append(request.url)
        if warm_cache and len(requests) == 1:
            assert request.body == b"payload"
            HttpChallengeCache.remove_challenge_for_url(url)
            return Mock(status_code=503, headers={})
        if request.url == url:
            assert not request.body
            assert request.headers["x-sensitive"] == "private"
            request.headers["x-current"] = "updated"
            request.headers["x-added"] = "retained"
            if target_cache:
                HttpChallengeCache.set_challenge_for_url(target, HttpChallenge(target, header))
            return Mock(status_code=redirect_status, headers={"location": target})
        assert request.url == target
        assert "x-sensitive" not in request.headers
        assert request.headers["x-current"] == "updated"
        assert request.headers["x-added"] == "retained"
        method = "GET" if redirect_status == 303 else "PUT"
        assert request.method == method
        if not target_cache and requests.count(target) == 1:
            assert not request.body
            return Mock(status_code=401, headers={"WWW-Authenticate": header})
        assert request.body == (None if redirect_status == 303 else b"payload")
        assert request.headers["Content-Length"] == ("0" if redirect_status == 303 else "7")
        return Mock(status_code=200, headers={})

    request = HttpRequest("PUT", url, headers={"x-sensitive": "private", "x-current": "original"}, content=b"payload")
    return request, send, requests


@pytest.mark.parametrize("warm_cache", [False, True])
@pytest.mark.parametrize("target_cache", [False, True])
@pytest.mark.parametrize("redirect_status", [303, 307])
def test_discovery_replay_preserves_redirect_headers(warm_cache, target_cache, redirect_status):
    request, send, requests = redirect_replay_case(warm_cache, target_cache, redirect_status)
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    pipeline = Pipeline(
        policies=[
            RedirectPolicy(redirect_remove_headers=["x-sensitive"]),
            RetryPolicy(retry_total=1, retry_backoff_factor=0),
            ChallengeAuthPolicy(credential),
            SensitiveHeaderCleanupPolicy(),
        ],
        transport=Mock(send=send),
    )
    assert pipeline.run(request).http_response.status_code == 200
    assert len(requests) == 2 + int(warm_cache) + int(not target_cache)


def test_cached_cae_scope_and_tenant_refresh():
    url = get_random_url()
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    policy = ChallengeAuthPolicy(credential)
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
        assert policy.on_challenge(request, response)
        credential.get_token.assert_called_with(scope, claims=claims, tenant_id=tenant, enable_cae=True)
    policy._token = None
    policy.on_request(request)
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
def test_cached_resource_syntax_is_preserved(resource):
    url = get_random_url()
    HttpChallengeCache.set_challenge_for_url(
        url, HttpChallenge(url, f'Bearer authorization="https://authority.net/tenant", resource={resource}')
    )
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    ChallengeAuthPolicy(credential).on_request(request)
    credential.get_token.assert_called_once_with(resource + "/.default", tenant_id="tenant", enable_cae=True)
    assert request.http_request.headers["Authorization"] == "Bearer token"


def test_cache_removal_is_idempotent():
    url = get_random_url()
    alias = url.replace(".vault.azure.net", ".VAULT.AZURE.NET:443")
    HttpChallengeCache.remove_challenge_for_url(url)
    challenge = HttpChallenge(
        url, 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    )
    HttpChallengeCache.set_challenge_for_url(url, challenge)
    HttpChallengeCache.remove_challenge_for_url(alias)
    HttpChallengeCache.remove_challenge_for_url(url)
    HttpChallengeCache.remove_challenge_for_url(alias)
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("method,body", [("PUT", b"payload"), ("HEAD", None), ("HEAD", b"payload")])
@pytest.mark.parametrize("warm_cache", [False, True])
@pytest.mark.parametrize("refill_cache", [False, True])
def test_retry_cache_eviction_preserves_request(method, body, warm_cache, refill_cache):
    url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    if warm_cache:
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    policy = ChallengeAuthPolicy(credential)
    other_credential = Mock(
        spec_set=["get_token"], get_token=Mock(return_value=AccessToken("other", time.time() + 3600))
    )
    other = Pipeline(
        policies=[ChallengeAuthPolicy(other_credential)],
        transport=Mock(send=Mock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))),
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

    def send(request):
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
            assert other.run(HttpRequest("GET", url + "/other")).http_response.status_code == 401
            assert HttpChallengeCache.get_challenge_for_url(url) is None
        elif action == "refill":
            HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
        return Mock(status_code=status, headers={"WWW-Authenticate": header} if status == 401 else {})

    pipeline = Pipeline(
        policies=[RetryPolicy(retry_total=5, retry_status=5, retry_backoff_factor=0), policy],
        transport=Mock(send=send),
    )
    assert pipeline.run(HttpRequest(method, url, content=body)).http_response.status_code == 200
    assert not stages
    assert pipeline.run(HttpRequest("GET", url + "/next")).http_response.status_code == 200


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
def test_cae_request_snapshot_survives_cache_changes(initial, cache_change, new_tenant, new_scope):
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
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    other_credential = Mock(
        spec_set=["get_token"], get_token=Mock(return_value=AccessToken("other", time.time() + 3600))
    )
    other = Pipeline(
        policies=[ChallengeAuthPolicy(other_credential)],
        transport=Mock(send=Mock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))),
    )
    full_challenge_pending = initial != "cached"
    claims_pending = True

    def send(request):
        nonlocal full_challenge_pending, claims_pending
        if full_challenge_pending:
            full_challenge_pending = False
            assert bool(request.headers.get("Authorization")) == initial.startswith("refresh")
            return Mock(status_code=401, headers={"WWW-Authenticate": full_header})
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == b"payload"
        if claims_pending:
            claims_pending = False
            assert other.run(HttpRequest("GET", url + "/other")).http_response.status_code == 401
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

    pipeline = Pipeline(
        policies=[RetryPolicy(retry_backoff_factor=0), ChallengeAuthPolicy(credential)], transport=Mock(send=send)
    )
    assert pipeline.run(HttpRequest("PUT", url, content=b"payload")).http_response.status_code == 200
    # Preserve CAE precedence: both accepted values override replacements supplied in the claims challenge.
    credential.get_token.assert_called_with(active_scope, tenant_id=active_tenant, claims="{}", enable_cae=True)
    cached = HttpChallengeCache.get_challenge_for_url(url)
    assert cached.get_scope() == active_scope
    assert cached.tenant_id == active_tenant


@pytest.mark.parametrize(
    "target", ["same-path", "same-case", "default-port", "other-host", "other-port", "other-scheme"]
)
def test_cae_request_snapshot_is_origin_bound(target):
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
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    requests = []

    def send(request):
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

    pipeline = Pipeline(
        policies=[RetryPolicy(), ChallengeAuthPolicy(credential), RedirectPolicy()], transport=Mock(send=send)
    )
    if target.startswith("other"):
        with pytest.raises(ServiceRequestError if target == "other-scheme" else ValueError):
            pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1
    else:
        assert pipeline.run(HttpRequest("GET", url)).http_response.status_code == 200
        credential.get_token.assert_called_with(scope, tenant_id="tenant", claims="{}", enable_cae=True)
        assert credential.get_token.call_count == 2


def test_cae_does_not_inherit_tenant_from_invalid_cache():
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
        ChallengeAuthPolicy(credential).on_challenge(request, response)
    credential.get_token.assert_not_called()
    assert HttpChallengeCache.get_challenge_for_url(url) is None


@pytest.mark.parametrize("redirect_status", [303, 307])
def test_discovery_replay_preserves_redirect_target(redirect_status):
    url = get_random_url()
    redirect_url = get_random_url()
    header = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, header))
    credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=AccessToken("token", time.time() + 3600)))
    other = Pipeline(
        policies=[ChallengeAuthPolicy(credential)],
        transport=Mock(send=Mock(return_value=Mock(status_code=401, headers={"WWW-Authenticate": "Bearer invalid=1"}))),
    )
    requests = []

    def send(request):
        requests.append(request.url)
        if len(requests) == 1:
            assert (request.method, request.url, request.body) == ("PUT", url, b"payload")
            assert request.headers["Authorization"] == "Bearer token"
            assert other.run(HttpRequest("GET", url + "/other")).http_response.status_code == 401
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

    pipeline = Pipeline(
        policies=[
            RetryPolicy(retry_total=1, retry_backoff_factor=0),
            ChallengeAuthPolicy(credential),
            RedirectPolicy(),
        ],
        transport=Mock(send=send),
    )
    assert pipeline.run(HttpRequest("PUT", url, content=b"payload")).http_response.status_code == 200
    assert len(requests) == 4
