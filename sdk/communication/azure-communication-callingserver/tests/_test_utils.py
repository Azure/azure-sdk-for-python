# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import unittest

import _test_constants
from azure.core.credentials import AccessToken
from azure.communication.callingserver.aio import CallingServerClient as CallingServerClientAsync
from azure.communication.callingserver import CallingServerClient

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken(_test_constants.FAKE_TOKEN, 0)
    def get_token(self, *args):
        return self.token

class FakeTokenCredential_Async(object):
    def __init__(self):
        self.token = AccessToken(_test_constants.FAKE_TOKEN, 0)
    async def get_token(self, *args):
        return self.token

def create_mock_call_connection(call_connection_id, status_code, payload, is_async=False, use_managed_identity=False):
    calling_server_client = create_mock_calling_server_client(status_code, payload, is_async, use_managed_identity)
    return calling_server_client.get_call_connection(call_connection_id)

def create_mock_calling_server_client(status_code, payload, is_async=False, use_managed_identity=False):
    async def async_mock_send(*_, **__):
        return _mock_response(status_code=status_code, json_payload=payload)

    def mock_send(*_, **__):
        return _mock_response(status_code=status_code, json_payload=payload)

    if is_async:
        return create_calling_server_client_async(async_mock_send, use_managed_identity)
    return create_calling_server_client(mock_send, use_managed_identity)

def create_calling_server_client_async(mock_transport=None, use_managed_identity=False):
    if mock_transport is None:
        return (
            CallingServerClientAsync.from_connection_string(_test_constants.CONNECTION_STRING)
            if use_managed_identity
            else CallingServerClientAsync(_test_constants.FAKE_ENDPOINT, FakeTokenCredential_Async())
            )

    return (
            CallingServerClientAsync.from_connection_string(_test_constants.CONNECTION_STRING, transport=Mock(send=mock_transport))
            if use_managed_identity
            else CallingServerClientAsync(_test_constants.FAKE_ENDPOINT, FakeTokenCredential_Async(), transport=Mock(send=mock_transport))
            )

def create_calling_server_client(mock_transport=None, use_managed_identity=False):
    if mock_transport is None:
        return (
            CallingServerClient.from_connection_string(_test_constants.CONNECTION_STRING)
            if use_managed_identity
            else CallingServerClient(_test_constants.FAKE_ENDPOINT, FakeTokenCredential())
            )
    return (
            CallingServerClient.from_connection_string(_test_constants.CONNECTION_STRING, transport=Mock(send=mock_transport))
            if use_managed_identity
            else CallingServerClient(_test_constants.FAKE_ENDPOINT, FakeTokenCredential(), transport=Mock(send=mock_transport))
            )

def _mock_response(status_code=200, headers=None, json_payload=None):
    response = Mock(status_code=status_code, headers=headers or {})
    if json_payload is not None:
        response.text = lambda encoding=None: json.dumps(json_payload)
        response.headers["content-type"] = "application/json"
        response.content_type = "application/json"
    else:
        response.text = lambda encoding=None: ""
        response.headers["content-type"] = "text/plain"
        response.content_type = "text/plain"
    return response