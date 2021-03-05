# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import AzureError, ServiceRequestError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest
import pytest


@pytest.mark.asyncio
async def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)

    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    fake_credential = Mock(get_token=get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"), context=None)
    assert get_token_calls == 1

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"), context=None)
    # Didn't need a new token
    assert get_token_calls == 1


@pytest.mark.asyncio
async def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda *_, **__: get_completed_future(AccessToken("", 0)))
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


@pytest.mark.asyncio
async def test_bearer_policy_token_caching():
    good_for_one_hour = AccessToken("token", time.time() + 3600)
    expected_token = good_for_one_hour
    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    credential = Mock(get_token=get_token)
    policies = [
        AsyncBearerTokenCredentialPolicy(credential, "scope"),
        Mock(send=Mock(return_value=get_completed_future())),
    ]
    pipeline = AsyncPipeline(transport=Mock, policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # policy has no token at first request -> it should call get_token

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    get_token_calls = 0
    expected_token = expired_token
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), Mock(send=lambda _: get_completed_future())]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 2  # token expired -> policy should call get_token


@pytest.mark.asyncio
async def test_bearer_policy_optionally_enforces_https():
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    async def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "AsyncBearerTokenCredentialPolicy didn't pop the 'enforce_https' option"

    credential = Mock(get_token=lambda *_, **__: get_completed_future(AccessToken("***", 42)))
    pipeline = AsyncPipeline(
        transport=Mock(send=assert_option_popped), policies=[AsyncBearerTokenCredentialPolicy(credential, "scope")]
    )

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        await pipeline.run(HttpRequest("GET", "http://not.secure"))
    with pytest.raises(ServiceRequestError):
        await pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    await pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)

    # https requests should always pass
    await pipeline.run(HttpRequest("GET", "https://secure"), enforce_https=False)
    await pipeline.run(HttpRequest("GET", "https://secure"), enforce_https=True)
    await pipeline.run(HttpRequest("GET", "https://secure"))


@pytest.mark.asyncio
async def test_preserves_enforce_https_opt_out():
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=Mock(send=lambda *_, **__: get_completed_future()), policies=policies)

    await pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)


@pytest.mark.asyncio
async def test_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=Mock(send=lambda *_, **__: get_completed_future()), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://secure"))


def get_completed_future(result=None):
    fut = asyncio.Future()
    fut.set_result(result)
    return fut
