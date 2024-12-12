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
import base64
import time

from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline
from azure.mgmt.core.policies._authentication import (
    ARMChallengeAuthenticationPolicy,
    AuxiliaryAuthenticationPolicy,
)

from azure.core.pipeline.transport import HttpRequest
from devtools_testutils.fake_credentials import FakeTokenCredential


import pytest
from unittest.mock import Mock


CLAIM_TOKEN = base64.b64encode(b'{"access_token": {"foo": "bar"}}').decode()
CLAIM_NBF = base64.b64encode(b'{"access_token":{"nbf":{"essential":true, "value":"1603742800"}}}').decode()
ip_claim = b'{"access_token":{"nbf":{"essential":true,"value":"1610563006"},"xms_rp_ipaddr":{"value":"1.2.3.4"}}}'
CLAIM_IP = base64.b64encode(ip_claim).decode()[:-2]  # Trim off padding = characters


def test_auxiliary_authentication_policy():
    """The auxiliary authentication policy should add a header containing a token from its credential"""
    first_token = AccessToken("first", int(time.time()) + 3600)
    second_token = AccessToken("second", int(time.time()) + 3600)

    def verify_authorization_header(request):
        assert request.http_request.headers["x-ms-authorization-auxiliary"] == ", ".join(
            "Bearer {}".format(token.token) for token in [first_token, second_token]
        )
        return Mock()

    fake_credential1 = Mock(spec_set=["get_token"], get_token=Mock(return_value=first_token))
    fake_credential2 = Mock(spec_set=["get_token"], get_token=Mock(return_value=second_token))
    policies = [
        AuxiliaryAuthenticationPolicy([fake_credential1, fake_credential2], "scope"),
        Mock(send=verify_authorization_header),
    ]

    pipeline = Pipeline(transport=Mock(), policies=policies)
    pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    assert fake_credential1.get_token.call_count == 1
    assert fake_credential2.get_token.call_count == 1

    pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    # Didn't need a new token
    assert fake_credential1.get_token.call_count == 1
    assert fake_credential2.get_token.call_count == 1


def test_claims_challenge():
    """ARMChallengeAuthenticationPolicy should pass claims from an authentication challenge to its credential"""

    first_token = AccessToken("first", int(time.time()) + 3600)
    second_token = AccessToken("second", int(time.time()) + 3600)
    tokens = (t for t in (first_token, second_token))

    expected_claims = '{"access_token": {"essential": "true"}'
    expected_scope = "scope"

    challenge = 'Bearer authorization_uri="https://localhost", error="insufficient_claims", error_description=".", claims="{}"'.format(
        base64.b64encode(expected_claims.encode()).decode()
    )
    responses = (
        r
        for r in (
            Mock(status_code=401, headers={"WWW-Authenticate": challenge}),
            Mock(status_code=200),
        )
    )

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

    credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    transport = Mock(send=Mock(wraps=send))
    policies = [ARMChallengeAuthenticationPolicy(credential, expected_scope)]
    pipeline = Pipeline(transport=transport, policies=policies)

    response = pipeline.run(HttpRequest("GET", "https://localhost"))

    assert response.http_response.status_code == 200
    assert transport.send.call_count == 2
    assert credential.get_token.call_count == 2

    args, kwargs = credential.get_token.call_args
    assert expected_scope in args
    assert kwargs["claims"] == expected_claims

    with pytest.raises(StopIteration):
        next(tokens)
    with pytest.raises(StopIteration):
        next(responses)


def test_multiple_claims_challenges():
    """ARMChallengeAuthenticationPolicy handle a response having multiple claims challenges"""

    first_token = AccessToken("first", int(time.time()) + 3600)
    second_token = AccessToken("second", int(time.time()) + 3600)
    tokens = (t for t in (first_token, second_token))

    expected_claims = '{"access_token": {"essential": "true"}'
    expected_scope = "scope"

    claims = base64.b64encode(expected_claims.encode()).decode()

    expected_header = ",".join(
        (
            'Bearer realm="", authorization_uri="https://localhost", client_id="00", error="insufficient_claims", claims="{}"'.format(
                claims
            ),
            'Bearer authorization_uri="https://login.windows-ppe.net/", error="invalid_token", error_description="User session has been revoked", claims="{}"'.format(
                claims
            ),
        )
    )

    responses = (
        r
        for r in (
            Mock(status_code=401, headers={"WWW-Authenticate": expected_header}),
            Mock(status_code=200),
        )
    )

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

    credential = Mock(spec_set=["get_token"], get_token=Mock(wraps=get_token))
    transport = Mock(send=Mock(wraps=send))
    policies = [ARMChallengeAuthenticationPolicy(credential, expected_scope)]
    pipeline = Pipeline(transport=transport, policies=policies)

    response = pipeline.run(HttpRequest("GET", "https://localhost"))

    assert response.http_response.status_code == 200
    assert transport.send.call_count == 2
    assert credential.get_token.call_count == 2

    args, kwargs = credential.get_token.call_args
    assert expected_scope in args
    assert kwargs["claims"] == expected_claims

    with pytest.raises(StopIteration):
        next(tokens)
    with pytest.raises(StopIteration):
        next(responses)
