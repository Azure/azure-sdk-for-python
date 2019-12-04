# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""
import time

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import HttpRequest
from azure.keyvault.keys._shared import AsyncChallengeAuthPolicy, HttpChallenge, HttpChallengeCache
import pytest

from keys_helpers import async_validating_transport, mock_response, Request
from test_challenge_auth import empty_challenge_cache, get_policies_for_request_mutation_test, get_random_url


@pytest.mark.asyncio
@empty_challenge_cache
async def test_policy():
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
    await pipeline.run(HttpRequest("POST", get_random_url(), data=data))


@pytest.mark.asyncio
@empty_challenge_cache
async def test_policy_updates_cache():
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
    # 4. fifth request should be authorized according to the new challenge
    # 5. sixth request should match the fifth
    transport = async_validating_transport(
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

    token = AccessToken(first_token, time.time() + 3600)

    async def get_token(*_, **__):
        return token

    credential = Mock(get_token=Mock(wraps=get_token))
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=transport)

    # policy should complete and cache the first challenge and access token
    for _ in range(2):
        await pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1

    # The next request will receive a new challenge. The policy should handle it and update caches.
    token = AccessToken(second_token, time.time() + 3600)
    for _ in range(2):
        await pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 2


@pytest.mark.asyncio
@empty_challenge_cache
async def test_token_expiration():
    """policy should not use a cached token which has expired"""

    url = get_random_url()

    expires_on = time.time() + 3600
    first_token = "*"
    second_token = "**"

    token = AccessToken(first_token, expires_on)

    async def get_token(*_, **__):
        return token

    credential = Mock(get_token=Mock(wraps=get_token))
    transport = async_validating_transport(
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
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=transport)

    for _ in range(2):
        await pipeline.run(HttpRequest("GET", url))
        assert credential.get_token.call_count == 1

    token = AccessToken(second_token, time.time() + 3600)
    with patch("time.time", lambda: expires_on):
        await pipeline.run(HttpRequest("GET", url))
    assert credential.get_token.call_count == 2


@pytest.mark.asyncio
@empty_challenge_cache
async def test_preserves_options_and_headers():
    """After a challenge, the original request should be sent with its options and headers preserved.

    If a policy mutates the options or headers of the challenge (unauthorized) request, the options of the service
    request should be present when it is sent with authorization.
    """

    url = get_random_url()

    token = "**"

    async def get_token(*_, **__):
        return AccessToken(token, 0)

    credential = Mock(get_token=Mock(wraps=get_token))

    transport = async_validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"Authorization": "Bearer " + token})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": 'Bearer authorization="{}", resource=foo'.format(url)}
            )
        ]
        + [mock_response()] * 2,
    )
    challenge_policy = AsyncChallengeAuthPolicy(credential=credential)
    policies = get_policies_for_request_mutation_test(challenge_policy)
    pipeline = AsyncPipeline(policies=policies, transport=transport)

    response = await pipeline.run(HttpRequest("GET", url))

    # ensure the mock sans I/O policies were used
    for policy in policies:
        if hasattr(policy, "on_request"):
            assert policy.on_request.called, "mock policy wasn't invoked"
