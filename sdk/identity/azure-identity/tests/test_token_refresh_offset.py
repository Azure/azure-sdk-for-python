# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from azure.identity._internal.aad_client import AadClient
from azure.identity._authn_client import AuthnClient
from azure.core.credentials import AccessToken
import pytest
from helpers import mock_response

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock



def test_aad_client_if_refresh():
    client = AadClient("test", "test")
    now = int(time.time())

    # do not need refresh
    token = AccessToken("token", now + 500)
    should_refresh = client.should_refresh(token)
    assert not should_refresh

    # need refresh
    token = AccessToken("token", now + 100)
    client._last_refresh_time = now - 500
    should_refresh = client.should_refresh(token)
    assert should_refresh

    # not exceed cool down time, do not refresh
    token = AccessToken("token", now + 100)
    client._last_refresh_time = now - 5
    should_refresh = client.should_refresh(token)
    assert not should_refresh

def test_auth_client_if_refresh():
    client = AuthnClient(endpoint="http://foo")
    now = int(time.time())

    # do not need refresh
    token = AccessToken("token", now + 500)
    should_refresh = client.should_refresh(token)
    assert not should_refresh

    # need refresh
    token = AccessToken("token", now + 100)
    client._last_refresh_time = now - 500
    should_refresh = client.should_refresh(token)
    assert should_refresh

    # not exceed cool down time, do not refresh
    token = AccessToken("token", now + 100)
    client._last_refresh_time = now - 5
    should_refresh = client.should_refresh(token)
    assert not should_refresh