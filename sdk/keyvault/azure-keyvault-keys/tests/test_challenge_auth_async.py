# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""
import asyncio
import os
import time
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.identity.aio import ClientSecretCredential
from azure.keyvault.keys._shared import AsyncChallengeAuthPolicy,HttpChallenge, HttpChallengeCache
from azure.keyvault.keys._shared.client_base import DEFAULT_VERSION
from azure.keyvault.keys.aio import KeyClient
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import AsyncKeysClientPreparer, get_decorator
from _shared.helpers import Request, mock_response
from _shared.helpers_async import async_validating_transport
from _shared.test_case_async import KeyVaultTestCase
from test_challenge_auth import empty_challenge_cache, get_random_url

only_default_version = get_decorator(is_async=True, api_versions=[DEFAULT_VERSION])


class TestChallengeAuth(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",only_default_version)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_multitenant_authentication(self, client, is_hsm, **kwargs):
        if not self.is_live:
            pytest.skip("This test is incompatible with vcrpy in playback")

        client_id = os.environ.get("KEYVAULT_CLIENT_ID")
        client_secret = os.environ.get("KEYVAULT_CLIENT_SECRET")
        if not (client_id and client_secret):
            pytest.skip("Values for KEYVAULT_CLIENT_ID and KEYVAULT_CLIENT_SECRET are required")

        # we set up a client for this method so it gets awaited, but we actually want to create a new client
        # this new client should use a credential with an initially fake tenant ID and still succeed with a real request
        credential = ClientSecretCredential(tenant_id=str(uuid4()), client_id=client_id, client_secret=client_secret)
        managed_hsm_url = kwargs.pop("managed_hsm_url", None)
        keyvault_url = kwargs.pop("vault_url", None)
        vault_url = managed_hsm_url if is_hsm else keyvault_url
        client = KeyClient(vault_url=vault_url, credential=credential)

        if self.is_live:
            await asyncio.sleep(2)  # to avoid throttling by the service
        key_name = self.get_resource_name("multitenant-key")
        key = await client.create_rsa_key(key_name)
        assert key.id

        # try making another request with the credential's token revoked
        # the challenge policy should correctly request a new token for the correct tenant when a challenge is cached
        client._client._config.authentication_policy._token = None
        fetched_key = await client.get_key(key_name)
        assert key.id == fetched_key.id


@pytest.mark.asyncio
@empty_challenge_cache
async def test_enforces_tls():
    url = "http://not.secure"
    HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, "Bearer authorization=_, resource=_"))

    credential = Mock()
    pipeline = AsyncPipeline(transport=Mock(), policies=[AsyncChallengeAuthPolicy(credential)])
    with pytest.raises(ServiceRequestError):
        await pipeline.run(HttpRequest("GET", url))


@pytest.mark.asyncio
@empty_challenge_cache
async def test_scope():
    """The policy's token requests should always be for an AADv2 scope"""

    expected_content = b"a duck"

    async def test_with_challenge(challenge, expected_scope):
        expected_token = "expected_token"

        class Requests:
            count = 0

        async def send(request):
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

        async def get_token(*scopes, **_):
            assert len(scopes) == 1
            assert scopes[0] == expected_scope
            return AccessToken(expected_token, 0)

        credential = Mock(get_token=Mock(wraps=get_token))
        pipeline = AsyncPipeline(
            policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send)
        )
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)

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

    await test_with_challenge(challenge_with_resource, scope)
    await test_with_challenge(challenge_with_scope, scope)


@pytest.mark.asyncio
@empty_challenge_cache
async def test_tenant():
    """The policy's token requests should pass the parsed tenant ID from the challenge"""

    expected_content = b"a duck"

    async def test_with_challenge(challenge, expected_tenant):
        expected_token = "expected_token"

        class Requests:
            count = 0

        async def send(request):
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

        async def get_token(*_, **kwargs):
            assert kwargs.get("tenant_id") == expected_tenant
            return AccessToken(expected_token, 0)

        credential = Mock(get_token=Mock(wraps=get_token))
        pipeline = AsyncPipeline(
            policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send)
        )
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)

        assert credential.get_token.call_count == 1

    tenant = "tenant-id"
    endpoint = "https://authority.net/{}".format(tenant)

    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": 'Bearer authorization="{}", resource=https://challenge.resource'.format(endpoint)},
    )

    await test_with_challenge(challenge, tenant)


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
    # 5. fifth request should be authorized according to the new challenge
    # 6. sixth request should match the fifth
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
    """After a challenge, the policy should send the original request with its options and headers preserved"""

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
    key = "foo"
    value = "bar"

    def add(request):
        # add the expected option and header
        request.context.options[key] = value
        request.http_request.headers[key] = value

    adder = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock(wraps=add), on_exception=lambda _: False)

    def verify(request):
        # authorized (non-challenge) requests should have the expected option and header
        if request.http_request.headers.get("Authorization"):
            assert request.context.options.get(key) == value, "request option wasn't preserved across challenge"
            assert request.http_request.headers.get(key) == value, "headers wasn't preserved across challenge"

    verifier = Mock(spec=SansIOHTTPPolicy, on_request=Mock(wraps=verify))

    challenge_policy = AsyncChallengeAuthPolicy(credential=credential)
    policies = [adder, challenge_policy, verifier]
    pipeline = AsyncPipeline(policies=policies, transport=transport)

    await pipeline.run(HttpRequest("GET", url))

    # ensure the mock sans I/O policies were called
    assert adder.on_request.called, "mock policy wasn't invoked"
    assert verifier.on_request.called, "mock policy wasn't invoked"
