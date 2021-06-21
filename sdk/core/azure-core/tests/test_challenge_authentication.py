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
import time

from azure.core.credentials import AccessToken
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import ChallengeAuthenticationPolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpRequest

import pytest

try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock


def test_adds_header():
    """The policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    fake_credential = Mock(get_token=Mock(return_value=expected_token))
    policy = ChallengeAuthenticationPolicy(fake_credential, "scope")
    policies = [policy, Mock(send=verify_authorization_header)]

    pipeline = Pipeline(transport=Mock(), policies=policies)
    pipeline.run(HttpRequest("GET", "https://localhost"))

    assert fake_credential.get_token.call_count == 1

    pipeline.run(HttpRequest("GET", "https://localhost"))

    # Didn't need a new token
    assert fake_credential.get_token.call_count == 1


def test_default_context():
    """The policy should call get_token with the scopes given at construction, and no keyword arguments, by default"""
    expected_scope = "scope"
    token = AccessToken("", 0)
    credential = Mock(get_token=Mock(return_value=token))
    policy = ChallengeAuthenticationPolicy(credential, expected_scope)
    pipeline = Pipeline(transport=Mock(), policies=[policy])

    pipeline.run(HttpRequest("GET", "https://localhost"))

    credential.get_token.assert_called_once_with(expected_scope)


def test_send():
    """The policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://localhost")
    expected_response = Mock()

    def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda _: AccessToken("", 0))
    policy = ChallengeAuthenticationPolicy(fake_credential, "scope")
    policies = [policy, Mock(send=verify_request)]
    response = Pipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


def test_token_caching():
    good_for_one_hour = AccessToken("token", time.time() + 3600)
    credential = Mock(get_token=Mock(return_value=good_for_one_hour))
    policy = ChallengeAuthenticationPolicy(credential, "scope")
    pipeline = Pipeline(transport=Mock(), policies=[policy])

    pipeline.run(HttpRequest("GET", "https://localhost"))
    assert credential.get_token.call_count == 1  # policy has no token at first request -> it should call get_token

    pipeline.run(HttpRequest("GET", "https://localhost"))
    assert credential.get_token.call_count == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    credential.get_token.reset_mock()
    credential.get_token.return_value = expired_token
    pipeline = Pipeline(transport=Mock(), policies=[ChallengeAuthenticationPolicy(credential, "scope")])

    pipeline.run(HttpRequest("GET", "https://localhost"))
    assert credential.get_token.call_count == 1

    pipeline.run(HttpRequest("GET", "https://localhost"))
    assert credential.get_token.call_count == 2  # token expired -> policy should call get_token


def test_optionally_enforces_https():
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "ChallengeAuthenticationPolicy didn't pop the 'enforce_https' option"
        return Mock()

    credential = Mock(get_token=lambda *_, **__: AccessToken("***", 42))
    policy = ChallengeAuthenticationPolicy(credential, "scope")
    pipeline = Pipeline(transport=Mock(send=assert_option_popped), policies=[policy])

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        pipeline.run(HttpRequest("GET", "http://localhost"))
    with pytest.raises(ServiceRequestError):
        pipeline.run(HttpRequest("GET", "http://localhost"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    pipeline.run(HttpRequest("GET", "http://localhost"), enforce_https=False)

    # https requests should always pass
    pipeline.run(HttpRequest("GET", "https://localhost"), enforce_https=False)
    pipeline.run(HttpRequest("GET", "https://localhost"), enforce_https=True)
    pipeline.run(HttpRequest("GET", "https://localhost"))


def test_preserves_enforce_https_opt_out():
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"
            return Mock()

    credential = Mock(get_token=Mock(return_value=AccessToken("***", 42)))
    policy = ChallengeAuthenticationPolicy(credential, "scope")
    pipeline = Pipeline(transport=Mock(), policies=[policy])

    pipeline.run(HttpRequest("GET", "http://localhost"), enforce_https=False)


def test_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    credential = Mock(get_token=Mock(return_value=AccessToken("***", 42)))
    policy = ChallengeAuthenticationPolicy(credential, "scope")
    policies = [policy, ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "https://localhost"))


def test_cannot_complete_challenge():
    """ChallengeAuthenticationPolicy should return the 401 response when it can't complete a challenge"""

    expected_scope = "scope"
    expected_token = AccessToken("***", int(time.time()) + 3600)
    credential = Mock(get_token=Mock(return_value=expected_token))
    expected_response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
    transport = Mock(send=Mock(return_value=expected_response))
    policy = ChallengeAuthenticationPolicy(credential, expected_scope)
    policy.on_challenge = Mock(wraps=policy.on_challenge)

    pipeline = Pipeline(transport=transport, policies=[policy])
    response = pipeline.run(HttpRequest("GET", "https://localhost"))

    assert policy.on_challenge.called
    assert response.http_response is expected_response
    assert transport.send.call_count == 1
    credential.get_token.assert_called_once_with(expected_scope)
