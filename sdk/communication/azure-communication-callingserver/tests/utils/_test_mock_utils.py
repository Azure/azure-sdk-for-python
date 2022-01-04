# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from . import _test_constants
from azure.core.credentials import AccessToken
from azure.communication.callingserver import CallingServerClient, CallingOperationStatus

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken(_test_constants.FAKE_TOKEN, 0)
    def get_token(self, *args):
        return self.token

def create_mock_call_connection(call_connection_id, status_code, payload, use_managed_identity=False):
    calling_server_client = create_mock_calling_server_client(status_code, payload, use_managed_identity)
    return calling_server_client.get_call_connection(call_connection_id)

def create_mock_calling_server_client(status_code, payload, use_managed_identity=False):
    def mock_send(*_, **__):
        return _mock_response(status_code=status_code, json_payload=payload)

    return create_calling_server_client(mock_send, use_managed_identity)

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


def mock_delete_audio_group(audio_group_id):
     response = Mock(status_code= 202)
     return response