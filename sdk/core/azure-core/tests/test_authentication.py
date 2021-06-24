# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import functools
import azure.core
from azure.core.credentials import AccessToken, AzureKeyCredential, AzureSasCredential, AzureNamedKeyCredential
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    BearerTokenCredentialPolicy,
    SansIOHTTPPolicy,
    AzureKeyCredentialPolicy,
    AzureSasCredentialPolicy,
)
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
import pytest

try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_adds_header(request_type, add_supported_format_rest_to_mock):
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)
        return Mock()

    fake_credential = Mock(get_token=Mock(return_value=expected_token))
    second_policy = Mock(send=verify_authorization_header)
    add_supported_format_rest_to_mock(second_policy)
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), second_policy]

    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=policies)
    pipeline.run(request_type("GET", "https://spam.eggs"))

    assert fake_credential.get_token.call_count == 1

    pipeline.run(request_type("GET", "https://spam.eggs"))

    # Didn't need a new token
    assert fake_credential.get_token.call_count == 1

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_send(request_type, add_supported_format_rest_to_mock):
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = request_type("GET", "https://spam.eggs")
    expected_response = Mock()
    if hasattr(request_type, "body"):
        # this is bc we do a format check on the response before passing it back
        # if it has a body, we assume the response is pipeline transport
        # else, we think it's rest
        expected_response.body = ""
    else:
        expected_response.content == ""

    def verify_request(request):
        if hasattr(request_type, "body"):
            # since we have to create a new http request for PipelineTransport tests,
            # it will not be the same request object
            assert request.http_request.method == "GET"
            assert request.http_request.url == "https://spam.eggs"
        else:
            assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda _: AccessToken("", 0))
    second_policy = Mock(send=verify_request)
    add_supported_format_rest_to_mock(second_policy)
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), second_policy]
    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    response = Pipeline(transport=transport, policies=policies).run(expected_request)
    if hasattr(request_type, "content"):
        # can't do this check for pipline transport reponses bc we have to convert
        # the response from a REST response to a pipeline transport response
        assert response is expected_response


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_token_caching(request_type, add_supported_format_rest_to_mock):
    good_for_one_hour = AccessToken("token", time.time() + 3600)
    credential = Mock(get_token=Mock(return_value=good_for_one_hour))
    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=[BearerTokenCredentialPolicy(credential, "scope")])

    pipeline.run(request_type("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 1  # policy has no token at first request -> it should call get_token

    pipeline.run(request_type("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    credential.get_token.reset_mock()
    credential.get_token.return_value = expired_token

    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=[BearerTokenCredentialPolicy(credential, "scope")])

    pipeline.run(request_type("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 1

    pipeline.run(request_type("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 2  # token expired -> policy should call get_token


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_optionally_enforces_https(request_type, add_supported_format_rest_to_mock):
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "BearerTokenCredentialPolicy didn't pop the 'enforce_https' option"
        return Mock()

    credential = Mock(get_token=lambda *_, **__: AccessToken("***", 42))
    transport = Mock(send=assert_option_popped)
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(
        transport=transport, policies=[BearerTokenCredentialPolicy(credential, "scope")]
    )

    # by default and when enforce_https=True, the policy should raise when given an insecure request
    with pytest.raises(ServiceRequestError):
        pipeline.run(request_type("GET", "http://not.secure"))
    with pytest.raises(ServiceRequestError):
        pipeline.run(request_type("GET", "http://not.secure"), enforce_https=True)

    # when enforce_https=False, an insecure request should pass
    pipeline.run(request_type("GET", "http://not.secure"), enforce_https=False)

    # https requests should always pass
    pipeline.run(request_type("GET", "https://secure"), enforce_https=False)
    pipeline.run(request_type("GET", "https://secure"), enforce_https=True)
    pipeline.run(request_type("GET", "https://secure"))


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_preserves_enforce_https_opt_out(request_type, add_supported_format_rest_to_mock):
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"
            return Mock()

    credential = Mock(get_token=Mock(return_value=AccessToken("***", 42)))
    policies = [BearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=policies)

    pipeline.run(request_type("GET", "http://not.secure"), enforce_https=False)


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_default_context(request_type, add_supported_format_rest_to_mock):
    """The policy should call get_token with the scopes given at construction, and no keyword arguments, by default"""
    expected_scope = "scope"
    token = AccessToken("", 0)
    credential = Mock(get_token=Mock(return_value=token))
    policy = BearerTokenCredentialPolicy(credential, expected_scope)

    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=[policy])

    pipeline.run(request_type("GET", "https://localhost"))

    credential.get_token.assert_called_once_with(expected_scope)


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_context_unmodified_by_default(request_type, add_supported_format_rest_to_mock):
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    credential = Mock(get_token=Mock(return_value=AccessToken("***", 42)))
    policies = [BearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]

    transport = Mock()
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=policies)

    pipeline.run(request_type("GET", "https://secure"))


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_calls_on_challenge(request_type, add_supported_format_rest_to_mock):
    """BearerTokenCredentialPolicy should call its on_challenge method when it receives an authentication challenge"""

    class TestPolicy(BearerTokenCredentialPolicy):
        called = False

        def on_challenge(self, request, challenge):
            self.__class__.called = True
            return False

    credential = Mock(get_token=Mock(return_value=AccessToken("***", int(time.time()) + 3600)))
    policies = [TestPolicy(credential, "scope")]
    response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
    transport = Mock(send=Mock(return_value=response))

    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=policies)
    pipeline.run(request_type("GET", "https://localhost"))

    assert TestPolicy.called


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_cannot_complete_challenge(request_type, add_supported_format_rest_to_mock):
    """BearerTokenCredentialPolicy should return the 401 response when it can't complete its challenge"""

    expected_scope = "scope"
    expected_token = AccessToken("***", int(time.time()) + 3600)
    credential = Mock(get_token=Mock(return_value=expected_token))
    expected_response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
    transport = Mock(send=Mock(return_value=expected_response))
    add_supported_format_rest_to_mock(transport)
    policies = [BearerTokenCredentialPolicy(credential, expected_scope)]

    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=policies)
    response = pipeline.run(request_type("GET", "https://localhost"))

    if hasattr(request_type, "content"):
        assert response.http_response is expected_response
    else:
        a = "b"
    assert transport.send.call_count == 1
    credential.get_token.assert_called_once_with(expected_scope)


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_bearer_policy_calls_sansio_methods(request_type, add_supported_format_rest_to_mock):
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

    credential = Mock(get_token=Mock(return_value=AccessToken("***", int(time.time()) + 3600)))
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=Mock(status_code=200)))

    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=[policy])
    pipeline.run(request_type("GET", "https://localhost"))

    policy.on_request.assert_called_once_with(policy.request)
    policy.on_response.assert_called_once_with(policy.request, policy.response)

    # the policy should call on_exception when next.send() raises
    class TestException(Exception):
        pass

    transport = Mock(send=Mock(side_effect=TestException))
    add_supported_format_rest_to_mock(transport)
    policy = TestPolicy(credential, "scope")
    pipeline = Pipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        pipeline.run(request_type("GET", "https://localhost"))
    policy.on_exception.assert_called_once_with(policy.request)


@pytest.mark.skipif(azure.core.__version__ >= "2", reason="this test applies only to azure-core 1.x")
def test_key_vault_regression():
    """Test for regression affecting azure-keyvault-* 4.0.0. This test must pass, unmodified, for all 1.x versions."""

    from azure.core.pipeline.policies._authentication import _BearerTokenCredentialPolicyBase

    credential = Mock()
    policy = _BearerTokenCredentialPolicyBase(credential)
    assert policy._credential is credential

    headers = {}
    token = "alphanums"
    policy._update_headers(headers, token)
    assert headers["Authorization"] == "Bearer " + token

    assert policy._need_new_token
    policy._token = AccessToken(token, time.time() + 3600)
    assert not policy._need_new_token
    assert policy._token.token == token


@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_azure_key_credential_policy(request_type, add_supported_format_rest_to_mock):
    """Tests to see if we can create an AzureKeyCredentialPolicy"""

    key_header = "api_key"
    api_key = "test_key"

    def verify_authorization_header(request):
        assert request.headers[key_header] == api_key
        return Mock()

    transport = Mock(send=verify_authorization_header)
    add_supported_format_rest_to_mock(transport)
    credential = AzureKeyCredential(api_key)
    credential_policy = AzureKeyCredentialPolicy(credential=credential, name=key_header)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(request_type("GET", "https://test_key_credential"))


def test_azure_key_credential_policy_raises():
    """Tests AzureKeyCredential and AzureKeyCredentialPolicy raises with non-string input parameters."""
    api_key = 1234
    key_header = 5678
    with pytest.raises(TypeError):
        credential = AzureKeyCredential(api_key)

    credential = AzureKeyCredential(str(api_key))
    with pytest.raises(TypeError):
        credential_policy = AzureKeyCredentialPolicy(credential=credential, name=key_header)


def test_azure_key_credential_updates():
    """Tests AzureKeyCredential updates"""
    api_key = "original"

    credential = AzureKeyCredential(api_key)
    assert credential.key == api_key

    api_key = "new"
    credential.update(api_key)
    assert credential.key == api_key

@pytest.mark.parametrize("sas,url,expected_url", [
    ("sig=test_signature", "https://test_sas_credential", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential", "https://test_sas_credential?sig=test_signature"),
    ("sig=test_signature", "https://test_sas_credential?sig=test_signature", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?sig=test_signature", "https://test_sas_credential?sig=test_signature"),
    ("sig=test_signature", "https://test_sas_credential?", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?", "https://test_sas_credential?sig=test_signature"),
    ("sig=test_signature", "https://test_sas_credential?foo=bar", "https://test_sas_credential?foo=bar&sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?foo=bar", "https://test_sas_credential?foo=bar&sig=test_signature"),
])
def test_azure_sas_credential_policy_pipeline_transport(sas, url, expected_url, add_supported_format_rest_to_mock):
    """Tests to see if we can create an AzureSasCredentialPolicy"""

    def verify_authorization(request):
        assert request.url == expected_url
        return Mock()  # since we have to call ._convert() if the inputted request was a a pipeline transport

    transport=Mock(send=verify_authorization)
    add_supported_format_rest_to_mock(transport)
    credential = AzureSasCredential(sas)
    credential_policy = AzureSasCredentialPolicy(credential=credential)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(PipelineTransportHttpRequest("GET", url))

@pytest.mark.parametrize("sas,url,expected_url", [
    ("sig=test_signature", "https://test_sas_credential", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential", "https://test_sas_credential?sig=test_signature"),
    ("sig=test_signature", "https://test_sas_credential?sig=test_signature", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?sig=test_signature", "https://test_sas_credential?sig=test_signature"),
    ("sig=test_signature", "https://test_sas_credential?", "https://test_sas_credential?sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?", "https://test_sas_credential?sig=test_signature"),
    ("sig=test_signature", "https://test_sas_credential?foo=bar", "https://test_sas_credential?foo=bar&sig=test_signature"),
    ("?sig=test_signature", "https://test_sas_credential?foo=bar", "https://test_sas_credential?foo=bar&sig=test_signature"),
])
def test_azure_sas_credential_policy_rest(sas, url, expected_url, add_supported_format_rest_to_mock):
    """Tests to see if we can create an AzureSasCredentialPolicy"""

    def verify_authorization(request):
        assert request.url == expected_url
        return Mock()

    transport=Mock(send=verify_authorization)
    credential = AzureSasCredential(sas)
    credential_policy = AzureSasCredentialPolicy(credential=credential)
    add_supported_format_rest_to_mock(transport)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(RestHttpRequest("GET", url))

def test_azure_sas_credential_updates():
    """Tests AzureSasCredential updates"""
    sas = "original"

    credential = AzureSasCredential(sas)
    assert credential.signature == sas

    sas = "new"
    credential.update(sas)
    assert credential.signature == sas

def test_azure_sas_credential_policy_raises():
    """Tests AzureSasCredential and AzureSasCredentialPolicy raises with non-string input parameters."""
    sas = 1234
    with pytest.raises(TypeError):
        credential = AzureSasCredential(sas)

def test_azure_named_key_credential():
    cred = AzureNamedKeyCredential("sample_name", "samplekey")

    assert cred.named_key.name == "sample_name"
    assert cred.named_key.key == "samplekey"
    assert isinstance(cred.named_key, tuple)

    cred.update("newname", "newkey")
    assert cred.named_key.name == "newname"
    assert cred.named_key.key == "newkey"
    assert isinstance(cred.named_key, tuple)

def test_azure_named_key_credential_raises():
    with pytest.raises(TypeError, match="Both name and key must be strings."):
        cred = AzureNamedKeyCredential("sample_name", 123345)

    cred = AzureNamedKeyCredential("sample_name", "samplekey")
    assert cred.named_key.name == "sample_name"
    assert cred.named_key.key == "samplekey"

    with pytest.raises(TypeError, match="Both name and key must be strings."):
        cred.update(1234, "newkey")
