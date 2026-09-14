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
from uuid import uuid4

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.pipeline import Pipeline
from azure.core.rest import HttpRequest
from azure.keyvault.securitydomain._internal import ChallengeAuthPolicy, HttpChallenge, HttpChallengeCache

TOKEN_TYPES = [AccessToken, AccessTokenInfo]


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
def test_rejected_challenge_is_not_cached():
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


ENTRA_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd022db57"
DSTS_TENANT_ID = "de763a21-49f7-4b08-a8e1-52c8fbc103b4"
DSTS_AUTHORITY = "https://uswest2-passive-dsts.dsts.core.windows.net"


@pytest.mark.parametrize(
    "authority,expected_tenant",
    [
        (f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}", ENTRA_TENANT_ID),
        (f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/authorize", ENTRA_TENANT_ID),
        (f"{DSTS_AUTHORITY}/dstsv2/{DSTS_TENANT_ID}", DSTS_TENANT_ID),
        (f"{DSTS_AUTHORITY}/DSTSv2/{DSTS_TENANT_ID}/", DSTS_TENANT_ID),
        # a DSTSv2 authority without a tenant segment keeps the previous behavior
        (f"{DSTS_AUTHORITY}/dstsv2", "dstsv2"),
        ("https://login.microsoftonline.com/", None),
    ],
)
def test_challenge_parsing_tenant_id(authority, expected_tenant):
    """The tenant ID should be parsed from both Microsoft Entra ID and DSTSv2 authorization URIs"""

    challenge = HttpChallenge(
        "https://request.uri", challenge=f'Bearer authorization="{authority}", resource=https://vault.azure.net'
    )

    assert challenge.get_authorization_server() == authority
    assert challenge.tenant_id == expected_tenant


@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_tenant_dstsv2(token_type):
    """The policy's token requests should pass the tenant ID that follows the "dstsv2" segment of the authority"""

    expected_token = "expected_token"
    authority = f"{DSTS_AUTHORITY}/dstsv2/{DSTS_TENANT_ID}"
    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{authority}", resource=https://vault.azure.net'},
    )

    class Requests:
        count = 0

    def send(request):
        Requests.count += 1
        if Requests.count == 1:
            # first request should be unauthorized
            assert "Authorization" not in request.headers
            return challenge
        elif Requests.count == 2:
            # second request should be authorized according to the challenge
            assert expected_token in request.headers["Authorization"]
            return Mock(status_code=200)
        raise ValueError("unexpected request")

    def get_token(*_, options=None, **kwargs):
        options_bag = options if options else kwargs
        assert options_bag.get("tenant_id") == DSTS_TENANT_ID
        return token_type(expected_token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
    pipeline.run(HttpRequest("GET", get_random_url()))

    assert Requests.count == 2
    if hasattr(credential, "get_token"):
        assert credential.get_token.call_count == 1
    else:
        assert credential.get_token_info.call_count == 1
