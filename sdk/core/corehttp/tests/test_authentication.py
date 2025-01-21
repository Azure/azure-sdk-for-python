# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
from unittest.mock import Mock

from corehttp.credentials import AccessTokenInfo, ServiceKeyCredential, ServiceNamedKeyCredential
from corehttp.exceptions import ServiceRequestError
from corehttp.runtime.pipeline import Pipeline
from corehttp.runtime.policies import (
    BearerTokenCredentialPolicy,
    SansIOHTTPPolicy,
    ServiceKeyCredentialPolicy,
)
from corehttp.rest import HttpRequest
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
import pytest


def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessTokenInfo("expected_token", 2524608000)

    def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    fake_credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(return_value=expected_token))
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]

    pipeline = Pipeline(transport=Mock(), policies=policies)
    pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    assert fake_credential.get_token_info.call_count == 1

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    # Didn't need a new token
    assert fake_credential.get_token_info.call_count == 1


def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock()

    def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    def get_token_info(*_, **__):
        return AccessTokenInfo("***", 42)

    fake_credential = Mock(spec_set=["get_token_info"], get_token_info=get_token_info)
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = Pipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


def test_bearer_policy_token_caching():
    good_for_one_hour = AccessTokenInfo("token", int(time.time()) + 3600)
    credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(return_value=good_for_one_hour))
    pipeline = Pipeline(transport=Mock(), policies=[BearerTokenCredentialPolicy(credential, "scope")])

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 1  # policy has no token at first request -> it should call get_token

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessTokenInfo("token", int(time.time()))
    credential.get_token_info.reset_mock()
    credential.get_token_info.return_value = expired_token
    pipeline = Pipeline(transport=Mock(), policies=[BearerTokenCredentialPolicy(credential, "scope")])

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 1

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token_info.call_count == 2  # token expired -> policy should call get_token


def test_bearer_policy_optionally_enforces_https():
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "BearerTokenCredentialPolicy didn't pop the 'enforce_https' option"
        return Mock()

    def get_token_info(*_, **__):
        return AccessTokenInfo("***", 42)

    credential = Mock(spec_set=["get_token_info"], get_token_info=get_token_info)
    pipeline = Pipeline(
        transport=Mock(send=assert_option_popped), policies=[BearerTokenCredentialPolicy(credential, "scope")]
    )

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        pipeline.run(HttpRequest("GET", "http://not.secure"))
    with pytest.raises(ServiceRequestError):
        pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)

    # https requests should always pass
    pipeline.run(HttpRequest("GET", "https://secure"), enforce_https=False)
    pipeline.run(HttpRequest("GET", "https://secure"), enforce_https=True)
    pipeline.run(HttpRequest("GET", "https://secure"))


def test_bearer_policy_preserves_enforce_https_opt_out():
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"
            return Mock()

    credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(return_value=AccessTokenInfo("***", 42)))
    policies = [BearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)


def test_bearer_policy_default_context():
    """The policy should call get_token with the scopes given at construction, and no keyword arguments, by default"""
    expected_scope = "scope"
    token = AccessTokenInfo("", 0)
    credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(return_value=token))
    policy = BearerTokenCredentialPolicy(credential, expected_scope)
    pipeline = Pipeline(transport=Mock(), policies=[policy])

    pipeline.run(HttpRequest("GET", "https://localhost"))

    credential.get_token_info.assert_called_once_with(expected_scope)


def test_bearer_policy_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(return_value=AccessTokenInfo("***", 42)))
    policies = [BearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "https://secure"))


def test_bearer_policy_calls_on_challenge():
    """BearerTokenCredentialPolicy should call its on_challenge method when it receives an authentication challenge"""

    class TestPolicy(BearerTokenCredentialPolicy):
        called = False

        def on_challenge(self, request, challenge):
            self.__class__.called = True
            return False

    credential = Mock(
        spec_set=["get_token_info"], get_token_info=Mock(return_value=AccessTokenInfo("***", int(time.time()) + 3600))
    )
    policies = [TestPolicy(credential, "scope")]
    response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
    transport = Mock(send=Mock(return_value=response))

    pipeline = Pipeline(transport=transport, policies=policies)
    pipeline.run(HttpRequest("GET", "https://localhost"))

    assert TestPolicy.called


def test_bearer_policy_cannot_complete_challenge():
    """BearerTokenCredentialPolicy should return the 401 response when it can't complete its challenge"""

    expected_scope = "scope"
    expected_token = AccessTokenInfo("***", int(time.time()) + 3600)
    credential = Mock(spec_set=["get_token_info"], get_token_info=Mock(return_value=expected_token))
    expected_response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
    transport = Mock(send=Mock(return_value=expected_response))
    policies = [BearerTokenCredentialPolicy(credential, expected_scope)]

    pipeline = Pipeline(transport=transport, policies=policies)
    response = pipeline.run(HttpRequest("GET", "https://localhost"))

    assert response.http_response is expected_response
    assert transport.send.call_count == 1
    credential.get_token_info.assert_called_once_with(expected_scope)


def test_bearer_policy_calls_sansio_methods():
    """BearerTokenCredentialPolicy should call SansIOHttpPolicy methods as does _SansIOHTTPPolicyRunner"""

    class TestPolicy(BearerTokenCredentialPolicy):
        def __init__(self, *args, **kwargs):
            super(TestPolicy, self).__init__(*args, **kwargs)
            self.on_exception = Mock(return_value=False)
            self.on_request = Mock()
            self.on_response = Mock()

        def send(self, request):
            self.request = request
            self.response = super(TestPolicy, self).send(request)
            return self.response

    credential = Mock(
        spec_set=["get_token_info"], get_token_info=Mock(return_value=AccessTokenInfo("***", int(time.time()) + 3600))
    )
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=Mock(status_code=200)))

    pipeline = Pipeline(transport=transport, policies=[policy])
    pipeline.run(HttpRequest("GET", "https://localhost"))

    policy.on_request.assert_called_once_with(policy.request)
    policy.on_response.assert_called_once_with(policy.request, policy.response)

    # the policy should call on_exception when next.send() raises
    class TestException(Exception):
        pass

    # during the first send...
    transport = Mock(send=Mock(side_effect=TestException))
    policy = TestPolicy(credential, "scope")
    pipeline = Pipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        pipeline.run(HttpRequest("GET", "https://localhost"))
    policy.on_exception.assert_called_once_with(policy.request)

    # ...or the second
    def raise_the_second_time(*args, **kwargs):
        if raise_the_second_time.calls == 0:
            raise_the_second_time.calls = 1
            return Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
        raise TestException()

    raise_the_second_time.calls = 0

    policy = TestPolicy(credential, "scope")
    policy.on_challenge = Mock(return_value=True)
    transport = Mock(send=Mock(wraps=raise_the_second_time))
    pipeline = Pipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        pipeline.run(HttpRequest("GET", "https://localhost"))
    assert transport.send.call_count == 2
    policy.on_challenge.assert_called_once()
    policy.on_exception.assert_called_once_with(policy.request)


def test_azure_core_sans_io_policy():
    """Tests to see that we can use an azure.core SansIOHTTPPolicy with the corehttp Pipeline"""

    class TestPolicy(AzureKeyCredentialPolicy):
        def __init__(self, *args, **kwargs):
            super(TestPolicy, self).__init__(*args, **kwargs)
            self.on_exception = Mock(return_value=False)
            self.on_request = Mock()

    credential = Mock(key="key")
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=Mock(status_code=200)))

    pipeline = Pipeline(transport=transport, policies=[policy])
    pipeline.run(HttpRequest("GET", "https://localhost"))

    policy.on_request.assert_called_once()


def test_service_key_credential_policy():
    """Tests to see if we can create an ServiceKeyCredentialPolicy"""

    key_header = "api_key"
    api_key = "test_key"

    def verify_authorization_header(request):
        assert request.headers[key_header] == api_key

    transport = Mock(send=verify_authorization_header)
    credential = ServiceKeyCredential(api_key)
    credential_policy = ServiceKeyCredentialPolicy(credential=credential, name=key_header)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(HttpRequest("GET", "https://test_key_credential"))


def test_service_key_credential_policy_raises():
    """Tests ServiceKeyCredential and ServiceKeyCredentialPolicy raises with non-compliant input parameters."""
    api_key = 1234
    key_header = 5678
    with pytest.raises(TypeError):
        credential = ServiceKeyCredential(api_key)

    credential = ServiceKeyCredential(str(api_key))
    with pytest.raises(TypeError):
        credential_policy = ServiceKeyCredentialPolicy(credential=credential, name=key_header)

    with pytest.raises(TypeError):
        credential_policy = ServiceKeyCredentialPolicy(credential=str(api_key), name=key_header)


def test_service_key_credential_updates():
    """Tests ServiceKeyCredential updates"""
    api_key = "original"

    credential = ServiceKeyCredential(api_key)
    assert credential.key == api_key

    api_key = "new"
    credential.update(api_key)
    assert credential.key == api_key


combinations = [
    ("sig=test_signature", "https://test_sas_credential", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential", "https://test_sas_credential?sig=test_signature"),
    (
        "sig=test_signature",
        "https://test_sas_credential?sig=test_signature",
        "https://test_sas_credential?sig=test_signature",
    ),
    (
        "?sig=test_signature",
        "https://test_sas_credential?sig=test_signature",
        "https://test_sas_credential?sig=test_signature",
    ),
    ("sig=test_signature", "https://test_sas_credential?", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?", "https://test_sas_credential?sig=test_signature"),
    (
        "sig=test_signature",
        "https://test_sas_credential?foo=bar",
        "https://test_sas_credential?foo=bar&sig=test_signature",
    ),
    (
        "?sig=test_signature",
        "https://test_sas_credential?foo=bar",
        "https://test_sas_credential?foo=bar&sig=test_signature",
    ),
]


def test_service_named_key_credential():
    cred = ServiceNamedKeyCredential("sample_name", "samplekey")

    assert cred.named_key.name == "sample_name"
    assert cred.named_key.key == "samplekey"
    assert isinstance(cred.named_key, tuple)

    cred.update("newname", "newkey")
    assert cred.named_key.name == "newname"
    assert cred.named_key.key == "newkey"
    assert isinstance(cred.named_key, tuple)


def test_service_named_key_credential_raises():
    with pytest.raises(TypeError, match="Both name and key must be strings."):
        cred = ServiceNamedKeyCredential("sample_name", 123345)

    cred = ServiceNamedKeyCredential("sample_name", "samplekey")
    assert cred.named_key.name == "sample_name"
    assert cred.named_key.key == "samplekey"

    with pytest.raises(TypeError, match="Both name and key must be strings."):
        cred.update(1234, "newkey")


def test_service_http_credential_policy():
    """Tests to see if we can create an ServiceKeyCredentialPolicy"""

    prefix = "SharedAccessKey"
    api_key = "test_key"
    header_content = f"{prefix} {api_key}"

    def verify_authorization_header(request):
        assert request.headers["Authorization"] == header_content

    transport = Mock(send=verify_authorization_header)
    credential = ServiceKeyCredential(api_key)
    credential_policy = ServiceKeyCredentialPolicy(credential=credential, name="Authorization", prefix=prefix)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(HttpRequest("GET", "https://test_key_credential"))


def test_need_new_token():
    expected_scope = "scope"
    now = int(time.time())

    policy = BearerTokenCredentialPolicy(Mock(), expected_scope)

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
