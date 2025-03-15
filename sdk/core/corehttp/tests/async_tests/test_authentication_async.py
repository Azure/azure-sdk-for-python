# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from unittest.mock import Mock

from corehttp.credentials import AccessTokenInfo
from corehttp.credentials import AsyncTokenCredential
from corehttp.exceptions import ServiceRequestError
from corehttp.runtime.pipeline import AsyncPipeline
from corehttp.runtime.policies import (
    AsyncBearerTokenCredentialPolicy,
    SansIOHTTPPolicy,
)
from corehttp.rest import HttpRequest
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
import pytest

pytestmark = pytest.mark.asyncio


async def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessTokenInfo("expected_token", 2524608000)

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    get_token_calls = 0

    async def get_token_info(*_, **__):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    fake_credential = Mock(spec_set=["get_token_info"], get_token_info=get_token_info)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"), context=None)
    assert get_token_calls == 1

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"), context=None)
    # Didn't need a new token
    assert get_token_calls == 1


async def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    get_token = get_completed_future(AccessTokenInfo("***", 42))
    fake_credential = Mock(spec_set=["get_token_info"], get_token_info=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


async def test_bearer_policy_sync_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    get_token = get_completed_future(AccessTokenInfo("***", 42))
    fake_credential = Mock(spec_set=["get_token_info"], get_token_info=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


async def test_bearer_policy_token_caching():
    good_for_one_hour = AccessTokenInfo("token", int(time.time()) + 3600)
    expected_token = good_for_one_hour
    get_token_calls = 0

    async def get_token_info(*_, **__):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    async def send_mock(_):
        return Mock(http_response=Mock(status_code=200))

    credential = Mock(spec_set=["get_token_info"], get_token_info=get_token_info)
    policies = [
        AsyncBearerTokenCredentialPolicy(credential, "scope"),
        Mock(send=send_mock),
    ]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # policy has no token at first request -> it should call get_token

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessTokenInfo("token", int(time.time()))
    get_token_calls = 0
    expected_token = expired_token
    policies = [
        AsyncBearerTokenCredentialPolicy(credential, "scope"),
        Mock(send=send_mock),
    ]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 1

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert get_token_calls == 2  # token expired -> policy should call get_token


async def test_bearer_policy_optionally_enforces_https():
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    async def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "AsyncBearerTokenCredentialPolicy didn't pop the 'enforce_https' option"
        return Mock()

    credential = Mock(
        spec_set=["get_token_info"], get_token_info=lambda *_, **__: get_completed_future(AccessTokenInfo("***", 42))
    )
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


async def test_bearer_policy_preserves_enforce_https_opt_out():
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"
            return Mock()

    get_token = get_completed_future(AccessTokenInfo("***", 42))
    credential = Mock(spec_set=["get_token_info"], get_token_info=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=Mock(send=lambda *_, **__: get_completed_future(Mock())), policies=policies)

    await pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)


async def test_bearer_policy_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"
            return Mock()

    get_token = get_completed_future(AccessTokenInfo("***", 42))
    credential = Mock(spec_set=["get_token_info"], get_token_info=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=Mock(send=lambda *_, **__: get_completed_future(Mock())), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://secure"))


async def test_bearer_policy_calls_sansio_methods():
    """AsyncBearerTokenCredentialPolicy should call SansIOHttpPolicy methods as does _SansIOAsyncHTTPPolicyRunner"""

    class TestPolicy(AsyncBearerTokenCredentialPolicy):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.on_exception = Mock(return_value=False)
            self.on_request = Mock()
            self.on_response = Mock()

        async def send(self, request):
            self.request = request
            self.response = await super().send(request)
            return self.response

    credential = Mock(
        spec_set=["get_token"],
        get_token=Mock(return_value=get_completed_future(AccessTokenInfo("***", int(time.time()) + 3600))),
    )
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=get_completed_future(Mock(status_code=200))))

    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    await pipeline.run(HttpRequest("GET", "https://localhost"))

    policy.on_request.assert_called_once_with(policy.request, auth_flows=None)
    policy.on_response.assert_called_once_with(policy.request, policy.response)

    # the policy should call on_exception when next.send() raises
    class TestException(Exception):
        pass

    # during the first send...
    transport = Mock(send=Mock(side_effect=TestException))
    policy = TestPolicy(credential, "scope")
    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        await pipeline.run(HttpRequest("GET", "https://localhost"))
    policy.on_exception.assert_called_once_with(policy.request)

    # ...or the second
    async def fake_send(*args, **kwargs):
        if fake_send.calls == 0:
            fake_send.calls = 1
            return Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
        raise TestException()

    fake_send.calls = 0

    policy = TestPolicy(credential, "scope")
    policy.on_challenge = Mock(return_value=get_completed_future(True))
    transport = Mock(send=Mock(wraps=fake_send))
    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        await pipeline.run(HttpRequest("GET", "https://localhost"))
    assert transport.send.call_count == 2
    policy.on_challenge.assert_called_once()
    policy.on_exception.assert_called_once_with(policy.request)


async def test_azure_core_sans_io_policy():
    """Tests to see that we can use an azure.core SansIOHTTPPolicy with the corehttp Pipeline"""

    class TestPolicy(AzureKeyCredentialPolicy):
        def __init__(self, *args, **kwargs):
            super(TestPolicy, self).__init__(*args, **kwargs)
            self.on_exception = Mock(return_value=False)
            self.on_request = Mock()

    credential = Mock(key="key")
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=get_completed_future(Mock(status_code=200))))

    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    await pipeline.run(HttpRequest("GET", "https://localhost"))

    policy.on_request.assert_called_once()


def get_completed_future(result=None):
    fut = asyncio.Future()
    fut.set_result(result)
    return fut


@pytest.mark.asyncio
async def test_async_token_credential_inheritance():
    class TestTokenCredential(AsyncTokenCredential):
        async def get_token_info(self, *scopes, options={}):
            return "TOKEN"

    cred = TestTokenCredential()
    token = await cred.get_token_info("scope")
    assert token == "TOKEN"


@pytest.mark.asyncio
async def test_async_token_credential_asyncio_lock():
    auth_policy = AsyncBearerTokenCredentialPolicy(Mock(), "scope")
    assert isinstance(auth_policy._lock, asyncio.Lock)


async def test_async_token_credential_sync():
    """Verify that AsyncBearerTokenCredentialPolicy can be constructed in a synchronous context."""
    AsyncBearerTokenCredentialPolicy(Mock(), "scope")


async def test_need_new_token():
    expected_scope = "scope"
    now = int(time.time())

    policy = AsyncBearerTokenCredentialPolicy(Mock(), expected_scope)

    # Token is expired.
    policy._token = AccessTokenInfo("", now - 1200)
    assert policy._need_new_token

    # Token is about to expire within 300 seconds.
    policy._token = AccessTokenInfo("", now + 299)
    assert policy._need_new_token

    # Token still has more than 300 seconds to live.
    policy._token = AccessTokenInfo("", now + 305)
    assert not policy._need_new_token

    # Token has both expires_on and refresh_on set well into the future.
    policy._token = AccessTokenInfo("", now + 1200, refresh_on=now + 1200)
    assert not policy._need_new_token

    # Token is not close to expiring, but refresh_on is in the past.
    policy._token = AccessTokenInfo("", now + 1200, refresh_on=now - 1)
    assert policy._need_new_token


@pytest.mark.asyncio
async def test_send_with_auth_flows():
    auth_flows = [{"type": "flow1"}, {"type": "flow2"}]
    credential = Mock(
        spec_set=["get_token_info"],
        get_token_info=Mock(return_value=get_completed_future(AccessTokenInfo("***", int(time.time()) + 3600))),
    )
    policy = AsyncBearerTokenCredentialPolicy(credential, "scope", auth_flows=auth_flows)
    transport = Mock(send=Mock(return_value=get_completed_future(Mock(status_code=200))))

    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    await pipeline.run(HttpRequest("GET", "https://localhost"))
    policy._credential.get_token_info.assert_called_with("scope", options={"auth_flows": auth_flows})
