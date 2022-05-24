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
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.mgmt.core.policies import AsyncARMChallengeAuthenticationPolicy, AsyncAuxiliaryAuthenticationPolicy
from azure.core.pipeline.transport import HttpRequest

import pytest

pytestmark = pytest.mark.asyncio


async def test_claims_challenge():
    """AsyncAsyncARMChallengeAuthenticationPolicy should pass claims from an authentication challenge to its credential"""

    first_token = AccessToken("first", int(time.time()) + 3600)
    second_token = AccessToken("second", int(time.time()) + 3600)
    tokens = (t for t in (first_token, second_token))

    expected_claims = '{"access_token": {"essential": "true"}'
    expected_scope = "scope"

    challenge = 'Bearer authorization_uri="https://localhost", error=".", error_description=".", claims="{}"'.format(
        base64.b64encode(expected_claims.encode()).decode()
    )
    responses = (r for r in (Mock(status_code=401, headers={"WWW-Authenticate": challenge}), Mock(status_code=200)))

    async def send(request):
        res = next(responses)
        if res.status_code == 401:
            expected_token = first_token.token
        else:
            expected_token = second_token.token
        assert request.headers["Authorization"] == "Bearer " + expected_token

        return res

    async def get_token(*scopes, **kwargs):
        assert scopes == (expected_scope,)
        return next(tokens)

    credential = Mock(get_token=Mock(wraps=get_token))
    transport = Mock(send=Mock(wraps=send))
    policies = [AsyncARMChallengeAuthenticationPolicy(credential, expected_scope)]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    response = await pipeline.run(HttpRequest("GET", "https://localhost"))

    assert response.http_response.status_code == 200
    assert transport.send.call_count == 2
    assert credential.get_token.call_count == 2
    credential.get_token.assert_called_with(expected_scope, claims=expected_claims)
    with pytest.raises(StopIteration):
        next(tokens)
    with pytest.raises(StopIteration):
        next(responses)


async def test_multiple_claims_challenges():
    """ARMChallengeAuthenticationPolicy should not attempt to handle a response having multiple claims challenges"""

    expected_header = ",".join(
        (
            'Bearer realm="", authorization_uri="https://login.microsoftonline.com/common/oauth2/authorize", client_id="00000003-0000-0000-c000-000000000000", error="insufficient_claims", claims="eyJhY2Nlc3NfdG9rZW4iOiB7ImZvbyI6ICJiYXIifX0="',
            'Bearer authorization_uri="https://login.windows-ppe.net/", error="invalid_token", error_description="User session has been revoked", claims="eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwgInZhbHVlIjoiMTYwMzc0MjgwMCJ9fX0="',
        )
    )

    async def send(request):
        return Mock(status_code=401, headers={"WWW-Authenticate": expected_header})

    async def get_token(*_, **__):
        return AccessToken("***", 42)

    transport = Mock(send=Mock(wraps=send))
    credential = Mock(get_token=Mock(wraps=get_token))
    policies = [AsyncARMChallengeAuthenticationPolicy(credential, "scope")]
    pipeline = AsyncPipeline(transport=transport, policies=policies)

    response = await pipeline.run(HttpRequest("GET", "https://localhost"))

    assert transport.send.call_count == 1
    assert credential.get_token.call_count == 1

    # the policy should have returned the error response because it was unable to handle the challenge
    assert response.http_response.status_code == 401
    assert response.http_response.headers["WWW-Authenticate"] == expected_header


async def test_auxiliary_authentication_policy():
    """The auxiliary authentication policy should add a header containing a token from its credential"""
    first_token = AccessToken("first", int(time.time()) + 3600)
    second_token = AccessToken("second", int(time.time()) + 3600)

    async def verify_authorization_header(request):
        assert request.http_request.headers["x-ms-authorization-auxiliary"] ==\
               ', '.join("Bearer {}".format(token.token) for token in [first_token, second_token])
        return Mock()

    get_token_calls1 = 0
    get_token_calls2 = 0

    async def get_token1(_):
        nonlocal get_token_calls1
        get_token_calls1 += 1
        return first_token

    async def get_token2(_):
        nonlocal get_token_calls2
        get_token_calls2 += 1
        return second_token

    fake_credential1 = Mock(get_token=get_token1)
    fake_credential2 = Mock(get_token=get_token2)
    policies = [AsyncAuxiliaryAuthenticationPolicy([fake_credential1, fake_credential2], "scope"),
                Mock(send=verify_authorization_header)]

    pipeline = AsyncPipeline(transport=Mock(), policies=policies)
    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    assert get_token_calls1 == 1
    assert get_token_calls2 == 1

    await pipeline.run(HttpRequest("GET", "https://spam.eggs"))

    # Didn't need a new token
    assert get_token_calls1 == 1
    assert get_token_calls2 == 1
