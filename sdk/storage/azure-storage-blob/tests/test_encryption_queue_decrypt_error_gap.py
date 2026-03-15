# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob._encryption import (
    _ENCRYPTION_PROTOCOL_V1,
    decrypt_queue_message,
    encrypt_queue_message,
)

from encryption_test_helper import KeyWrapper


class _FakeHttpResponse(object):
    status_code = 200
    reason = "OK"
    headers = {}


class _FakePipelineResponse(object):
    def __init__(self):
        self.http_response = _FakeHttpResponse()


def test_decrypt_queue_message_when_key_id_does_not_match_raises_http_response_error():
    key_encryption_key = KeyWrapper("key1")
    wrong_key_encryption_key = KeyWrapper("key2")
    encrypted_message = encrypt_queue_message("hello world", key_encryption_key, _ENCRYPTION_PROTOCOL_V1)

    with pytest.raises(HttpResponseError) as error:
        decrypt_queue_message(
            encrypted_message,
            _FakePipelineResponse(),
            False,
            wrong_key_encryption_key,
            None,
        )

    assert error.value.message == "Decryption failed."
    assert str(error.value.__cause__) == "Provided or resolved key-encryption-key does not match the id of key used to encrypt."
