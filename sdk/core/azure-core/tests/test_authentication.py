# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import base64
import itertools
import time

import azure.core
from azure.core.credentials import AccessToken, AzureKeyCredential, AzureSasCredential
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    BearerTokenCredentialPolicy,
    SansIOHTTPPolicy,
    AzureKeyCredentialPolicy,
    AzureSasCredentialPolicy,
)
from azure.core.pipeline.policies._authentication import _parse_challenges
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
        return Mock()

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
        return Mock()

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
            return Mock()

    credential = Mock(get_token=Mock(return_value=AccessToken("***", 42)))
    policies = [BearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "http://not.secure"), enforce_https=False)


def test_context_unmodified_by_default():
    """When no options for the policy accompany a request, the policy shouldn't add anything to the request context"""

    class ContextValidator(SansIOHTTPPolicy):
        def on_request(self, request):
            assert not any(request.context), "the policy shouldn't add to the request's context"

    credential = Mock(get_token=Mock(return_value=AccessToken("***", 42)))
    policies = [BearerTokenCredentialPolicy(credential, "scope"), ContextValidator()]
    pipeline = Pipeline(transport=Mock(), policies=policies)

    pipeline.run(HttpRequest("GET", "https://secure"))


def test_challenge_parsing():
    challenges = (
        (  # CAE - insufficient claims
            'Bearer realm="", authorization_uri="https://login.microsoftonline.com/common/oauth2/authorize", client_id="00000003-0000-0000-c000-000000000000", error="insufficient_claims", claims="eyJhY2Nlc3NfdG9rZW4iOiB7ImZvbyI6ICJiYXIifX0="',
            {
                "authorization_uri": "https://login.microsoftonline.com/common/oauth2/authorize",
                "client_id": "00000003-0000-0000-c000-000000000000",
                "error": "insufficient_claims",
                "claims": "eyJhY2Nlc3NfdG9rZW4iOiB7ImZvbyI6ICJiYXIifX0=",
                "realm": "",
            },
        ),
        (  # CAE - sessions revoked
            'Bearer authorization_uri="https://login.windows-ppe.net/", error="invalid_token", error_description="User session has been revoked", claims="eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwgInZhbHVlIjoiMTYwMzc0MjgwMCJ9fX0="',
            {
                "authorization_uri": "https://login.windows-ppe.net/",
                "error": "invalid_token",
                "error_description": "User session has been revoked",
                "claims": "eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwgInZhbHVlIjoiMTYwMzc0MjgwMCJ9fX0=",
            },
        ),
        (  # CAE - IP policy
            'Bearer authorization_uri="https://login.windows.net/", error="invalid_token", error_description="Tenant IP Policy validate failed.", claims="eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOiIxNjEwNTYzMDA2In0sInhtc19ycF9pcGFkZHIiOnsidmFsdWUiOiIxLjIuMy40In19fQ"',
            {
                "authorization_uri": "https://login.windows.net/",
                "error": "invalid_token",
                "error_description": "Tenant IP Policy validate failed.",
                "claims": "eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOiIxNjEwNTYzMDA2In0sInhtc19ycF9pcGFkZHIiOnsidmFsdWUiOiIxLjIuMy40In19fQ"
            }
        ),
        (  # Key Vault
            'Bearer authorization="https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47", resource="https://vault.azure.net"',
            {
                "authorization": "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47",
                "resource": "https://vault.azure.net",
            },
        ),
        (  # ARM
            'Bearer authorization_uri="https://login.windows.net/", error="invalid_token", error_description="The authentication failed because of missing \'Authorization\' header."',
            {
                "authorization_uri": "https://login.windows.net/",
                "error": "invalid_token",
                "error_description": "The authentication failed because of missing 'Authorization' header.",
            },
        ),
    )

    for challenge, expected_parameters in challenges:
        challenge = _parse_challenges(challenge)
        assert len(challenge) == 1
        assert challenge[0].scheme == "Bearer"
        assert challenge[0].parameters == expected_parameters

    for permutation in itertools.permutations(challenge for challenge, _ in challenges):
        parsed_challenges = _parse_challenges(", ".join(permutation))
        assert len(parsed_challenges) == len(challenges)
        expected_parameters = [parameters for _, parameters in challenges]
        for challenge in parsed_challenges:
            assert challenge.scheme == "Bearer"
            expected_parameters.remove(challenge.parameters)
        assert len(expected_parameters) == 0


def test_calls_on_before_request():
    """BearerTokenCredentialPolicy should call on_before_request before sending a request"""

    transport = Mock()

    class TestPolicy(BearerTokenCredentialPolicy):
        called = False

        def on_before_request(self, request):
            assert not transport.send.called
            self.__class__.called = True

    pipeline = Pipeline(policies=[TestPolicy(Mock(), "scope")], transport=transport)
    pipeline.run(HttpRequest("GET", "https://localhost"))

    assert TestPolicy.called
    assert transport.send.call_count == 1


def test_calls_on_challenge():
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

    pipeline = Pipeline(transport=transport, policies=policies)
    pipeline.run(HttpRequest("GET", "https://localhost"))

    assert TestPolicy.called


def test_cannot_complete_challenge():
    """BearerTokenCredentialPolicy should return the 401 response when it can't complete its challenge"""

    expected_scope = "scope"
    expected_token = AccessToken("***", int(time.time()) + 3600)
    credential = Mock(get_token=Mock(return_value=expected_token))
    expected_response = Mock(status_code=401, headers={"WWW-Authenticate": 'Basic realm="localhost"'})
    transport = Mock(send=Mock(return_value=expected_response))
    policies = [BearerTokenCredentialPolicy(credential, expected_scope)]

    pipeline = Pipeline(transport=transport, policies=policies)
    response = pipeline.run(HttpRequest("GET", "https://localhost"))

    assert response.http_response is expected_response
    assert transport.send.call_count == 1
    credential.get_token.assert_called_once_with(expected_scope)


def test_claims_challenge():
    """BearerTokenCredentialPolicy should pass claims from an authentication challenge to its credential"""

    first_token = AccessToken("first", int(time.time()) + 3600)
    second_token = AccessToken("second", int(time.time()) + 3600)
    tokens = (t for t in (first_token, second_token))

    expected_claims = '{"access_token": {"essential": "true"}'
    expected_scope = "scope"

    challenge = 'Bearer claims="{}"'.format(base64.b64encode(expected_claims.encode()).decode())
    responses = (r for r in (Mock(status_code=401, headers={"WWW-Authenticate": challenge}), Mock(status_code=200)))

    def send(request):
        res = next(responses)
        if res.status_code == 401:
            expected_token = first_token.token
        else:
            expected_token = second_token.token
        assert request.headers["Authorization"] == "Bearer " + expected_token

        return res

    def get_token(*scopes, **kwargs):
        assert scopes == (expected_scope,)
        return next(tokens)

    credential = Mock(get_token=Mock(wraps=get_token))
    transport = Mock(send=Mock(wraps=send))
    policies = [BearerTokenCredentialPolicy(credential, expected_scope)]
    pipeline = Pipeline(transport=transport, policies=policies)

    response = pipeline.run(HttpRequest("GET", "https://localhost"))

    assert response.http_response.status_code == 200
    assert transport.send.call_count == 2
    assert credential.get_token.call_count == 2
    credential.get_token.assert_called_with(expected_scope, claims_challenge=expected_claims)
    with pytest.raises(StopIteration):
        next(tokens)
    with pytest.raises(StopIteration):
        next(responses)


def test_calls_prior_base_class_methods():
    """Backcompat requires BearerTokenCredentialPolicy to behave like SansIOHttpPolicy"""

    class TestPolicy(BearerTokenCredentialPolicy):
        def __init__(self, *args, **kwargs):
            super(TestPolicy, self).__init__(*args, **kwargs)
            self.on_exception = Mock(return_value=None)
            self.on_request = Mock()
            self.on_response = Mock()

        def send(self, request):
            self.request = request
            self.response = super(TestPolicy, self).send(request)
            return self.response

    credential = Mock(get_token=Mock(return_value=AccessToken("***", int(time.time()) + 3600)))
    policy = TestPolicy(credential, "scope")
    transport = Mock(send=Mock(return_value=Mock(status_code=200)))

    pipeline = Pipeline(transport=transport, policies=[policy])
    pipeline.run(HttpRequest("GET", "https://localhost"))

    policy.on_request.assert_called_once_with(policy.request)
    policy.on_response.assert_called_once_with(policy.request, policy.response)

    # on_exception should be called when send() raises
    class TestException(Exception):
        pass

    credential = Mock(get_token=Mock(side_effect=TestException))
    policy = TestPolicy(credential, "scope")
    pipeline = Pipeline(transport=transport, policies=[policy])
    with pytest.raises(TestException):
        pipeline.run(HttpRequest("GET", "https://localhost"))
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


def test_azure_key_credential_policy():
    """Tests to see if we can create an AzureKeyCredentialPolicy"""

    key_header = "api_key"
    api_key = "test_key"

    def verify_authorization_header(request):
        assert request.headers[key_header] == api_key

    transport = Mock(send=verify_authorization_header)
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
