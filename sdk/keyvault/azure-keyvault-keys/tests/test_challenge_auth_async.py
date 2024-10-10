# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the HTTP challenge authentication implementation. These tests aren't parallelizable, because
the challenge cache is global to the process.
"""
import asyncio
from itertools import product
import os
import time
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.rest import HttpRequest
from azure.keyvault.keys._shared import AsyncChallengeAuthPolicy,HttpChallenge, HttpChallengeCache
from azure.keyvault.keys._shared.client_base import DEFAULT_VERSION
from azure.keyvault.keys.aio import KeyClient
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import AsyncKeysClientPreparer, get_decorator
from _shared.helpers import Request, mock_response
from _shared.helpers_async import async_validating_transport
from _shared.test_case_async import KeyVaultTestCase
from test_challenge_auth import (
    empty_challenge_cache,
    get_random_url,
    add_url_port,
    CAE_CHALLENGE_RESPONSE,
    CAE_DECODED_CLAIM,
    KV_CHALLENGE_RESPONSE,
    KV_CHALLENGE_TENANT,
    RESOURCE,
    TOKEN_TYPES,
)

only_default_version = get_decorator(is_async=True, api_versions=[DEFAULT_VERSION])


class TestChallengeAuth(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version,is_hsm",only_default_version)
    @AsyncKeysClientPreparer()
    @recorded_by_proxy_async
    async def test_multitenant_authentication(self, client, is_hsm, **kwargs):
        if not self.is_live:
            pytest.skip("This test is incompatible with vcrpy in playback")

        # we set up a client for this method so it gets awaited, but we actually want to create a new client
        # this new client should use a credential with an initially fake tenant ID and still succeed with a real request
        original_tenant = os.environ.get("AZURE_TENANT_ID")
        os.environ["AZURE_TENANT_ID"] = str(uuid4())
        credential = self.get_credential(KeyClient, additionally_allowed_tenants="*", is_async=True)
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

        # clear the fake tenant
        if original_tenant:
            os.environ["AZURE_TENANT_ID"] = original_tenant
        else:
            os.environ.pop("AZURE_TENANT_ID")


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
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_scope(token_type):
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
            return token_type(expected_token, 0)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = AsyncPipeline(
            policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send)
        )
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)

        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    endpoint = "https://authority.net/tenant"

    # an AADv1 resource becomes an AADv2 scope with the addition of '/.default'
    resource = "https://vault.azure.net"
    scope = resource + "/.default"

    challenge_with_resource = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'},
    )

    challenge_with_scope = Mock(
        status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", scope={scope}'}
    )

    await test_with_challenge(challenge_with_resource, scope)
    await test_with_challenge(challenge_with_scope, scope)


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_tenant(token_type):
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

        async def get_token(*_, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("tenant_id") == expected_tenant
            return token_type(expected_token, 0)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = AsyncPipeline(
            policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send)
        )
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)

        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}"
    resource = "https://vault.azure.net"

    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'},
    )

    await test_with_challenge(challenge, tenant)


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_adfs(token_type):
    """The policy should handle AD FS challenges as a special case and omit the tenant ID from token requests"""

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
            elif Requests.count in (2, 3):
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        async def get_token(*_, **kwargs):
            # we shouldn't provide a tenant ID during AD FS authentication
            assert "tenant_id" not in kwargs
            return token_type(expected_token, 0)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        policy = AsyncChallengeAuthPolicy(credential=credential)
        pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

        # Regression test: https://github.com/Azure/azure-sdk-for-python/issues/33621
        policy._token = None
        await pipeline.run(request)

    tenant = "tenant-id"
    # AD FS challenges have an unusual authority format; see https://github.com/Azure/azure-sdk-for-python/issues/28648
    endpoint = f"https://adfs.redmond.azurestack.corp.microsoft.com/adfs/{tenant}"
    resource = "https://vault.azure.net"

    challenge = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource={resource}'},
    )

    await test_with_challenge(challenge, tenant)


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_policy_updates_cache(token_type):
    """
    It's possible for the challenge returned for a request to change, e.g. when a vault is moved to a new tenant.
    When the policy receives a 401, it should update the cached challenge for the requested URL, if one exists.
    """

    url = get_random_url()
    first_scope = "https://vault.azure.net/first-scope"
    first_token = "first-scope-token"
    second_scope = "https://vault.azure.net/second-scope"
    second_token = "second-scope-token"
    challenge_fmt = 'Bearer authorization="https://login.authority.net/tenant", resource='

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
            Request(url, required_headers={"Authorization": f"Bearer {first_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {first_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {first_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {second_token}"}),
            Request(url, required_headers={"Authorization": f"Bearer {second_token}"}),
        ),
        responses=(
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt + first_scope}),
            mock_response(status_code=200),
            mock_response(status_code=200),
            mock_response(status_code=401, headers={"WWW-Authenticate": challenge_fmt + second_scope}),
            mock_response(status_code=200),
            mock_response(status_code=200),
        ),
    )

    token = token_type(first_token, time.time() + 3600)

    async def get_token(*_, **__):
        return token

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=transport)

    # policy should complete and cache the first challenge and access token
    for _ in range(2):
        await pipeline.run(HttpRequest("GET", url))
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    # The next request will receive a new challenge. The policy should handle it and update caches.
    token = token_type(second_token, time.time() + 3600)
    for _ in range(2):
        await pipeline.run(HttpRequest("GET", url))
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 2
        else:
            assert credential.get_token_info.call_count == 2


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_token_expiration(token_type):
    """policy should not use a cached token which has expired"""

    url = get_random_url()

    expires_on = time.time() + 3600
    first_token = "*"
    second_token = "**"
    resource = "https://vault.azure.net"

    token = token_type(first_token, expires_on)

    async def get_token(*_, **__):
        return token

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
    transport = async_validating_transport(
        requests=[
            Request(),
            Request(required_headers={"Authorization": "Bearer " + first_token}),
            Request(required_headers={"Authorization": "Bearer " + first_token}),
            Request(required_headers={"Authorization": "Bearer " + second_token}),
        ],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            )
        ]
        + [mock_response()] * 3,
    )
    pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=transport)

    for _ in range(2):
        await pipeline.run(HttpRequest("GET", url))
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 1
        else:
            assert credential.get_token_info.call_count == 1

    token = token_type(second_token, time.time() + 3600)
    with patch("time.time", lambda: expires_on):
        await pipeline.run(HttpRequest("GET", url))
    if hasattr(credential, "get_token"):
        assert credential.get_token.call_count == 2
    else:
        assert credential.get_token_info.call_count == 2


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", TOKEN_TYPES)
async def test_preserves_options_and_headers(token_type):
    """After a challenge, the policy should send the original request with its options and headers preserved"""

    url = get_random_url()
    token = "**"
    resource = "https://vault.azure.net"

    async def get_token(*_, **__):
        return token_type(token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    transport = async_validating_transport(
        requests=[Request()] * 2 + [Request(required_headers={"Authorization": "Bearer " + token})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
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


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("verify_challenge_resource,token_type", product([True, False], TOKEN_TYPES))
async def test_verify_challenge_resource_matches(verify_challenge_resource, token_type):
    """The auth policy should raise if the challenge resource doesn't match the request URL unless check is disabled"""

    url = get_random_url()
    url_with_port = add_url_port(url)
    token = "**"
    resource = "https://myvault.azure.net"  # Doesn't match a "".vault.azure.net" resource because of the "my" prefix

    async def get_token(*_, **__):
        return token_type(token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    transport = async_validating_transport(
        requests=[Request(), Request(required_headers={"Authorization": f"Bearer {token}"})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            ),
            mock_response(status_code=200, json_payload={"key": {"kid": f"{url}/key-name"}})
        ]
    )
    transport_2 = async_validating_transport(
        requests=[Request(), Request(required_headers={"Authorization": f"Bearer {token}"})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            ),
            mock_response(status_code=200, json_payload={"key": {"kid": f"{url}/key-name"}})
        ]
    )

    client = KeyClient(url, credential, transport=transport, verify_challenge_resource=verify_challenge_resource)
    client_with_port = KeyClient(
        url_with_port, credential, transport=transport_2, verify_challenge_resource=verify_challenge_resource
    )

    if verify_challenge_resource:
        with pytest.raises(ValueError) as e:
            await client.get_key("key-name")
        assert f"The challenge resource 'myvault.azure.net' does not match the requested domain" in str(e.value)
        with pytest.raises(ValueError) as e:
            await client_with_port.get_key("key-name")
        assert f"The challenge resource 'myvault.azure.net' does not match the requested domain" in str(e.value)
    else:
        key = await client.get_key("key-name")
        assert key.name == "key-name"
        key = await client_with_port.get_key("key-name")
        assert key.name == "key-name"


@pytest.mark.asyncio
@pytest.mark.parametrize("verify_challenge_resource,token_type", product([True, False], TOKEN_TYPES))
async def test_verify_challenge_resource_valid(verify_challenge_resource, token_type):
    """The auth policy should raise if the challenge resource isn't a valid URL unless check is disabled"""

    url = get_random_url()
    token = "**"
    resource = "bad-resource"

    async def get_token(*_, **__):
        return token_type(token, 0)

    if token_type == AccessToken:
        credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    else:
        credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))

    transport = async_validating_transport(
        requests=[Request(), Request(required_headers={"Authorization": f"Bearer {token}"})],
        responses=[
            mock_response(
                status_code=401, headers={"WWW-Authenticate": f'Bearer authorization="{url}", resource={resource}'}
            ),
            mock_response(status_code=200, json_payload={"key": {"kid": f"{url}/key-name"}})
        ]
    )

    client = KeyClient(url, credential, transport=transport, verify_challenge_resource=verify_challenge_resource)

    if verify_challenge_resource:
        with pytest.raises(ValueError) as e:
            await client.get_key("key-name")
        assert "The challenge contains invalid scope" in str(e.value)
    else:
        key = await client.get_key("key-name")
        assert key.name == "key-name"


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", [AccessToken, AccessTokenInfo])
async def test_cae(token_type):
    """The policy should handle claims in a challenge response after having successfully authenticated prior."""

    expected_content = b"a duck"

    async def test_with_challenge(claims_challenge, expected_claim):
        first_token = "first_token"
        expected_token = "expected_token"

        class Requests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content; triggers a KV challenge response
                assert not request.body
                assert "Authorization" not in request.headers
                assert request.headers["Content-Length"] == "0"
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return Mock(status_code=200)
            elif Requests.count == 3:
                # third request will trigger a CAE challenge response in this test scenario
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return claims_challenge
            elif Requests.count == 4:
                # fourth request should include the required claims and correctly use content from the first challenge
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            elif Requests.count == 5:
                # fifth request should be a regular request with the expected token
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 6:
                # sixth request should respond to the KV challenge WITHOUT including claims
                # we return another challenge to confirm that the policy will return consecutive 401s to the user
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return KV_CHALLENGE_RESPONSE
            raise ValueError("unexpected request")

        async def get_token(*scopes, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("enable_cae") == True
            assert options_bag.get("tenant_id") == KV_CHALLENGE_TENANT
            assert scopes[0] == RESOURCE + "/.default"
            # Response to KV challenge
            if Requests.count == 1:
                assert options_bag.get("claims") == None
                return AccessToken(first_token, time.time() + 3600)
            # Response to CAE challenge
            elif Requests.count == 3:
                assert options_bag.get("claims") == expected_claim
                return AccessToken(expected_token, time.time() + 3600)
            # Response to second KV challenge
            elif Requests.count == 5:
                assert options_bag.get("claims") == None
                return AccessToken(first_token, time.time() + 3600)
            elif Requests.count == 6:
                raise ValueError("unexpected token request")

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)  # Send the request once to trigger a regular auth challenge
        await pipeline.run(request)  # Send the request again to trigger a CAE challenge
        await pipeline.run(request)  # Send the request once to trigger another regular auth challenge

        # token requests made for the CAE challenge and first two KV challenges, but not the final KV challenge
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 3
        else:
            assert credential.get_token_info.call_count == 3

    await test_with_challenge(CAE_CHALLENGE_RESPONSE, CAE_DECODED_CLAIM)


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", [AccessToken, AccessTokenInfo])
async def test_cae_consecutive_challenges(token_type):
    """The policy should correctly handle consecutive challenges in cases where the flow is valid or invalid."""

    expected_content = b"a duck"

    async def test_with_challenge(claims_challenge, expected_claim):
        first_token = "first_token"
        expected_token = "expected_token"

        class Requests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content; triggers a KV challenge response
                assert not request.body
                assert "Authorization" not in request.headers
                assert request.headers["Content-Length"] == "0"
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 2:
                # second request will trigger a CAE challenge response in this test scenario
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return claims_challenge
            elif Requests.count == 3:
                # third request should include the required claims and correctly use content from the first challenge
                # we return another CAE challenge to verify that the policy will return consecutive CAE 401s to the user
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert expected_token in request.headers["Authorization"]
                return claims_challenge
            raise ValueError("unexpected request")

        async def get_token(*scopes, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("enable_cae") == True
            assert options_bag.get("tenant_id") == KV_CHALLENGE_TENANT
            assert scopes[0] == RESOURCE + "/.default"
            # Response to KV challenge
            if Requests.count == 1:
                assert options_bag.get("claims") == None
                return AccessToken(first_token, time.time() + 3600)
            # Response to first CAE challenge
            elif Requests.count == 2:
                assert options_bag.get("claims") == expected_claim
                return AccessToken(expected_token, time.time() + 3600)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)

        # token requests made for the KV challenge and first CAE challenge, but not the second CAE challenge
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 2
        else:
            assert credential.get_token_info.call_count == 2

    await test_with_challenge(CAE_CHALLENGE_RESPONSE, CAE_DECODED_CLAIM)


@pytest.mark.asyncio
@empty_challenge_cache
@pytest.mark.parametrize("token_type", [AccessToken, AccessTokenInfo])
async def test_cae_token_expiry(token_type):
    """The policy should avoid sending claims more than once when a token expires."""

    expected_content = b"a duck"

    async def test_with_challenge(claims_challenge, expected_claim):
        first_token = "first_token"
        second_token = "second_token"
        third_token = "third_token"

        class Requests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request should be unauthorized and have no content; triggers a KV challenge response
                assert not request.body
                assert "Authorization" not in request.headers
                assert request.headers["Content-Length"] == "0"
                return KV_CHALLENGE_RESPONSE
            elif Requests.count == 2:
                # second request will trigger a CAE challenge response in this test scenario
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert first_token in request.headers["Authorization"]
                return claims_challenge
            elif Requests.count == 3:
                # third request should include the required claims and correctly use content from the first challenge
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert second_token in request.headers["Authorization"]
                return Mock(status_code=200)
            elif Requests.count == 4:
                # fourth request should not include claims, but otherwise use content from the first challenge
                assert request.headers["Content-Length"]
                assert request.body == expected_content
                assert third_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        async def get_token(*scopes, options=None, **kwargs):
            options_bag = options if options else kwargs
            assert options_bag.get("enable_cae") == True
            assert options_bag.get("tenant_id") == KV_CHALLENGE_TENANT
            assert scopes[0] == RESOURCE + "/.default"
            # Response to KV challenge
            if Requests.count == 1:
                assert options_bag.get("claims") == None
                return AccessToken(first_token, time.time() + 3600)
            # Response to first CAE challenge
            elif Requests.count == 2:
                assert options_bag.get("claims") == expected_claim
                return AccessToken(second_token, 0)  # Return a token that expires immediately to trigger a refresh
            # Token refresh before making the final request
            elif Requests.count == 3:
                assert options_bag.get("claims") == None
                return AccessToken(third_token, time.time() + 3600)

        if token_type == AccessToken:
            credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
        else:
            credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(wraps=get_token))
        pipeline = AsyncPipeline(policies=[AsyncChallengeAuthPolicy(credential=credential)], transport=Mock(send=send))
        request = HttpRequest("POST", get_random_url())
        request.set_bytes_body(expected_content)
        await pipeline.run(request)
        await pipeline.run(request)  # Send the request again to trigger a token refresh upon expiry

        # token requests made for the KV and CAE challenges, as well as for the token refresh
        if hasattr(credential, "get_token"):
            assert credential.get_token.call_count == 3
        else:
            assert credential.get_token_info.call_count == 3

    await test_with_challenge(CAE_CHALLENGE_RESPONSE, CAE_DECODED_CLAIM)
