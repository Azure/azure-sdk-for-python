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

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest
from azure.keyvault.keys._shared import ChallengeAuthPolicy, HttpChallenge, HttpChallengeCache

from keys_helpers import mock_response, Request, validating_transport


def empty_challenge_cache(fn):
    @functools.wraps(fn)
    def wrapper():
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return fn()

    return wrapper


@empty_challenge_cache
def test_challenge_cache():
    url_a = "https://azure.service.a"
    challenge_a = HttpChallenge(url_a, "Bearer authorization=authority A, resource=resource A")

    url_b = "https://azure.service.b"
    challenge_b = HttpChallenge(url_b, "Bearer authorization=authority B, resource=resource B")

    for url, challenge in zip((url_a, url_b), (challenge_a, challenge_b)):
        HttpChallengeCache.set_challenge_for_url(url, challenge)
        assert HttpChallengeCache.get_challenge_for_url(url) == challenge
        assert HttpChallengeCache.get_challenge_for_url(url + "/some/path") == challenge
        assert HttpChallengeCache.get_challenge_for_url(url + "/some/path?with-query=string") == challenge
        assert HttpChallengeCache.get_challenge_for_url(url + ":443") == challenge

        HttpChallengeCache.remove_challenge_for_url(url)
        assert not HttpChallengeCache.get_challenge_for_url(url)


def test_challenge_parsing():
    authority = "https://login.authority.net/tenant"
    resource = "https://challenge.resource"
    challenge = HttpChallenge(
        "https://request.uri", challenge="Bearer authorization={}, resource={}".format(authority, resource)
    )

    assert challenge.get_authorization_server() == authority
    assert challenge.get_resource() == resource


@empty_challenge_cache
def test_policy():
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

    def send(request):
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

    def get_token(*scopes):
        assert len(scopes) is 1
        assert scopes[0] == expected_scope
        return AccessToken(expected_token, 0)

    credential = Mock(get_token=Mock(wraps=get_token))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
    pipeline.run(HttpRequest("POST", "https://azure.service", data=data))

    assert credential.get_token.call_count == 1


@empty_challenge_cache
def test_policy_updates_cache():
    """
    It's possible for the challenge returned for a request to change, e.g. when a vault is moved to a new tenant.
    When the policy receives a 401, it should update the cached challenge for the requested URL, if one exists.
    """

    url = "https://azure.service/path"
    first_scope = "https://first-scope"
    first_token = "first-scope-token"
    second_scope = "https://second-scope"
    second_token = "second-scope-token"
    challenge_fmt = 'Bearer authorization="https://login.authority.net/tenant", resource={}'

    # mocking a tenant change:
    # 1. first request -> respond with challenge
    # 2. second request should be authorized according to the challenge
    # 3. third request should match the second (using a cached access token)
    # 4. fourth request should also match the second -> respond with a new challenge
    # 4. fifth request should be authorized according to the new challenge
    # 5. sixth request should match the fifth
    transport = validating_transport(
        requests=(
            Request(url),
            Request(url, required_headers={"Authorization": "Bearer {}".format(first_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(first_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(first_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(second_token)}),
            Request(url, required_headers={"Authorization": "Bearer {}".format(second_token)}),
        ),
        responses=(
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt.format(first_scope)}),
            mock_response(status_code=200),
            mock_response(status_code=200),
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt.format(second_scope)}),
            mock_response(status_code=200),
            mock_response(status_code=200),
        ),
    )

    credential = Mock(get_token=Mock(return_value=AccessToken(first_token, time.time() + 3600)))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=transport)

    # policy should complete and cache the first challenge and access token
    for _ in range(2):
        pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1

    # The next request will receive a new challenge. The policy should handle it and update caches.
    credential.get_token.return_value = AccessToken(second_token, time.time() + 3600)
    for _ in range(2):
        pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 2


@empty_challenge_cache
def test_token_expiration():
    """policy should not use a cached token which has expired"""

    expires_on = time.time() + 3600
    first_token = "*"
    second_token = "**"

    token = AccessToken(first_token, expires_on)
    def get_token(*_, **__):
        return token

    credential = Mock(get_token=Mock(wraps=get_token))
    transport = validating_transport(
        requests=[
            Request(),
            Request(required_headers={"Authorization": "Bearer " + first_token}),
            Request(required_headers={"Authorization": "Bearer " + first_token}),
            Request(required_headers={"Authorization": "Bearer " + second_token}),
        ],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": 'Bearer authorization="https://a/b", resource=foo'}
            )
        ]
        + [mock_response()] * 3,
    )
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=transport)

    for _ in range(2):
        pipeline.run(HttpRequest("GET", "https://a/b"))
        assert credential.get_token.call_count == 1

    token = AccessToken(second_token, time.time() + 3600)
    with patch("time.time", lambda: expires_on):
        pipeline.run(HttpRequest("GET", "https://a/b"))
    assert credential.get_token.call_count == 2
