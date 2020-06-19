# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from azure.identity._internal.aad_client import AadClient
from azure.core.credentials import AccessToken
import pytest

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock


def test_if_refresh():
    client = AadClient("test", "test")
    now = int(time.time())

    # do not need refresh
    token = AccessToken("token", now + 500)
    is_refresh = client.is_refresh(token)
    assert not is_refresh

    # need refresh
    token = AccessToken("token", now + 100)
    client._last_refresh_time = now - 500
    is_refresh = client.is_refresh(token)
    assert is_refresh

    # not exceed cool down time, do not refresh
    token = AccessToken("token", now + 100)
    client._last_refresh_time = now - 5
    is_refresh = client.is_refresh(token)
    assert not is_refresh
