# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import time
from azure.core.credentials import AccessToken

from azure.identity._internal import create_access_token


def test_create_access_token():
    token = create_access_token("token", 42)
    assert isinstance(token, AccessToken)
    assert token.token == "token"
    assert token.expires_on == 42


def test_create_access_token_refresh_on():
    if not hasattr(AccessToken, "refresh_on"):
        pytest.skip("AccessToken.refresh_on is not available")

    token = create_access_token("token", 42)
    assert isinstance(token, AccessToken)
    assert token.token == "token"
    assert token.expires_on == 42
    assert token.refresh_on is None

    token = create_access_token("token", 42, {"refresh_on": 10})
    assert isinstance(token, AccessToken)
    assert token.token == "token"
    assert token.expires_on == 42
    assert token.refresh_on == 10

    now = int(time.time())
    token = create_access_token("token2", 42, {"refresh_in": 5})
    assert isinstance(token, AccessToken)
    assert token.token == "token2"
    assert token.expires_on == 42
    assert token.refresh_on >= now + 5
