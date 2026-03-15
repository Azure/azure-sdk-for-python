# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from json import loads

import pytest

from azure.storage.blob._encryption import (
    _ENCRYPTION_PROTOCOL_V1,
    _ENCRYPTION_PROTOCOL_V2,
    _GCM_REGION_DATA_LENGTH,
    decrypt_queue_message,
    encrypt_queue_message,
)
from encryption_test_helper import KeyWrapper


class _FakePipelineResponse(object):
    def __init__(self):
        self.http_response = None


def test_encrypt_queue_message_when_message_contains_unicode_returns_decrypted_message():
    message = "Hello āzure queue 世界"
    key_encryption_key = KeyWrapper("key1")

    encrypted_message = encrypt_queue_message(message, key_encryption_key, _ENCRYPTION_PROTOCOL_V1)
    decrypted_message = decrypt_queue_message(
        encrypted_message,
        _FakePipelineResponse(),
        True,
        key_encryption_key,
        None,
    )

    assert decrypted_message == message


def test_encrypt_queue_message_when_version_is_v2_returns_gcm_metadata():
    key_encryption_key = KeyWrapper("key1")

    encrypted_message = loads(encrypt_queue_message("hello queue", key_encryption_key, _ENCRYPTION_PROTOCOL_V2))
    encryption_data = encrypted_message["EncryptionData"]

    assert encryption_data["EncryptionAgent"]["Protocol"] == _ENCRYPTION_PROTOCOL_V2
    assert encryption_data["EncryptionAgent"]["EncryptionAlgorithm"] == "AES_GCM_256"
    assert encryption_data["EncryptedRegionInfo"]["DataLength"] == _GCM_REGION_DATA_LENGTH
    assert "ContentEncryptionIV" not in encryption_data


def test_encrypt_queue_message_when_version_is_invalid_raises_value_error():
    key_encryption_key = KeyWrapper("key1")

    with pytest.raises(ValueError) as error:
        encrypt_queue_message("hello queue", key_encryption_key, "2.1")

    assert str(error.value) == "Invalid encryption version specified."


def test_encrypt_queue_message_when_version_is_v1_builds_queue_message_payload():
    key_encryption_key = KeyWrapper("key1")

    encrypted_message = loads(encrypt_queue_message("hello queue", key_encryption_key, _ENCRYPTION_PROTOCOL_V1))
    encryption_data = encrypted_message["EncryptionData"]

    assert sorted(encrypted_message.keys()) == ["EncryptedMessageContents", "EncryptionData"]
    assert encryption_data["WrappedContentKey"]["KeyId"] == "key1"
    assert encryption_data["WrappedContentKey"]["Algorithm"] == "A256KW"
    assert encryption_data["EncryptionAgent"]["Protocol"] == _ENCRYPTION_PROTOCOL_V1
    assert encryption_data["EncryptionAgent"]["EncryptionAlgorithm"] == "AES_CBC_256"
    assert "ContentEncryptionIV" in encryption_data


def test_encrypt_queue_message_when_encryption_succeeds_returns_serialized_json_string():
    message = "return path message"
    key_encryption_key = KeyWrapper("key1")

    encrypted_message = encrypt_queue_message(message, key_encryption_key, _ENCRYPTION_PROTOCOL_V2)
    decrypted_message = decrypt_queue_message(
        encrypted_message,
        _FakePipelineResponse(),
        True,
        key_encryption_key,
        None,
    )

    assert encrypted_message.startswith('{"EncryptedMessageContents": "')
    assert '"EncryptionData": {' in encrypted_message
    assert decrypted_message == message
