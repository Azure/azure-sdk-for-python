# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from json import dumps, loads

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob._encryption import (
    _ENCRYPTION_PROTOCOL_V1,
    _generate_AES_CBC_cipher,
    _generate_encryption_data_dict,
    decrypt_queue_message,
    encrypt_queue_message,
)
from azure.storage.blob._shared import encode_base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap, aes_key_wrap
from cryptography.hazmat.primitives.padding import PKCS7


class KeyWrapper(object):
    def __init__(self, kid='local:key1'):
        self.kek = os.urandom(32)
        self.backend = default_backend()
        self.kid = kid

    def wrap_key(self, key, algorithm='A256KW'):
        if algorithm == 'A256KW':
            return aes_key_wrap(self.kek, key, self.backend)
        raise ValueError("Unknown key wrap algorithm.")

    def unwrap_key(self, key, algorithm):
        if algorithm == 'A256KW':
            return aes_key_unwrap(self.kek, key, self.backend)
        raise ValueError("Unknown key wrap algorithm.")

    def get_key_wrap_algorithm(self):
        return 'A256KW'

    def get_kid(self):
        return self.kid


class DummyHttpResponse(object):
    def __init__(self):
        self.status_code = 500
        self.reason = "Internal Server Error"
        self.headers = {}
        self.request = None


class DummyPipelineResponse(object):
    def __init__(self):
        self.http_response = DummyHttpResponse()


def _build_encrypted_queue_message_from_bytes(message_as_bytes, key_encryption_key):
    content_encryption_key = os.urandom(32)
    initialization_vector = os.urandom(16)

    cipher = _generate_AES_CBC_cipher(content_encryption_key, initialization_vector)
    padder = PKCS7(128).padder()
    padded_data = padder.update(message_as_bytes) + padder.finalize()

    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    queue_message = {
        "EncryptedMessageContents": encode_base64(encrypted_data),
        "EncryptionData": _generate_encryption_data_dict(
            key_encryption_key, content_encryption_key, initialization_vector, _ENCRYPTION_PROTOCOL_V1
        ),
    }
    return dumps(queue_message)


def test_decrypt_queue_message_when_encrypted_contents_key_is_missing_returns_original_message():
    key_encryption_key = KeyWrapper('key1')
    response = DummyPipelineResponse()
    original_message = encrypt_queue_message("hello world", key_encryption_key, _ENCRYPTION_PROTOCOL_V1)
    message_dict = loads(original_message)
    del message_dict["EncryptedMessageContents"]
    message = dumps(message_dict)

    decrypted = decrypt_queue_message(message, response, False, key_encryption_key, None)

    assert decrypted == message


def test_decrypt_queue_message_when_encrypted_contents_key_is_missing_and_required_raises_value_error():
    key_encryption_key = KeyWrapper('key1')
    response = DummyPipelineResponse()
    original_message = encrypt_queue_message("hello world", key_encryption_key, _ENCRYPTION_PROTOCOL_V1)
    message_dict = loads(original_message)
    del message_dict["EncryptedMessageContents"]
    message = dumps(message_dict)

    with pytest.raises(ValueError) as error:
        decrypt_queue_message(message, response, True, key_encryption_key, None)

    assert str(error.value) == (
        "Encryption required, but received message does not contain appropriate metatadata. "
        "Message was either not encrypted or metadata was incorrect."
    )


def test_decrypt_queue_message_when_v1_message_uses_resolver_returns_plaintext():
    key_encryption_key = KeyWrapper('key1')
    response = DummyPipelineResponse()
    message = encrypt_queue_message("resolved plaintext", key_encryption_key, _ENCRYPTION_PROTOCOL_V1)

    decrypted = decrypt_queue_message(
        message,
        response,
        False,
        None,
        lambda key_id: key_encryption_key if key_id == key_encryption_key.get_kid() else None,
    )

    assert decrypted == "resolved plaintext"


def test_decrypt_queue_message_when_v1_message_contains_unicode_returns_plaintext():
    key_encryption_key = KeyWrapper('key1')
    response = DummyPipelineResponse()
    message = encrypt_queue_message("héllo queue 😀", key_encryption_key, _ENCRYPTION_PROTOCOL_V1)

    decrypted = decrypt_queue_message(message, response, False, key_encryption_key, None)

    assert decrypted == "héllo queue 😀"


def test_decrypt_queue_message_when_plaintext_is_invalid_utf8_raises_http_response_error():
    key_encryption_key = KeyWrapper('key1')
    response = DummyPipelineResponse()
    message = _build_encrypted_queue_message_from_bytes(b"\xff\xfe\xfd", key_encryption_key)

    with pytest.raises(HttpResponseError) as error:
        decrypt_queue_message(message, response, False, key_encryption_key, None)

    assert error.value.response is response.http_response
    assert error.value.message == "Decryption failed."
    assert isinstance(error.value.__cause__, UnicodeDecodeError)
