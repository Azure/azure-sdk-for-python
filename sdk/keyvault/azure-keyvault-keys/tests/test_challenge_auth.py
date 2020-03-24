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
from uuid import uuid4

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.keyvault.keys._shared import ChallengeAuthPolicy, HttpChallenge, HttpChallengeCache

import pytest

from _shared.helpers import mock_response, Request, validating_transport


def empty_challenge_cache(fn):
    @functools.wraps(fn)
    def wrapper():
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        return fn()

    return wrapper


def get_random_url():
    """The challenge cache is keyed on URLs. Random URLs defend against tests interfering with each other."""

    return "https://{}/{}".format(uuid4(), uuid4()).replace("-", "")


@empty_challenge_cache
def test_enforces_tls():
    url = "http://not.secure"
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, "Bearer authorization=_, resource=_"))

    credential = Mock()
    pipeline = Pipeline(transport=Mock(), policies=[ChallengeAuthPolicy(credential)])
    with pytest.raises(ServiceRequestError):
        pipeline.run(HttpRequest("GET", url))


@empty_challenge_cache
def test_challenge_cache():
    url_a = get_random_url()
    challenge_a = HttpChallenge(url_a, "Bearer authorization=authority A, resource=resource A")

    url_b = get_random_url()
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
def test_scope():
    """The policy's token requests should always be for an AADv2 scope"""

    expected_content = b"a duck"

    def test_with_challenge(challenge, expected_scope):
        expected_token = "expected_token"

        class Requests:
            count = 0

        def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content
                assert not request.body
                assert request.headers["Content-Length"] == "0"
                return challenge
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        def get_token(*scopes):
            assert len(scopes) == 1
            assert scopes[0] == expected_scope
            return AccessToken(expected_token, 0)

        credential = Mock(get_token=Mock(wraps=get_token))
        pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        pipeline.run(request)

        assert credential.get_token.call_count == 1

    endpoint = "https://authority.net/tenant"

    # an AADv1 resource becomes an AADv2 scope with the addition of '/.default'
    resource = "https://challenge.resource"
    scope = resource + "/.default"

    challenge_with_resource = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="{}", resource={}'.format(endpoint, resource)},
    )

    challenge_with_scope = Mock(
        status_code=401, headers={"WWW-Authenticate": 'Bearer authorization="{}", scope={}'.format(endpoint, scope)}
    )

    test_with_challenge(challenge_with_resource, scope)
    test_with_challenge(challenge_with_scope, scope)


@empty_challenge_cache
def test_policy_updates_cache():
    """
    It's possible for the challenge returned for a request to change, e.g. when a vault is moved to a new tenant.
    When the policy receives a 401, it should update the cached challenge for the requested URL, if one exists.
    """

    url = get_random_url()
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
    # 5. fifth request should be authorized according to the new challenge
    # 6. sixth request should match the fifth
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

    url = get_random_url()

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
                status_code=401, headers={"WWW-Authenticate": 'Bearer authorization="{}", resource=foo'.format(url)}
            )
        ]
        + [mock_response()] * 3,
    )
    pipeline = Pipeline(policies=[ChallengeAuthPolicy(credential=credential)], transport=transport)

    for _ in range(2):
        pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1

    token = AccessToken(second_token, time.time() + 3600)
    with patch("time.time", lambda: expires_on):
        pipeline.run(HttpRequest("GET", url))
    assert credential.get_token.call_count == 2


@empty_challenge_cache
def test_preserves_options_and_headers():
    """After a challenge, the original request should be sent with its options and headers preserved.

    If a policy mutates the options or headers of the challenge (unauthorized) request, the options of the service
    request should be present when it is sent with authorization.
    """

    url = get_random_url()
    token = "**"

    def get_token(*_, **__):
        return AccessToken(token, 0)

    credential = Mock(get_token=Mock(wraps=get_token))

    transport = validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"Authorization": "Bearer " + token})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": 'Bearer authorization="{}", resource=foo'.format(url)}
            )
        ]
        + [mock_response()] * 2,
    )
    challenge_policy = ChallengeAuthPolicy(credential=credential)
    policies = get_policies_for_request_mutation_test(challenge_policy)
    pipeline = Pipeline(policies=policies, transport=transport)

    response = pipeline.run(HttpRequest("GET", url))

    # ensure the mock sans I/O policies were called
    for policy in policies:
        if hasattr(policy, "on_request"):
            assert policy.on_request.called, "mock policy wasn't invoked"


def get_policies_for_request_mutation_test(challenge_policy):
    # create mock policies to add, remove, and verify an option and header
    key = "foo"
    value = "bar"
    do_not_handle = lambda _: False

    def add(request):
        # add the expected option and header
        request.context.options[key] = value
        request.http_request.headers[key] = value

    adder = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(wraps=add), on_exception=do_not_handle)

    def remove(request):
        # remove expected header and all options of unauthorized (challenge) requests
        if not request.http_request.headers.get("Authorization"):
            request.http_request.headers.pop(key, None)
            request.context.options = {}

    remover = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(wraps=remove), on_exception=do_not_handle)

    def verify(request):
        # authorized (non-challenge) requests should have the expected option and header
        if request.http_request.headers.get("Authorization"):
            assert request.context.options.get(key) == value, "request option not preserved across challenge"
            assert request.http_request.headers.get(key) == value, "headers not preserved across challenge"

    verifier = Mock(spec=SansIOHTTPPolicy, on_request=Mock(wraps=verify))

    # Mutating the challenge request shouldn't affect the authorized request.
    # This is the pipeline flow:
    #  1. add option and header
    #  2. challenge auth
    #  3. remove option, header from unauthorized request
    #  4. verify option, header on authorized request
    return [adder, challenge_policy, remover, verifier]
