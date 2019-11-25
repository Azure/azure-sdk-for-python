# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time

from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpRequest

try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock


def test_bearer_policy_adds_header():
    """The bearer token policy should add a header containing a token from its credential"""
    expected_token = AccessToken("expected_token", 0)

    def verify_authorization_header(request):
        assert request.http_request.headers["Authorization"] == "Bearer {}".format(expected_token.token)

    fake_credential = Mock(get_token=Mock(return_value=expected_token))
    policies = [BearerTokenCredentialPolicy(fake_credential, "scope"), Mock(send=verify_authorization_header)]

    Pipeline(transport=Mock(), policies=policies).run(HttpRequest("GET", "https://spam.eggs"))

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
