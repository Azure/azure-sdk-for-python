# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob._encryption import (
    _ENCRYPTION_PROTOCOL_V1,
    _ENCRYPTION_PROTOCOL_V2,
    decrypt_queue_message,
    encrypt_queue_message,
)


class _IdentityKeyWrapper(object):
    def __init__(self, kid="local:key1"):
        self.kid = kid

    def wrap_key(self, key):
        return key

    def unwrap_key(self, key, algorithm):
        return key

    def get_key_wrap_algorithm(self):
        return "test-algorithm"

    def get_kid(self):
        return self.kid


class _HttpResponse(object):
    def __init__(self):
        self.reason = "Bad Request"
        self.status_code = 400


class _PipelineResponse(object):
    def __init__(self, http_response):
        self.http_response = http_response


def test_decrypt_queue_message_when_decryption_fails_uses_inner_http_response():
    key = _IdentityKeyWrapper("key1")
    wrong_key = _IdentityKeyWrapper("key2")
    message = encrypt_queue_message("hello world", key, _ENCRYPTION_PROTOCOL_V1)
    http_response = _HttpResponse()
    response = _PipelineResponse(http_response)

    with pytest.raises(HttpResponseError) as error:
        decrypt_queue_message(message, response, False, wrong_key, None)

    assert error.value.response is http_response
    assert "Decryption failed." in str(error.value)


def test_decrypt_queue_message_when_message_is_not_json_returns_original_message():
    message = "not-json"
    response = _PipelineResponse(_HttpResponse())

    result = decrypt_queue_message(message, response, False, None, None)

    assert result == "not-json"


def test_decrypt_queue_message_when_required_and_loaded_json_missing_metadata_raises_value_error():
    response = _PipelineResponse(_HttpResponse())

    with pytest.raises(ValueError) as error:
        decrypt_queue_message("{}", response, True, None, None)

    assert str(error.value) == (
        "Encryption required, but received message does not contain appropriate metatadata. "
        "Message was either not encrypted or metadata was incorrect."
    )


def test_decrypt_queue_message_when_encryption_data_is_malformed_returns_original_message():
    message = json.dumps({
        "EncryptedMessageContents": "",
        "EncryptionData": {"EncryptionAgent": {}},
    })
    response = _PipelineResponse(_HttpResponse())

    result = decrypt_queue_message(message, response, False, None, None)

    assert result == message


def test_decrypt_queue_message_when_message_is_valid_v2_returns_plaintext():
    key = _IdentityKeyWrapper("key1")
    message = encrypt_queue_message("hello queue", key, _ENCRYPTION_PROTOCOL_V2)
    response = _PipelineResponse(_HttpResponse())

    result = decrypt_queue_message(message, response, False, key, None)

    assert result == "hello queue"
