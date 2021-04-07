# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import asyncio
import time
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncChallengeAuthenticationPolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest

import pytest

pytestmark = pytest.mark.asyncio


async def test_adds_header():
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
    policies = [AsyncChallengeAuthenticationPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(HttpRequest("GET", "https://localhost"), context=None)
    assert get_token_calls == 1

    await pipeline.run(HttpRequest("GET", "https://localhost"), context=None)
    # Didn't need a new token
    assert get_token_calls == 1


async def test_default_context():
    """The policy should call get_token with the scopes given at construction, and no keyword arguments, by default"""

    async def send(_):
        return Mock()

    async def get_token(_):
        return AccessToken("", 0)

    expected_scope = "scope"
    credential = Mock(get_token=Mock(wraps=get_token))
    policy = AsyncChallengeAuthenticationPolicy(credential, expected_scope)
    pipeline = AsyncPipeline(transport=Mock(send=send), policies=[policy])

    await pipeline.run(HttpRequest("GET", "https://localhost"))

    credential.get_token.assert_called_once_with(expected_scope)


async def test_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://localhost")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda *_, **__: get_completed_future(AccessToken("", 0)))
    policies = [AsyncChallengeAuthenticationPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


async def test_token_caching():
    good_for_one_hour = AccessToken("token", time.time() + 3600)
    expected_token = good_for_one_hour
    get_token_calls = 0

    async def get_token(_):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    credential = Mock(get_token=get_token)

    async def send(_):
        return Mock()

    transport = Mock(send=send)

    pipeline = AsyncPipeline(transport=transport, policies=[AsyncChallengeAuthenticationPolicy(credential, "scope")])
    await pipeline.run(HttpRequest("GET", "https://localhost"))
    assert get_token_calls == 1  # policy has no token at first request -> it should call get_token
    await pipeline.run(HttpRequest("GET", "https://localhost"))
    assert get_token_calls == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    get_token_calls = 0
    expected_token = expired_token
    pipeline = AsyncPipeline(transport=transport, policies=[AsyncChallengeAuthenticationPolicy(credential, "scope")])

    await pipeline.run(HttpRequest("GET", "https://localhost"))
    assert get_token_calls == 1
    await pipeline.run(HttpRequest("GET", "https://localhost"))
    assert get_token_calls == 2  # token expired -> policy should call get_token


async def test_optionally_enforces_https():
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    async def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "AsyncChallengeAuthenticationPolicy didn't pop the 'enforce_https' option"
        return Mock()

    credential = Mock(get_token=lambda *_, **__: get_completed_future(AccessToken("***", 42)))
    pipeline = AsyncPipeline(transport=Mock(send=assert_option_popped), policies=[AsyncChallengeAuthenticationPolicy(credential, "scope")])

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        await pipeline.run(HttpRequest("GET", "http://localhost"))
    with pytest.raises(ServiceRequestError):
        await pipeline.run(HttpRequest("GET", "http://localhost"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    await pipeline.run(HttpRequest("GET", "http://localhost"), enforce_https=False)

    # https requests should always pass
    await pipeline.run(HttpRequest("GET", "https://localhost"), enforce_https=False)
    await pipeline.run(HttpRequest("GET", "https://localhost"), enforce_https=True)
    await pipeline.run(HttpRequest("GET", "https://localhost"))


async def test_preserves_enforce_https_opt_out():
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"

    async def send(_):
        return Mock()

    transport = Mock(send=send)

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(get_token=lambda *_, **__: get_token)
    policies = [AsyncChallengeAuthenticationPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(HttpRequest("GET", "http://localhost"), enforce_https=False)


async def test_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    async def send(_):
        return Mock()

    transport = Mock(send=send)

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(get_token=lambda *_, **__: get_token)
    policies = [AsyncChallengeAuthenticationPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    await pipeline.run(HttpRequest("GET", "https://localhost"))


async def test_cannot_complete_challenge():
    """ChallengeAuthenticationPolicy should return the 401 response when it can't complete a challenge"""

    expected_response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})

    async def send(_):
        return expected_response

    transport = Mock(send=Mock(wraps=send))

    expected_scope = "scope"
    get_token = Mock(return_value=get_completed_future(AccessToken("***", 42)))
    credential = Mock(get_token=get_token)
    policy = AsyncChallengeAuthenticationPolicy(credential, expected_scope)
    policy.on_challenge = Mock(wraps=policy.on_challenge)

    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    response = await pipeline.run(HttpRequest("GET", "https://localhost"))

    assert policy.on_challenge.called
    assert response.http_response is expected_response
    assert transport.send.call_count == 1
    credential.get_token.assert_called_once_with(expected_scope)


def get_completed_future(result=None):
    fut = asyncio.Future()
    fut.set_result(result)
    return fut
