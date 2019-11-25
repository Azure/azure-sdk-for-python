# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest
from azure.keyvault.keys._shared import ChallengeAuthPolicy, HttpChallenge, HttpChallengeCache
import pytest

from keys_helpers import mock_response, Request, validating_transport


def test_challenge_cache():
    # ensure the test starts with an empty cache
    HttpChallengeCache.clear()

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


def test_policy():
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


def test_policy_updates_cache():
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
    transport = validating_transport(
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
    credential = Mock(get_token=lambda _: AccessToken(next(tokens), 0))
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=transport)

    # policy should complete and cache the first challenge
    pipeline.run(HttpRequest("GET", url))

    # The next request will receive a challenge. The policy should handle it and update the cache entry.
    pipeline.run(HttpRequest("GET", url))
