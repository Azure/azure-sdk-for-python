# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time

import azure.core
from azure.core.credentials import AccessToken, AzureKeyCredential, AzureSasCredential
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, SansIOHTTPPolicy, AzureKeyCredentialPolicy, AzureSasCredentialPolicy
from azure.core.pipeline.transport import HttpRequest

import pytest

try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock


def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    # 2524608000 == 01/01/2050 @ 12:00am (UTC)
    expected_token = AccessToken("expected_token", 2524608000)

    def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)

    fake_credential = Mock(get_token=Mock(return_value=expected_token))
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]

    pipeline = Pipeline(transport=Mock(), policies=policies)
    pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    assert fake_credential.get_token.call_count == 1

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    # Didn't need a new token
    assert fake_credential.get_token.call_count == 1

def test_bearer_policy_send():
    """The bearer token policy should invoke the next policy's send method and return the result"""
    expected_request = HttpRequest("GET", "https://spam.eggs")
    expected_response = Mock()

    def verify_request(request):
        assert request.http_request is expected_request
        return expected_response

    fake_credential = Mock(get_token=lambda _: AccessToken("", 0))
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_request)]
    response = Pipeline(transport=Mock(), policies=policies).run(expected_request)

    assert response is expected_response


def test_bearer_policy_token_caching():
    good_for_one_hour = AccessToken("token", time.time() + 3600)
    credential = Mock(get_token=Mock(return_value=good_for_one_hour))
    pipeline = Pipeline(transport=Mock(), policies=[BearerTokenCredentialPolicy(credential, "scope")])

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 1  # policy has no token at first request -> it should call get_token

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 1  # token is good for an hour -> policy should return it from cache

    expired_token = AccessToken("token", time.time())
    credential.get_token.reset_mock()
    credential.get_token.return_value = expired_token
    pipeline = Pipeline(transport=Mock(), policies=[BearerTokenCredentialPolicy(credential, "scope")])

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 1

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))
    assert credential.get_token.call_count == 2  # token expired -> policy should call get_token


def test_bearer_policy_optionally_enforces_https():
    """HTTPS enforcement should be controlled by a keyword argument, and enabled by default"""

    def assert_option_popped(request, **kwargs):
        assert "enforce_https" not in kwargs, "BearerTokenCredentialPolicy didn't pop the 'enforce_https' option"

    credential = Mock(get_token=lambda *_, **__: AccessToken("***", 42))
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


def test_preserves_enforce_https_opt_out():
    """The policy should use request context to preserve an opt out from https enforcement"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert "enforce_https" in request.context, "'enforce_https' is not in the request's context"

    policies = [BearerTokenCredentialPolicy(credential=Mock(), scope="scope"), ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)


def test_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    policies = [BearerTokenCredentialPolicy(credential=Mock(), scope="scope"), ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "https://secure"))


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

def test_azure_key_credential_policy():
    """Tests to see if we can create an AzureKeyCredentialPolicy"""

    key_header = "api_key"
    api_key = "test_key"

    def verify_authorization_header(request):
        assert request.headers[key_header] == api_key

    transport=Mock(send=verify_authorization_header)
    credential = AzureKeyCredential(api_key)
    credential_policy = AzureKeyCredentialPolicy(credential=credential, name=key_header)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(HttpRequest("GET", "https://test_key_credential"))

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
def test_azure_sas_credential_policy(sas, url, expected_url):
    """Tests to see if we can create an AzureSasCredentialPolicy"""

    def verify_authorization(request):
        assert request.url == expected_url

    transport=Mock(send=verify_authorization)
    credential = AzureSasCredential(sas)
    credential_policy = AzureSasCredentialPolicy(credential=credential)
    pipeline = Pipeline(transport=transport, policies=[credential_policy])

    pipeline.run(HttpRequest("GET", url))

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
