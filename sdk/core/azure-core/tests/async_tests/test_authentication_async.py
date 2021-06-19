# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from unittest.mock import Mock

from requests.models import RequestEncodingMixin

from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline._backcompat import SupportedFormat
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
import pytest

pytestmark = pytest.mark.asyncio

async def async_magic():
    pass

Mock.__await__ = lambda x: async_magic().__await__()

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_adds_header(request_type):
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    fake_credential = Mock(get_token=get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    transport = Mock()
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(request_type("GET", "https://spam.eggs"), context=None)
    assert get_token_calls == 1

    await pipeline.run(request_type("GET", "https://spam.eggs"), context=None)
    # Didn't need a new token
    assert get_token_calls == 1

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_send(request_type):
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = request_type("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        if hasattr(request_type, "content"):
            # at this point in the pipelines, the request is a pipeline transport request
            # bc we switch rest requests to pipeline transport requests for back compat
            # checking values instead
            assert request.http_request.method == "GET"
            assert request.http_request.url == "https://spam.eggs"
        else:
            assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda *_, **__: get_completed_future(AccessToken("", 0)))
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    transport = Mock()
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    response = await AsyncPipeline(transport=transport, policies=policies).run(expected_request)

    assert response is expected_response


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_token_caching(request_type):
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
        Mock(send=Mock(return_value=get_completed_future(Mock()))),
    ]
    transport = Mock()
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(request_type("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # policy has no token at first request -> it should call get_token

    await pipeline.run(request_type("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    get_token_calls = 0
    expected_token = expired_token
    policies = [
        AsyncBearerTokenCredentialPolicy(credential, "scope"),
        Mock(send=lambda _: get_completed_future(Mock())),
    ]

    transport = Mock()
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(request_type("GET", "https://spam.eggs"))
    assert get_token_calls == 1

    await pipeline.run(request_type("GET", "https://spam.eggs"))
    assert get_token_calls == 2  # token expired -> policy should call get_token


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_optionally_enforces_https(request_type):
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    async def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "AsyncBearerTokenCredentialPolicy didn't pop the 'enforce_https' option"
        return Mock()

    credential = Mock(get_token=lambda *_, **__: get_completed_future(AccessToken("***", 42)))
    transport = Mock(send=assert_option_popped)
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    pipeline = AsyncPipeline(
        transport=transport, policies=[AsyncBearerTokenCredentialPolicy(credential, "scope")]
    )

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        await pipeline.run(request_type("GET", "http://not.secure"))
    with pytest.raises(ServiceRequestError):
        await pipeline.run(request_type("GET", "http://not.secure"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    await pipeline.run(request_type("GET", "http://not.secure"), enforce_https=False)

    # https requests should always pass
    await pipeline.run(request_type("GET", "https://secure"), enforce_https=False)
    await pipeline.run(request_type("GET", "https://secure"), enforce_https=True)
    await pipeline.run(request_type("GET", "https://secure"))


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_preserves_enforce_https_opt_out(request_type):
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"
            return Mock()

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    transport = Mock(send=lambda *_, **__: get_completed_future(Mock()))
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(request_type("GET", "http://not.secure"), enforce_https=False)

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_context_unmodified_by_default(request_type):
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"
            return Mock()

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    transport = Mock(send=lambda *_, **__: get_completed_future(Mock()))
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST, SupportedFormat.PIPELINE_TRANSPORT]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(request_type("GET", "https://secure"))



@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_bearer_policy_calls_sansio_methods(request_type):
    """AsyncBearerTokenCredentialPolicy should call SansIOHttpPolicy methods as does _SansIOAsyncHTTPPolicyRunner"""

    class TestPolicy(AsyncBearerTokenCredentialPolicy):
        def __init__(self, *args, **kwargs):
            super(TestPolicy, self).__init__(*args, **kwargs)
            self.on_exception = Mock(return_value=False)
            self.on_request = Mock()
            self.on_response = Mock()

        async def send(self, request):
            self.request = request
            self.response = await super(TestPolicy, self).send(request)
            return self.response

    credential = Mock(get_token=Mock(return_value=get_completed_future(AccessToken("***", int(time.time()) + 3600))))
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=get_completed_future(Mock(status_code=200))))
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST]

    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    await pipeline.run(request_type("GET", "https://localhost"))

    policy.on_request.assert_called_once_with(policy.request)
    policy.on_response.assert_called_once_with(policy.request, policy.response)

    # the policy should call on_exception when next.send() raises
    class TestException(Exception):
        pass

    transport = Mock(send=Mock(side_effect=TestException))
    if hasattr(request_type, "content"):
        transport.supported_formats = [SupportedFormat.REST]
    policy = TestPolicy(credential, "scope")
    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        await pipeline.run(request_type("GET", "https://localhost"))
    policy.on_exception.assert_called_once_with(policy.request)


def get_completed_future(result=None):
    fut = asyncio.Future()
    fut.set_result(result)
    return fut
