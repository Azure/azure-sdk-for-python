# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.data.tables.aio._authentication_async import AsyncBearerTokenChallengePolicy
import pytest

pytestmark = pytest.mark.asyncio

HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_challenge_policy_uses_scopes_and_tenant(http_request):
    """The policy's token requests should pass the parsed scope and tenant ID from the challenge"""

    async def test_with_challenge(challenge, expected_scope, expected_tenant):
        expected_token = "expected_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                return challenge
            elif Requests.count == 2:
                # second request should be authorized according to challenge and have the expected content
                assert expected_token in request.headers["Authorization"]
                return Mock(status_code=200)
            raise ValueError("unexpected request")

        async def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != expected_scope
                assert kwargs.get("tenant_id") is None
            elif TokenRequests.count == 2:
                # second request should use the scope and tenant ID specified in the auth challenge
                assert scopes[0] == expected_scope
                assert kwargs.get("tenant_id") == expected_tenant
            else:
                raise ValueError("unexpected token request")
            return AccessToken(expected_token, 0)

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = AsyncBearerTokenChallengePolicy(credential, "scope")
        pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))
        await pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    await test_with_challenge(challenge_with_commas, scope, tenant)

    # this challenge separates the authorization server and resource with only spaces in the WWW-Authenticate header
    challenge_without_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization={endpoint} resource={resource}'},
    )
    await test_with_challenge(challenge_without_commas, scope, tenant)

    # this challenge gives an AADv2 scope, ending with "/.default", instead of an AADv1 resource
    challenge_with_scope = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization={endpoint} scope={scope}'},
    )
    await test_with_challenge(challenge_with_scope, scope, tenant)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_challenge_policy_disable_tenant_discovery(http_request):
    """The policy's token requests should exclude the challenge's tenant if requested"""

    async def test_with_challenge(challenge, challenge_scope):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should still be unauthorized because we didn't authenticate in the correct tenant
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        async def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != challenge_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the scope specified in the auth challenge, but not the tenant
                assert scopes[0] == challenge_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = AsyncBearerTokenChallengePolicy(credential, "scope", discover_tenant=False)
        pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))
        await pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    # the request should fail after the challenge because we don't use the correct tenant
    # after the second 4xx response, the policy should raise the authentication error
    await test_with_challenge(challenge_with_commas, scope)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_challenge_policy_disable_scopes_discovery(http_request):
    """The policy's token requests should exclude the challenge's scope if requested"""

    async def test_with_challenge(challenge, challenge_scope, challenge_tenant):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should still be unauthorized because we didn't authenticate with the correct scope
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        async def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != challenge_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the tenant specified in the auth challenge, but not the scope
                assert scopes[0] != challenge_scope
                assert kwargs.get("tenant_id") == challenge_tenant
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = AsyncBearerTokenChallengePolicy(credential, "scope", discover_scopes=False)
        pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))
        await pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    # the request should fail after the challenge because we don't use the correct scope
    # after the second 4xx response, the policy should raise the authentication error
    await test_with_challenge(challenge_with_commas, scope, tenant)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_challenge_policy_disable_any_discovery(http_request):
    """The policy shouldn't respond to the challenge if it can't use the provided scope or tenant"""

    async def test_with_challenge(challenge, challenge_scope, challenge_tenant):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        async def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != challenge_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = AsyncBearerTokenChallengePolicy(
            credential, "scope", discover_tenant=False, discover_scopes=False
        )
        pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))
        await pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge separates the authorization server and resource with commas in the WWW-Authenticate header
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}", resource="{resource}"'},
    )
    # the policy should only send one request since we can't update our request per the challenge response
    await test_with_challenge(challenge_with_commas, scope, tenant)


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_challenge_policy_no_scope_in_challenge(http_request):
    """The policy's token requests should use constructor scopes if none are in the challenge"""

    async def test_with_challenge(challenge, challenge_scope, challenge_tenant):
        bad_token = "bad_token"

        class Requests:
            count = 0

        class TokenRequests:
            count = 0

        async def send(request):
            Requests.count += 1
            if Requests.count == 1:
                # first request triggers a 401 response w/ auth challenge
                assert bad_token in request.headers["Authorization"]
                return challenge
            elif Requests.count == 2:
                # second request should still be unauthorized because we didn't authenticate with the correct scope
                assert bad_token in request.headers["Authorization"]
                return challenge
            raise ValueError("unexpected request")

        async def get_token(*scopes, **kwargs):
            assert len(scopes) == 1
            TokenRequests.count += 1
            if TokenRequests.count == 1:
                # first request uses the scope given to the policy, and no tenant ID
                assert scopes[0] != challenge_scope
                assert kwargs.get("tenant_id") is None
                return AccessToken(bad_token, 0)
            elif TokenRequests.count == 2:
                # second request should use the tenant specified in the auth challenge, and same scope as before
                assert scopes[0] != challenge_scope
                assert kwargs.get("tenant_id") == challenge_tenant
                return AccessToken(bad_token, 0)
            raise ValueError("unexpected token request")

        credential = Mock(get_token=Mock(wraps=get_token))
        policy = AsyncBearerTokenChallengePolicy(credential, "scope")
        pipeline = AsyncPipeline(policies=[policy], transport=Mock(send=send))
        await pipeline.run(http_request("GET", "https://localhost"))

    tenant = "tenant-id"
    endpoint = f"https://authority.net/{tenant}/oauth2/authorize"
    resource = "https://challenge.resource"
    scope = f"{resource}/.default"

    # this challenge has no `resource` or `scope` field
    challenge_with_commas = Mock(
        status_code=401,
        headers={"WWW-Authenticate": f'Bearer authorization="{endpoint}"'},
    )
    # the request should fail after the challenge because we don't use the correct scope
    # after the second 4xx response, the policy should raise the authentication error
    await test_with_challenge(challenge_with_commas, scope, tenant)
