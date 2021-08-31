# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import _test_constants

from azure.communication.callingserver.aio import CallingServerClient as CallingServerClientAsync
from azure.communication.callingserver import CallingServerClient

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

def create_mock_call_connection(status_code, payload, is_async=False):
    calling_server_client = create_mock_calling_server_client(status_code, payload, is_async)
    return calling_server_client.get_call_connection(_test_constants.CALL_ID)

def create_mock_calling_server_client(status_code, payload, is_async=False):
    async def async_mock_send(*_, **__):
        return _mock_response(status_code=status_code, json_payload=payload)

    def mock_send(*_, **__):
        return _mock_response(status_code=status_code, json_payload=payload)

    if is_async:
        return create_calling_server_client_async(async_mock_send)
    return create_calling_server_client(mock_send)

def create_calling_server_client_async(mock_transport=None):
    if mock_transport is None:
        return CallingServerClientAsync.from_connection_string(_test_constants.CONNECTION_STRING)
    return CallingServerClientAsync.from_connection_string(_test_constants.CONNECTION_STRING,
        transport=Mock(send=mock_transport))

def create_calling_server_client(mock_transport=None):
    if mock_transport is None:
        return CallingServerClient.from_connection_string(_test_constants.CONNECTION_STRING)
    return CallingServerClient.from_connection_string(_test_constants.CONNECTION_STRING,
        transport=Mock(send=mock_transport))

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
