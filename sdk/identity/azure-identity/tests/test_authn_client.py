# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import time

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

from azure.core.credentials import AccessToken
from azure.identity._authn_client import AuthnClient


def test_authn_client_deserialization():
    # using the synchronous AuthnClient to drive this test but the functionality tested is
    # in the sans I/O AuthnClientBase, shared with AsyncAuthnClient
    now = 6
    expires_in = 59 - now
    expires_on = now + expires_in
    access_token = "***"
    expected_access_token = AccessToken(access_token, expires_on)
    scope = "scope"

    mock_response = Mock(
        headers={"content-type": "application/json"}, status_code=200, content_type=["application/json"]
    )
    mock_send = Mock(return_value=mock_response)

    # response with expires_on only
    mock_response.text = lambda: json.dumps(
        {"access_token": access_token, "expires_on": expires_on, "token_type": "Bearer", "resource": scope}
    )
    token = AuthnClient("http://foo", transport=Mock(send=mock_send)).request_token(scope)
    assert token == expected_access_token

    # response with expires_on only and it's a datetime string (App Service MSI)
    mock_response.text = lambda: json.dumps(
        {
            "access_token": access_token,
            "expires_on": "01/01/1970 00:00:{} +00:00".format(now + expires_in),
            "token_type": "Bearer",
            "resource": scope,
        }
    )
    token = AuthnClient("http://foo", transport=Mock(send=mock_send)).request_token(scope)
    assert token == expected_access_token

    # response with string expires_in and expires_on (IMDS, Cloud Shell)
    mock_response.text = lambda: json.dumps(
        {
            "access_token": access_token,
            "expires_in": str(expires_in),
            "expires_on": str(expires_on),
            "token_type": "Bearer",
            "resource": scope,
        }
    )
    token = AuthnClient("http://foo", transport=Mock(send=mock_send)).request_token(scope)
    assert token == expected_access_token

    # response with int expires_in (AAD)
    mock_response.text = lambda: json.dumps(
        {"access_token": access_token, "expires_in": expires_in, "token_type": "Bearer", "ext_expires_in": expires_in}
    )
    with patch("azure.identity._authn_client.time.time") as mock_time:
        mock_time.return_value = now
        token = AuthnClient("http://foo", transport=Mock(send=mock_send)).request_token(scope)
        assert token == expected_access_token


def test_caching_when_only_expires_in_set():
    """the cache should function when auth responses don't include an explicit expires_on"""

    access_token = "token"
    now = 42
    expires_in = 1800
    expires_on = now + expires_in
    expected_token = AccessToken(access_token, expires_on)

    mock_response = Mock(
        text=lambda: json.dumps({"access_token": access_token, "expires_in": expires_in, "token_type": "Bearer"}),
        headers={"content-type": "application/json"},
        status_code=200,
        content_type=["application/json"],
    )
    mock_send = Mock(return_value=mock_response)

    client = AuthnClient("http://foo", transport=Mock(send=mock_send))
    with patch("azure.identity._authn_client.time.time") as mock_time:
        mock_time.return_value = 42
        token = client.request_token(["scope"])
        assert token.token == expected_token.token
        assert token.expires_on == expected_token.expires_on

        cached_token = client.get_cached_token(["scope"])
        assert cached_token == expected_token


def test_expires_in_strings():
    expected_token = "token"

    mock_response = Mock(
        headers={"content-type": "application/json"}, status_code=200, content_type=["application/json"]
    )
    mock_send = Mock(return_value=mock_response)

    mock_response.text = lambda: json.dumps(
        {"access_token": expected_token, "expires_in": "42", "ext_expires_in": "42", "token_type": "Bearer"}
    )

    now = int(time.time())
    with patch("azure.identity._authn_client.time.time") as mock_time:
        mock_time.return_value = now
        token = AuthnClient("http://foo", transport=Mock(send=mock_send)).request_token("scope")
    assert token.token == expected_token
    assert token.expires_on == now + 42
