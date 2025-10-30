# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import base64
import sys
import time
from unittest.mock import Mock, patch, AsyncMock, create_autospec
from requests import Response

from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.credentials_async import AsyncTokenCredential, AsyncSupportsTokenInfo
from azure.core.exceptions import ServiceRequestError, HttpResponseError, ClientAuthenticationError
from azure.core.pipeline import AsyncPipeline, PipelineRequest, PipelineContext, PipelineResponse
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    SansIOHTTPPolicy,
    AsyncRedirectPolicy,
    SensitiveHeaderCleanupPolicy,
)
from azure.core.pipeline.policies._authentication import MAX_REFRESH_JITTER_SECONDS
from azure.core.pipeline.transport import AsyncHttpTransport, HttpRequest
import pytest
import trio

from utils import HTTP_REQUESTS


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_adds_header(http_request):
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    get_token_calls = 0

    async def get_token(*_, **__):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    fake_credential = Mock(spec_set=["get_token"], get_token=get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(http_request("GET", "https://spam.eggs"), context=None)
    assert get_token_calls == 1

    await pipeline.run(http_request("GET", "https://spam.eggs"), context=None)
    # Didn't need a new token
    assert get_token_calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_authorize_request(http_request):
    """The authorize_request method should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    fake_credential = Mock(spec_set=["get_token"], get_token=Mock(return_value=expected_token))
    policy = AsyncBearerTokenCredentialPolicy(fake_credential, "scope")
    http_req = http_request("GET", "https://spam.eggs")
    request = PipelineRequest(http_req, PipelineContext(None))

    await policy.authorize_request(request, "scope", claims="foo")
    assert policy._token is expected_token
    assert http_req.headers["Authorization"] == f"Bearer {expected_token.token}"
    assert fake_credential.get_token.call_count == 1
    assert fake_credential.get_token.call_args[0] == ("scope",)
    assert fake_credential.get_token.call_args[1] == {"claims": "foo", "enable_cae": True}


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_adds_header_access_token_info(http_request):
    """The bearer token policy should also add an auth header when an AccessTokenInfo is returned."""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    access_token = AccessToken("other_token", 2524608000)
    expected_token = AccessTokenInfo("expected_token", 2524608000, refresh_on=2524608000)

    async def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    get_token_calls = 0
    get_token_info_calls = 0

    class MockCredential(AsyncTokenCredential):
        async def get_token(self, *_, **__):
            nonlocal get_token_calls
            get_token_calls += 1
            return access_token

        async def get_token_info(*_, **__):
            nonlocal get_token_info_calls
            get_token_info_calls += 1
            return expected_token

    fake_credential: AsyncTokenCredential = MockCredential()
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]
    pipeline = AsyncPipeline(transport=AsyncMock(), policies=policies)

    await pipeline.run(http_request("GET", "https://spam.eggs"), context=None)
    assert get_token_info_calls == 1

    await pipeline.run(http_request("GET", "https://spam.eggs"), context=None)
    # Didn't need a new token
    assert get_token_info_calls == 1
    # get_token should not have been called
    assert get_token_calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_authorize_request_access_token_info(http_request):
    """The authorize_request method should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessTokenInfo("expected_token", 2524608000)
    fake_credential = Mock(get_token=Mock(), get_token_info=Mock(return_value=expected_token))
    policy = AsyncBearerTokenCredentialPolicy(fake_credential, "scope")
    http_req = http_request("GET", "https://spam.eggs")
    request = PipelineRequest(http_req, PipelineContext(None))

    await policy.authorize_request(request, "scope", claims="foo")
    assert policy._token is expected_token
    assert http_req.headers["Authorization"] == f"Bearer {expected_token.token}"
    assert fake_credential.get_token_info.call_args[0] == ("scope",)
    assert fake_credential.get_token_info.call_args[1] == {"options": {"claims": "foo", "enable_cae": True}}


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_send(http_request):
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = http_request("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    get_token = get_completed_future(AccessToken("***", 42))
    fake_credential = Mock(spec_set=["get_token"], get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_sync_send(http_request):
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = http_request("GET", "https://spam.eggs")
    expected_response = Mock()

    async def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    get_token = get_completed_future(AccessToken("***", 42))
    fake_credential = Mock(spec_set=["get_token"], get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = await AsyncPipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_token_caching(http_request):
    good_for_one_hour = AccessToken("token", int(time.time() + 3600))
    expected_token = good_for_one_hour
    get_token_calls = 0

    async def get_token(*_, **__):
        nonlocal get_token_calls
        get_token_calls += 1
        return expected_token

    credential = Mock(spec_set=["get_token"], get_token=get_token)
    policies = [
        AsyncBearerTokenCredentialPolicy(credential, "scope"),
        Mock(send=Mock(return_value=get_completed_future(Mock()))),
    ]
    pipeline = AsyncPipeline(transport=Mock, policies=policies)

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # policy has no token at first request -> it should call get_token

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert get_token_calls == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", int(time.time()))
    get_token_calls = 0
    expected_token = expired_token
    policies = [
        AsyncBearerTokenCredentialPolicy(credential, "scope"),
        Mock(send=lambda _: get_completed_future(Mock())),
    ]
    pipeline = AsyncPipeline(transport=Mock(), policies=policies)

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert get_token_calls == 1

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert get_token_calls == 2  # token expired -> policy should call get_token


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_access_token_info_caching(http_request):
    """The policy should cache AccessTokenInfo instances and refresh them when necessary."""

    good_for_one_hour = AccessTokenInfo("token", int(time.time() + 3600))

    credential = create_autospec(AsyncSupportsTokenInfo, instance=True, spec_set=True)
    credential.get_token_info = AsyncMock(return_value=good_for_one_hour)
    pipeline = AsyncPipeline(transport=AsyncMock(), policies=[AsyncBearerTokenCredentialPolicy(credential, "scope")])

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert (
        credential.get_token_info.call_count == 1
    )  # policy has no token at first request -> it should call get_token_info

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessTokenInfo("token", int(time.time()))
    credential.get_token_info.reset_mock()
    credential.get_token_info.return_value = expired_token
    pipeline = AsyncPipeline(transport=AsyncMock(), policies=[AsyncBearerTokenCredentialPolicy(credential, "scope")])

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 1

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 2  # token is expired -> policy should call get_token_info again

    refreshable_token = AccessTokenInfo(
        "token", int(time.time() + 3600), refresh_on=int(time.time() - (MAX_REFRESH_JITTER_SECONDS + 5))
    )
    credential.get_token_info.reset_mock()
    credential.get_token_info.return_value = refreshable_token
    pipeline = AsyncPipeline(transport=AsyncMock(), policies=[AsyncBearerTokenCredentialPolicy(credential, "scope")])

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 1

    await pipeline.run(http_request("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 2  # token refresh-on time has passed, call again


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_optionally_enforces_https(http_request):
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    async def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "AsyncBearerTokenCredentialPolicy didn't pop the 'enforce_https' option"
        return Mock()

    credential = Mock(spec_set=["get_token"], get_token=lambda *_, **__: get_completed_future(AccessToken("***", 42)))
    pipeline = AsyncPipeline(
        transport=Mock(send=assert_option_popped), policies=[AsyncBearerTokenCredentialPolicy(credential, "scope")]
    )

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        await pipeline.run(http_request("GET", "http://not.secure"))
    with pytest.raises(ServiceRequestError):
        await pipeline.run(http_request("GET", "http://not.secure"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    await pipeline.run(http_request("GET", "http://not.secure"), enforce_https=False)

    # https requests should always pass
    await pipeline.run(http_request("GET", "https://secure"), enforce_https=False)
    await pipeline.run(http_request("GET", "https://secure"), enforce_https=True)
    await pipeline.run(http_request("GET", "https://secure"))


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_preserves_enforce_https_opt_out(http_request):
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"
            return Mock()

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(spec_set=["get_token"], get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=Mock(send=lambda *_, **__: get_completed_future(Mock())), policies=policies)

    await pipeline.run(http_request("GET", "http://not.secure"), enforce_https=False)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_context_unmodified_by_default(http_request):
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"
            return Mock()

    get_token = get_completed_future(AccessToken("***", 42))
    credential = Mock(spec_set=["get_token"], get_token=lambda *_, **__: get_token)
    policies = [AsyncBearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = AsyncPipeline(transport=Mock(send=lambda *_, **__: get_completed_future(Mock())), policies=policies)

    await pipeline.run(http_request("GET", "https://secure"))


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_bearer_policy_calls_sansio_methods(http_request):
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
        get_token=Mock(return_value=get_completed_future(AccessToken("***", int(time.time()) + 3600))),
    )
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=get_completed_future(Mock(status_code=200))))

    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    await pipeline.run(http_request("GET", "https://localhost"))

    policy.on_request.assert_called_once_with(policy.request)
    policy.on_response.assert_called_once_with(policy.request, policy.response)

    # the policy should call on_exception when next.send() raises
    class TestException(Exception):
        pass

    # during the first send...
    transport = Mock(send=Mock(side_effect=TestException))
    policy = TestPolicy(credential, "scope")
    pipeline = AsyncPipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        await pipeline.run(http_request("GET", "https://localhost"))
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
        await pipeline.run(http_request("GET", "https://localhost"))
    assert transport.send.call_count == 2
    policy.on_challenge.assert_called_once()
    policy.on_exception.assert_called_once_with(policy.request)


def get_completed_future(result=None):
    fut = asyncio.Future()
    fut.set_result(result)
    return fut


@pytest.mark.asyncio
async def test_bearer_policy_redirect_same_domain():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._first = True

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                assert request.headers["Authorization"] == "Bearer {}".format(auth_headder)
                response = Response()
                response.status_code = 301
                response.headers["location"] = "https://localhost"
                return response
            assert request.headers["Authorization"] == "Bearer {}".format(auth_headder)
            response = Response()
            response.status_code = 200
            return response

    auth_headder = "token"
    expected_scope = "scope"

    async def get_token(*_, **__):
        token = AccessToken(auth_headder, 0)
        return token

    credential = Mock(spec_set=["get_token"], get_token=get_token)
    auth_policy = AsyncBearerTokenCredentialPolicy(credential, expected_scope)
    redirect_policy = AsyncRedirectPolicy()
    header_clean_up_policy = SensitiveHeaderCleanupPolicy()
    pipeline = AsyncPipeline(transport=MockTransport(), policies=[redirect_policy, auth_policy, header_clean_up_policy])

    await pipeline.run(HttpRequest("GET", "https://localhost"))


@pytest.mark.asyncio
async def test_bearer_policy_redirect_different_domain():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._first = True

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                assert request.headers["Authorization"] == "Bearer {}".format(auth_headder)
                response = Response()
                response.status_code = 301
                response.headers["location"] = "https://localhost1"
                return response
            assert not request.headers.get("Authorization")
            response = Response()
            response.status_code = 200
            return response

    auth_headder = "token"
    expected_scope = "scope"

    async def get_token(*_, **__):
        token = AccessToken(auth_headder, 0)
        return token

    credential = Mock(spec_set=["get_token"], get_token=get_token)
    auth_policy = AsyncBearerTokenCredentialPolicy(credential, expected_scope)
    redirect_policy = AsyncRedirectPolicy()
    header_clean_up_policy = SensitiveHeaderCleanupPolicy()
    pipeline = AsyncPipeline(transport=MockTransport(), policies=[redirect_policy, auth_policy, header_clean_up_policy])

    await pipeline.run(HttpRequest("GET", "https://localhost"))


@pytest.mark.asyncio
async def test_bearer_policy_redirect_opt_out_clean_up():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._first = True

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                assert request.headers["Authorization"] == "Bearer {}".format(auth_headder)
                response = Response()
                response.status_code = 301
                response.headers["location"] = "https://localhost1"
                return response
            assert request.headers["Authorization"] == "Bearer {}".format(auth_headder)
            response = Response()
            response.status_code = 200
            return response

    auth_headder = "token"
    expected_scope = "scope"

    async def get_token(*_, **__):
        token = AccessToken(auth_headder, 0)
        return token

    credential = Mock(spec_set=["get_token"], get_token=get_token)
    auth_policy = AsyncBearerTokenCredentialPolicy(credential, expected_scope)
    redirect_policy = AsyncRedirectPolicy()
    header_clean_up_policy = SensitiveHeaderCleanupPolicy(disable_redirect_cleanup=True)
    pipeline = AsyncPipeline(transport=MockTransport(), policies=[redirect_policy, auth_policy, header_clean_up_policy])

    await pipeline.run(HttpRequest("GET", "https://localhost"))


@pytest.mark.asyncio
async def test_bearer_policy_redirect_customize_sensitive_headers():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._first = True

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                assert request.headers["Authorization"] == "Bearer {}".format(auth_headder)
                response = Response()
                response.status_code = 301
                response.headers["location"] = "https://localhost1"
                return response
            assert request.headers.get("Authorization")
            response = Response()
            response.status_code = 200
            return response

    auth_headder = "token"
    expected_scope = "scope"

    async def get_token(*_, **__):
        token = AccessToken(auth_headder, 0)
        return token

    credential = Mock(spec_set=["get_token"], get_token=get_token)
    auth_policy = AsyncBearerTokenCredentialPolicy(credential, expected_scope)
    redirect_policy = AsyncRedirectPolicy()
    header_clean_up_policy = SensitiveHeaderCleanupPolicy(blocked_redirect_headers=["x-ms-authorization-auxiliary"])
    pipeline = AsyncPipeline(transport=MockTransport(), policies=[redirect_policy, auth_policy, header_clean_up_policy])

    await pipeline.run(HttpRequest("GET", "https://localhost"))


@pytest.mark.asyncio
async def test_async_token_credential_inheritance():
    class TestTokenCredential(AsyncTokenCredential):
        async def get_token(self, *scopes, **kwargs):
            return "TOKEN"

    cred = TestTokenCredential()
    await cred.get_token("scope")


@pytest.mark.asyncio
async def test_async_token_credential_asyncio_lock():
    auth_policy = AsyncBearerTokenCredentialPolicy(Mock(), "scope")
    assert isinstance(auth_policy._lock, asyncio.Lock)


@pytest.mark.trio
async def test_async_token_credential_trio_lock():
    auth_policy = AsyncBearerTokenCredentialPolicy(Mock(), "scope")
    assert isinstance(auth_policy._lock, trio.Lock)


def test_async_token_credential_sync():
    """Verify that AsyncBearerTokenCredentialPolicy can be constructed in a synchronous context."""
    auth_policy = AsyncBearerTokenCredentialPolicy(Mock(), "scope")
    with patch.dict("sys.modules"):
        # Ensure trio isn't in sys.modules (i.e. imported).
        sys.modules.pop("trio", None)
        AsyncBearerTokenCredentialPolicy(Mock(), "scope")


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_async_bearer_policy_on_challenge_caches_token(http_request):
    """Test that async on_challenge caches the token when handling claims challenges"""
    # Setup credentials that return different tokens for different calls
    initial_token = AccessToken("initial_token", int(time.time()) + 3600)
    claims_token = AccessToken("claims_token", int(time.time()) + 3600)

    call_count = 0

    async def mock_get_token_info(*scopes, options=None):
        nonlocal call_count
        call_count += 1
        if options and "claims" in options:
            return claims_token
        return initial_token

    fake_credential = Mock(spec_set=["get_token_info"], get_token_info=mock_get_token_info)
    policy = AsyncBearerTokenCredentialPolicy(fake_credential, "scope")

    # Create request and initial response
    http_req = http_request("GET", "https://example.com")
    request = PipelineRequest(http_req, PipelineContext(None))

    # Create a 401 response with insufficient_claims challenge
    test_claims = '{"access_token":{"foo":"bar"}}'
    encoded_claims = base64.urlsafe_b64encode(test_claims.encode()).decode().rstrip("=")
    challenge_header = f'Bearer error="insufficient_claims", claims="{encoded_claims}"'

    response_mock = Mock(status_code=401, headers={"WWW-Authenticate": challenge_header})
    response = PipelineResponse(request, response_mock, PipelineContext(None))

    # Call on_challenge
    result = await policy.on_challenge(request, response)

    # Verify the challenge was handled successfully
    assert result is True

    # Verify the token was cached
    assert policy._token is claims_token
    assert policy._token.token == "claims_token"

    # Verify the Authorization header was set correctly
    assert request.http_request.headers["Authorization"] == "Bearer claims_token"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_async_bearer_policy_on_challenge_exception_chaining(http_request):
    """Test that exceptions during async on_challenge are chained with HttpResponseError"""

    # Mock credential that raises an exception during get_token_info with claims
    async def mock_get_token_info(*scopes, options=None):
        if options and "claims" in options:
            raise ClientAuthenticationError("Failed to request token info with claims")
        return AccessTokenInfo("initial_token", int(time.time()) + 3600)

    fake_credential = Mock(
        spec_set=["get_token", "get_token_info"],
        get_token=AsyncMock(return_value=AccessToken("fallback", int(time.time()) + 3600)),
        get_token_info=mock_get_token_info,
    )
    policy = AsyncBearerTokenCredentialPolicy(fake_credential, "scope")

    # Create a 401 response with insufficient_claims challenge
    test_claims = '{"access_token":{"foo":"bar"}}'
    encoded_claims = base64.urlsafe_b64encode(test_claims.encode()).decode().rstrip("=")
    challenge_header = f'Bearer error="insufficient_claims", claims="{encoded_claims}"'

    response_mock = Mock(status_code=401, headers={"WWW-Authenticate": challenge_header})

    # Mock transport that returns the 401 response
    async def mock_transport_send(request):
        return response_mock

    transport = Mock(send=mock_transport_send)
    pipeline = AsyncPipeline(transport=transport, policies=[policy])

    # Execute the request and verify exception chaining
    with pytest.raises(ClientAuthenticationError) as exc_info:
        await pipeline.run(http_request("GET", "https://example.com"))

    # Verify the original exception is preserved
    original_exception = exc_info.value
    assert original_exception.message == "Failed to request token info with claims"

    # Verify the exception is chained with HttpResponseError
    assert original_exception.__cause__ is not None
    assert isinstance(original_exception.__cause__, HttpResponseError)

    # Verify the HttpResponseError contains the original 401 response
    http_response_error = original_exception.__cause__
    assert http_response_error.response is response_mock


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_async_bearer_policy_reads_streamed_response_on_challenge_exception(http_request):
    """Test that the async policy reads streamed response body when on_challenge raises exception"""

    # Create a credential that will raise an exception when get_token is called with claims
    async def failing_get_token(*scopes, **kwargs):
        if "claims" in kwargs:
            raise ClientAuthenticationError("Failed to get token with claims")
        return AccessToken("initial_token", int(time.time()) + 3600)

    credential = Mock(spec_set=["get_token"], get_token=failing_get_token)
    policy = AsyncBearerTokenCredentialPolicy(credential, "scope")

    # Create a 401 response with insufficient_claims challenge that will trigger the exception
    test_claims = '{"access_token":{"foo":"bar"}}'
    encoded_claims = base64.urlsafe_b64encode(test_claims.encode()).decode().rstrip("=")
    challenge_header = f'Bearer error="insufficient_claims", claims="{encoded_claims}"'

    # Create the mock HTTP response with stream reading capability
    http_response_mock = Mock()
    http_response_mock.status_code = 401
    http_response_mock.headers = {"WWW-Authenticate": challenge_header}
    http_response_mock.read = AsyncMock(return_value=b"Error details from server")

    # Mock transport that returns the HTTP response directly (it will be wrapped by Pipeline)
    async def mock_transport_send(request, **kwargs):
        return http_response_mock

    transport = Mock(send=mock_transport_send)

    # Create pipeline with stream option
    pipeline = AsyncPipeline(transport=transport, policies=[policy])

    # Execute the request and verify exception handling
    with pytest.raises(ClientAuthenticationError) as exc_info:
        await pipeline.run(http_request("GET", "https://example.com"), stream=True)

    # Verify that the response.read() was called to consume the stream
    http_response_mock.read.assert_called_once()

    # Verify the exception chaining
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, HttpResponseError)
