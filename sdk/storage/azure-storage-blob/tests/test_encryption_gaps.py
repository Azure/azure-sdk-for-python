# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import mock
from json import loads

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.padding import PKCS7

from azure.storage.blob._encryption import (
    _ENCRYPTION_PROTOCOL_V1,
    _ENCRYPTION_PROTOCOL_V2,
    _EncryptionAgent,
    _EncryptionAlgorithm,
    _EncryptedRegionInfo,
    _EncryptionData,
    _ERROR_OBJECT_INVALID,
    _GCM_NONCE_LENGTH,
    _GCM_REGION_DATA_LENGTH,
    _GCM_TAG_LENGTH,
    _WrappedContentKey,
    encrypt_blob,
    generate_blob_encryption_data,
    get_adjusted_download_range_and_offset,
    get_adjusted_upload_size,
    modify_user_agent_for_encryption,
)
from azure.storage.blob._encryption import (
    _dict_to_encryption_data,
    _generate_encryption_data_dict,
    _validate_and_unwrap_cek,
)
from azure.storage.blob._encryption import (
    _ENCRYPTION_PROTOCOL_V2_1,
    _generate_AES_CBC_cipher,
    decrypt_blob,
)
from azure.storage.blob._version import VERSION

from devtools_testutils.storage import StorageRecordedTestCase
from encryption_test_helper import KeyWrapper
from encryption_test_helper import mock_urandom
from perfstress_tests.key_wrapper import KeyWrapper as PerfstressKeyWrapper


class TestStorageBlobEncryptionGaps(StorageRecordedTestCase):

    def test_encrypt_blob_when_blob_is_none_raises_value_error(self):
        key_encryption_key = KeyWrapper('key1')

        with pytest.raises(ValueError) as exc:
            encrypt_blob(None, key_encryption_key, _ENCRYPTION_PROTOCOL_V1)

        assert str(exc.value) == 'blob should not be None.'

    def test_generate_blob_encryption_data_when_kek_missing_get_kid_raises_attribute_error(self):
        valid_key = KeyWrapper('key1')

        invalid_key = lambda: None
        invalid_key.wrap_key = valid_key.wrap_key
        invalid_key.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm

        with pytest.raises(AttributeError) as exc:
            generate_blob_encryption_data(invalid_key, _ENCRYPTION_PROTOCOL_V1)

        assert str(exc.value) == _ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid')

    def test_generate_blob_encryption_data_when_kek_missing_get_key_wrap_algorithm_raises_attribute_error(self):
        valid_key = KeyWrapper('key1')

        invalid_key = lambda: None
        invalid_key.wrap_key = valid_key.wrap_key
        invalid_key.get_kid = valid_key.get_kid

        with pytest.raises(AttributeError) as exc:
            generate_blob_encryption_data(invalid_key, _ENCRYPTION_PROTOCOL_V1)

        assert str(exc.value) == _ERROR_OBJECT_INVALID.format('key encryption key', 'get_key_wrap_algorithm')

    def test__EncryptionData_when_algorithm_is_invalid_raises_value_error(self):
        encryption_agent = _EncryptionAgent('NotARealAlgorithm', _ENCRYPTION_PROTOCOL_V1)
        wrapped_content_key = _WrappedContentKey('A256KW', b'encrypted_key', 'kid')

        with pytest.raises(ValueError) as exc:
            _EncryptionData(None, None, encryption_agent, wrapped_content_key, {})

        assert str(exc.value) == 'Invalid encryption algorithm.'

    def test_modify_user_agent_for_encryption_when_user_agent_overwrite_is_true_returns_without_changes(self):
        request_options = {'user_agent': 'custom-agent', 'user_agent_overwrite': True}

        modify_user_agent_for_encryption(
            'azsdk-python-blob/12.30.0b1 Python/3.11.0',
            'blob',
            '2.0',
            request_options,
        )

        assert request_options['user_agent'] == 'custom-agent'
        assert request_options['user_agent_overwrite'] is True
        assert len(request_options) == 2


class TestStorageEncryptionGaps(StorageRecordedTestCase):

    def test_modify_user_agent_for_encryption_when_feature_flag_exists_returns_without_changes(self):
        user_agent = "azstorage-clientsideencryption/2.0 azsdk-python-blob/12.30.0 Python/3.12.0"
        request_options = {}

        modify_user_agent_for_encryption(user_agent, "blob", _ENCRYPTION_PROTOCOL_V2, request_options)

        assert request_options == {}

    def test_get_adjusted_upload_size_when_version_is_v2_returns_size_with_region_overhead(self):
        length = _GCM_REGION_DATA_LENGTH + 1

        adjusted_size = get_adjusted_upload_size(length, _ENCRYPTION_PROTOCOL_V2)

        assert adjusted_size == length + (2 * (_GCM_NONCE_LENGTH + _GCM_TAG_LENGTH))

    def test_get_adjusted_download_range_and_offset_when_v1_with_start_and_length_aligns_range_and_offsets(self):
        encryption_data = _EncryptionData(
            b"0" * 16,
            None,
            _EncryptionAgent(_EncryptionAlgorithm.AES_CBC_256, _ENCRYPTION_PROTOCOL_V1),
            _WrappedContentKey("alg", b"encrypted-key", "key-id"),
            {},
        )

        adjusted_range, adjusted_offsets = get_adjusted_download_range_and_offset(30, 34, 5, encryption_data)

        assert adjusted_range == (0, 47)
        assert adjusted_offsets == (30, 13)

    def test_get_adjusted_download_range_and_offset_when_v2_with_region_info_returns_region_aligned_values(self):
        encryption_data = _EncryptionData(
            None,
            _EncryptedRegionInfo(10, 2, 3),
            _EncryptionAgent(_EncryptionAlgorithm.AES_GCM_256, _ENCRYPTION_PROTOCOL_V2),
            _WrappedContentKey("alg", b"encrypted-key", "key-id"),
            {},
        )

        adjusted_range, adjusted_offsets = get_adjusted_download_range_and_offset(12, 16, None, encryption_data)

        assert adjusted_range == (15, 29)
        assert adjusted_offsets == (2, 7)

    def test_get_adjusted_download_range_and_offset_when_v2_missing_region_info_raises_value_error(self):
        # Tests defensive branch — requires mock.
        encryption_data = mock.Mock()
        encryption_data.encryption_agent.protocol = _ENCRYPTION_PROTOCOL_V2
        encryption_data.encrypted_region_info = None

        with pytest.raises(ValueError) as error:
            get_adjusted_download_range_and_offset(0, 10, None, encryption_data)

        assert str(error.value) == "Missing required metadata for Encryption V2"


class RecordingKeyWrapper(object):
    def __init__(self):
        self.last_wrapped = None

    def wrap_key(self, key):
        self.last_wrapped = key
        return b"wrapped-key-bytes"

    def unwrap_key(self, key, algorithm):
        return key

    def get_kid(self):
        return "local:key1"

    def get_key_wrap_algorithm(self):
        return "A256KW"


def _get_v2_encryption_data():
    encryption_agent = _EncryptionAgent(_EncryptionAlgorithm.AES_GCM_256, _ENCRYPTION_PROTOCOL_V2)
    wrapped_content_key = _WrappedContentKey("A256KW", b"encrypted-key", "local:key1")
    encrypted_region_info = _EncryptedRegionInfo(_GCM_REGION_DATA_LENGTH, _GCM_NONCE_LENGTH, _GCM_TAG_LENGTH)
    return _EncryptionData(
        None,
        encrypted_region_info,
        encryption_agent,
        wrapped_content_key,
        {"EncryptionLibrary": "Python " + VERSION},
    )


def test_get_adjusted_download_range_and_offset_when_v2_start_is_in_second_region_aligns_start_and_offsets():
    encryption_data = _get_v2_encryption_data()
    region_length = _GCM_NONCE_LENGTH + _GCM_REGION_DATA_LENGTH + _GCM_TAG_LENGTH
    start = _GCM_REGION_DATA_LENGTH + 123
    end = start + 10

    adjusted_range, offsets = get_adjusted_download_range_and_offset(start, end, None, encryption_data)

    assert adjusted_range == (region_length, (2 * region_length) - 1)
    assert offsets == (123, 134)


def test_get_adjusted_download_range_and_offset_when_v2_end_is_in_second_region_extends_to_region_boundary():
    encryption_data = _get_v2_encryption_data()
    region_length = _GCM_NONCE_LENGTH + _GCM_REGION_DATA_LENGTH + _GCM_TAG_LENGTH
    start = 5
    end = _GCM_REGION_DATA_LENGTH + 9

    adjusted_range, offsets = get_adjusted_download_range_and_offset(start, end, None, encryption_data)

    assert adjusted_range == (0, (2 * region_length) - 1)
    assert offsets == (5, _GCM_REGION_DATA_LENGTH + 10)


def test_generate_blob_encryption_data_when_v2_wraps_version_prefixed_cek():
    key_encryption_key = RecordingKeyWrapper()

    cek, iv, encryption_data = generate_blob_encryption_data(key_encryption_key, _ENCRYPTION_PROTOCOL_V2)

    assert iv is None
    assert key_encryption_key.last_wrapped == _ENCRYPTION_PROTOCOL_V2.encode().ljust(8, b"\0") + cek
    assert isinstance(encryption_data, str)


def test_generate_blob_encryption_data_when_v2_sets_gcm_encryption_agent():
    key_encryption_key = RecordingKeyWrapper()

    _, _, encryption_data = generate_blob_encryption_data(key_encryption_key, _ENCRYPTION_PROTOCOL_V2)
    encryption_data_dict = loads(encryption_data)

    assert list(encryption_data_dict["EncryptionAgent"].items()) == [
        ("Protocol", "2.0"),
        ("EncryptionAlgorithm", "AES_GCM_256"),
    ]


def test_generate_blob_encryption_data_when_v2_includes_encrypted_region_info_metadata():
    key_encryption_key = RecordingKeyWrapper()

    _, _, encryption_data = generate_blob_encryption_data(key_encryption_key, _ENCRYPTION_PROTOCOL_V2)
    encryption_data_dict = loads(encryption_data)

    assert list(encryption_data_dict["EncryptedRegionInfo"].items()) == [
        ("DataLength", _GCM_REGION_DATA_LENGTH),
        ("NonceLength", _GCM_NONCE_LENGTH),
    ]
    assert encryption_data_dict["KeyWrappingMetadata"] == {"EncryptionLibrary": "Python " + VERSION}


def _get_valid_v1_encryption_data_dict():
    kek = PerfstressKeyWrapper("key1")
    cek = b"a" * 32
    iv = b"b" * 16
    return _generate_encryption_data_dict(kek, cek, iv, _ENCRYPTION_PROTOCOL_V1)


def test__dict_to_encryption_data_when_protocol_is_unsupported_raises_value_error():
    encryption_data_dict = _get_valid_v1_encryption_data_dict()
    encryption_data_dict["EncryptionAgent"]["Protocol"] = "9.9"

    with pytest.raises(ValueError) as exc:
        _dict_to_encryption_data(encryption_data_dict)

    assert str(exc.value) == "Unsupported encryption version."


def test__dict_to_encryption_data_when_encryption_agent_missing_raises_value_error():
    encryption_data_dict = _get_valid_v1_encryption_data_dict()
    del encryption_data_dict["EncryptionAgent"]

    with pytest.raises(ValueError) as exc:
        _dict_to_encryption_data(encryption_data_dict)

    assert str(exc.value) == "Unsupported encryption version."


def test__dict_to_encryption_data_when_protocol_key_missing_preserves_keyerror_cause():
    encryption_data_dict = _get_valid_v1_encryption_data_dict()
    encryption_data_dict["EncryptionAgent"] = {
        "EncryptionAlgorithm": encryption_data_dict["EncryptionAgent"]["EncryptionAlgorithm"]
    }

    with pytest.raises(ValueError) as exc:
        _dict_to_encryption_data(encryption_data_dict)

    assert str(exc.value) == "Unsupported encryption version."
    assert isinstance(exc.value.__cause__, KeyError)
    assert exc.value.__cause__.args[0] == "Protocol"


def test__dict_to_encryption_data_when_key_wrapping_metadata_missing_sets_none():
    encryption_data_dict = _get_valid_v1_encryption_data_dict()
    del encryption_data_dict["KeyWrappingMetadata"]

    encryption_data = _dict_to_encryption_data(encryption_data_dict)

    assert encryption_data.key_wrapping_metadata is None
    assert encryption_data.encryption_agent.protocol == _ENCRYPTION_PROTOCOL_V1
    assert encryption_data.content_encryption_IV == b"b" * 16


def test__validate_and_unwrap_cek_when_protocol_is_unsupported_raises_value_error():
    encryption_data = _EncryptionData(
        None,
        _EncryptedRegionInfo(4, 12, 16),
        _EncryptionAgent(_EncryptionAlgorithm.AES_GCM_256, "9.9"),
        _WrappedContentKey("A256KW", b"wrapped-key", "key1"),
        {},
    )

    with pytest.raises(ValueError) as exc:
        _validate_and_unwrap_cek(encryption_data, PerfstressKeyWrapper("key1"), None)

    assert str(exc.value) == "Specified encryption version is not supported."

from azure.storage.blob._encryption import (
    _decrypt_message,
    encrypt_queue_message,
)
from azure.storage.blob._shared import decode_base64_to_bytes


def _get_queue_encryption_parts(message_text, version, kek):
    encrypted_message = loads(encrypt_queue_message(message_text, kek, version))
    encryption_data = _dict_to_encryption_data(encrypted_message["EncryptionData"])
    decoded_data = decode_base64_to_bytes(encrypted_message["EncryptedMessageContents"])
    return encryption_data, decoded_data


def test__validate_and_unwrap_cek_when_key_and_resolver_are_none_raises_value_error():
    kek = KeyWrapper("key1")
    encryption_data, _ = _get_queue_encryption_parts("hello world", _ENCRYPTION_PROTOCOL_V1, kek)

    with pytest.raises(ValueError) as error:
        _validate_and_unwrap_cek(encryption_data, None, None)

    assert str(error.value) == "Unable to decrypt. key_resolver and key_encryption_key cannot both be None."


def test__decrypt_message_when_message_is_none_raises_value_error():
    kek = KeyWrapper("key1")
    encryption_data, _ = _get_queue_encryption_parts("hello world", _ENCRYPTION_PROTOCOL_V1, kek)

    with pytest.raises(ValueError) as error:
        _decrypt_message(None, encryption_data, kek)

    assert str(error.value) == "message should not be None."


def test__decrypt_message_when_unwrap_validation_fails_for_unsupported_protocol_raises_value_error():
    encryption_data = _EncryptionData(
        b"0" * 16,
        None,
        _EncryptionAgent(_EncryptionAlgorithm.AES_CBC_256, "3.0"),
        _WrappedContentKey("A256KW", b"wrapped-key", "key1"),
        {},
    )

    with pytest.raises(ValueError) as error:
        _decrypt_message(b"ciphertext", encryption_data, KeyWrapper("key1"))

    assert str(error.value) == "Specified encryption version is not supported."


def test__decrypt_message_when_protocol_is_v2_returns_plaintext():
    plaintext = "hello encrypted world"
    kek = KeyWrapper("key1")
    encryption_data, decoded_data = _get_queue_encryption_parts(plaintext, _ENCRYPTION_PROTOCOL_V2, kek)

    decrypted = _decrypt_message(decoded_data, encryption_data, kek)

    assert decrypted == plaintext.encode("utf-8")


def test__decrypt_message_when_protocol_is_not_v1_or_v2_after_unwrap_raises_value_error():
    encryption_data = _EncryptionData(
        b"0" * 16,
        None,
        _EncryptionAgent(_EncryptionAlgorithm.AES_CBC_256, "3.0"),
        _WrappedContentKey("A256KW", b"wrapped-key", "key1"),
        {},
    )

    # Tests defensive branch — requires mock.
    with mock.patch("azure.storage.blob._encryption._validate_and_unwrap_cek", return_value=b"1" * 32):
        with pytest.raises(ValueError) as error:
            _decrypt_message(b"ciphertext", encryption_data, KeyWrapper("key1"))

    assert str(error.value) == "Specified encryption version is not supported."


def test__decrypt_message_when_protocol_is_v2_1_with_region_info_returns_plaintext():
    plaintext = b"hello encryption v2.1"
    cek = b"c" * 32
    nonce = (1).to_bytes(_GCM_NONCE_LENGTH, "big")
    kek = KeyWrapper("key1")
    wrapped_cek = kek.wrap_key(_ENCRYPTION_PROTOCOL_V2_1.encode().ljust(8, b"\0") + cek)
    encryption_data = _EncryptionData(
        None,
        _EncryptedRegionInfo(len(plaintext), _GCM_NONCE_LENGTH, _GCM_TAG_LENGTH),
        _EncryptionAgent(_EncryptionAlgorithm.AES_GCM_256, _ENCRYPTION_PROTOCOL_V2_1),
        _WrappedContentKey(kek.get_key_wrap_algorithm(), wrapped_cek, kek.get_kid()),
        {"EncryptionLibrary": "Python x.x.x"},
    )
    message = nonce + AESGCM(cek).encrypt(nonce, plaintext, None)

    assert _decrypt_message(message, encryption_data, kek) == plaintext


def test__decrypt_message_when_protocol_is_v1_returns_plaintext():
    plaintext = b"hello encryption v1"
    cek = b"k" * 32
    iv = b"i" * 16
    kek = KeyWrapper("key1")
    wrapped_cek = kek.wrap_key(cek)
    encryption_data = _EncryptionData(
        iv,
        None,
        _EncryptionAgent(_EncryptionAlgorithm.AES_CBC_256, _ENCRYPTION_PROTOCOL_V1),
        _WrappedContentKey(kek.get_key_wrap_algorithm(), wrapped_cek, kek.get_kid()),
        {"EncryptionLibrary": "Python x.x.x"},
    )
    cipher = _generate_AES_CBC_cipher(cek, iv)
    padder = PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    encryptor = cipher.encryptor()
    message = encryptor.update(padded_data) + encryptor.finalize()

    assert _decrypt_message(message, encryption_data, kek) == plaintext


def test_encrypt_blob_when_version_is_v2_returns_gcm_metadata_and_encrypted_payload():
    blob = b"hello world"
    kek = KeyWrapper("key1")

    with mock.patch("os.urandom", mock_urandom):
        encryption_data, encrypted_data = encrypt_blob(blob, kek, _ENCRYPTION_PROTOCOL_V2)

    parsed_encryption_data = loads(encryption_data)
    encryption_metadata = _dict_to_encryption_data(parsed_encryption_data)
    content_encryption_key = _validate_and_unwrap_cek(encryption_metadata, kek, None)
    nonce = encrypted_data[:_GCM_NONCE_LENGTH]
    ciphertext_with_tag = encrypted_data[_GCM_NONCE_LENGTH:]
    decrypted_data = AESGCM(content_encryption_key).decrypt(nonce, ciphertext_with_tag, None)

    assert parsed_encryption_data["EncryptionAgent"]["Protocol"] == _ENCRYPTION_PROTOCOL_V2
    assert parsed_encryption_data["EncryptionAgent"]["EncryptionAlgorithm"] == _EncryptionAlgorithm.AES_GCM_256
    assert parsed_encryption_data["EncryptionMode"] == "FullBlob"
    assert decrypted_data == blob


def test_generate_blob_encryption_data_when_kek_is_provided_for_v1_returns_metadata_and_keys():
    kek = KeyWrapper("key1")

    with mock.patch("os.urandom", mock_urandom):
        cek, iv, encryption_data = generate_blob_encryption_data(kek, _ENCRYPTION_PROTOCOL_V1)

    parsed_encryption_data = loads(encryption_data)
    encryption_metadata = _dict_to_encryption_data(parsed_encryption_data)

    assert len(cek) == 32
    assert len(iv) == 16
    assert parsed_encryption_data["EncryptionAgent"]["Protocol"] == _ENCRYPTION_PROTOCOL_V1
    assert parsed_encryption_data["EncryptionAgent"]["EncryptionAlgorithm"] == _EncryptionAlgorithm.AES_CBC_256
    assert parsed_encryption_data["EncryptionMode"] == "FullBlob"
    assert _validate_and_unwrap_cek(encryption_metadata, kek, None) == cek


def test_decrypt_blob_when_algorithm_is_unsupported_raises_value_error():
    fake_encryption_data = type(
        "FakeEncryptionData",
        (),
        {
            "encryption_agent": type(
                "FakeEncryptionAgent",
                (),
                {"encryption_algorithm": "UNSUPPORTED", "protocol": _ENCRYPTION_PROTOCOL_V1},
            )()
        },
    )()

    # Tests defensive branch — requires mock.
    with mock.patch("azure.storage.blob._encryption._dict_to_encryption_data", return_value=fake_encryption_data):
        with pytest.raises(ValueError) as exc:
            decrypt_blob(False, None, None, b"ciphertext", 0, 0, {"x-ms-meta-encryptiondata": "{}"})

    assert str(exc.value) == "Specified encryption algorithm is not supported."


class LocalKeyWrapper(object):
    def __init__(self, kid='local:key1'):
        self.kid = kid

    def wrap_key(self, key, algorithm='A256KW'):
        return key

    def unwrap_key(self, key, algorithm):
        return key

    def get_key_wrap_algorithm(self):
        return 'A256KW'

    def get_kid(self):
        return self.kid


def test_decrypt_blob_when_version_is_invalid_raises_value_error():
    # Tests defensive branch — requires mock.
    encryption_data = SimpleNamespace(
        content_encryption_IV=b'0' * 16,
        encrypted_region_info=None,
        encryption_agent=SimpleNamespace(
            encryption_algorithm=_EncryptionAlgorithm.AES_CBC_256,
            protocol='3.0',
        ),
    )

    with mock.patch('azure.storage.blob._encryption._dict_to_encryption_data', return_value=encryption_data):
        with pytest.raises(ValueError) as error:
            decrypt_blob(
                True,
                None,
                None,
                b'encrypted',
                0,
                0,
                {'x-ms-meta-encryptiondata': '{}'},
            )

    assert str(error.value) == 'Specified encryption version is not supported.'


def test_decrypt_blob_when_v1_has_no_content_range_returns_plaintext():
    key_encryption_key = LocalKeyWrapper('key1')
    plaintext = b'hello world'
    encryption_data, encrypted = encrypt_blob(plaintext, key_encryption_key, _ENCRYPTION_PROTOCOL_V1)

    decrypted = decrypt_blob(
        True,
        key_encryption_key,
        None,
        encrypted,
        0,
        0,
        {
            'x-ms-meta-encryptiondata': encryption_data,
            'x-ms-blob-type': 'BlockBlob',
        },
    )

    assert decrypted == plaintext


def test_decrypt_blob_when_v1_has_no_content_range_uses_metadata_iv_and_offsets():
    key_encryption_key = LocalKeyWrapper('key1')
    plaintext = b'abcdefghijklmnopqrstuvwxyz'
    encryption_data, encrypted = encrypt_blob(plaintext, key_encryption_key, _ENCRYPTION_PROTOCOL_V1)

    decrypted = decrypt_blob(
        True,
        key_encryption_key,
        None,
        encrypted,
        2,
        3,
        {
            'x-ms-meta-encryptiondata': encryption_data,
            'x-ms-blob-type': 'BlockBlob',
        },
    )

    assert decrypted == plaintext[2:-3]


def test_decrypt_blob_when_v1_iv_is_none_raises_value_error():
    # Tests defensive branch — requires mock.
    encryption_data = SimpleNamespace(
        content_encryption_IV=None,
        encrypted_region_info=None,
        encryption_agent=SimpleNamespace(
            encryption_algorithm=_EncryptionAlgorithm.AES_CBC_256,
            protocol=_ENCRYPTION_PROTOCOL_V1,
        ),
    )

    with mock.patch('azure.storage.blob._encryption._dict_to_encryption_data', return_value=encryption_data), mock.patch(
        'azure.storage.blob._encryption._validate_and_unwrap_cek', return_value=b'0' * 32
    ):
        with pytest.raises(ValueError) as error:
            decrypt_blob(
                True,
                None,
                None,
                b'encrypted',
                0,
                0,
                {
                    'x-ms-meta-encryptiondata': '{}',
                    'x-ms-blob-type': 'BlockBlob',
                },
            )

    assert str(error.value) == 'Missing required metadata for Encryption V1'


def test_decrypt_blob_when_version_skips_v1_and_v2_raises_value_error():
    # Tests defensive branch — requires mock.
    encryption_data = SimpleNamespace(
        content_encryption_IV=None,
        encrypted_region_info=None,
        encryption_agent=SimpleNamespace(
            encryption_algorithm=_EncryptionAlgorithm.AES_CBC_256,
            protocol='3.0',
        ),
    )

    with mock.patch('azure.storage.blob._encryption._dict_to_encryption_data', return_value=encryption_data), mock.patch(
        'azure.storage.blob._encryption._validate_and_unwrap_cek', return_value=b'0' * 32
    ), mock.patch(
        'azure.storage.blob._encryption._VALID_ENCRYPTION_PROTOCOLS',
        [_ENCRYPTION_PROTOCOL_V1, _ENCRYPTION_PROTOCOL_V2, _ENCRYPTION_PROTOCOL_V2_1, '3.0'],
    ):
        with pytest.raises(ValueError) as error:
            decrypt_blob(
                True,
                None,
                None,
                b'encrypted',
                0,
                0,
                {'x-ms-meta-encryptiondata': '{}'},
            )

    assert str(error.value) == 'Specified encryption version is not supported.'

from azure.storage.blob._encryption import get_blob_encryptor_and_padder


def test_decrypt_blob_when_v2_metadata_has_no_region_info_raises_value_error():
    # Tests defensive branch — requires mock.
    encryption_data = SimpleNamespace(
        encryption_agent=SimpleNamespace(
            encryption_algorithm=_EncryptionAlgorithm.AES_GCM_256,
            protocol=_ENCRYPTION_PROTOCOL_V2,
        ),
        encrypted_region_info=None,
    )

    with mock.patch("azure.storage.blob._encryption._dict_to_encryption_data", return_value=encryption_data), mock.patch(
        "azure.storage.blob._encryption._validate_and_unwrap_cek", return_value=b"0" * 32
    ):
        with pytest.raises(ValueError) as exc:
            decrypt_blob(
                False,
                None,
                None,
                b"ciphertext",
                0,
                0,
                {"x-ms-meta-encryptiondata": "{}"},
            )

    assert str(exc.value) == "Missing required metadata for Encryption V2"


def test_get_blob_encryptor_and_padder_when_cek_and_iv_are_provided_returns_working_encryptor_and_padder():
    cek = b"k" * 32
    iv = b"i" * 16
    plaintext = b"hello world"

    encryptor, padder = get_blob_encryptor_and_padder(cek, iv, True)
    padded = padder.update(plaintext) + padder.finalize()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    expected_padder = PKCS7(128).padder()
    expected_padded = expected_padder.update(plaintext) + expected_padder.finalize()
    expected_encryptor = _generate_AES_CBC_cipher(cek, iv).encryptor()
    expected_ciphertext = expected_encryptor.update(expected_padded) + expected_encryptor.finalize()

    assert padded == expected_padded
    assert ciphertext == expected_ciphertext


def test_encrypt_queue_message_when_message_is_none_raises_value_error():
    with pytest.raises(ValueError) as exc:
        encrypt_queue_message(None, KeyWrapper("key1"), _ENCRYPTION_PROTOCOL_V1)

    assert str(exc.value) == "message should not be None."


def test_encrypt_queue_message_when_key_encryption_key_is_none_raises_value_error():
    with pytest.raises(ValueError) as exc:
        encrypt_queue_message("hello world", None, _ENCRYPTION_PROTOCOL_V1)

    assert str(exc.value) == "key_encryption_key should not be None."


def test_encrypt_queue_message_when_key_encryption_key_missing_wrap_key_raises_attribute_error():
    valid_key = KeyWrapper("key1")
    invalid_key = lambda: None
    invalid_key.get_kid = valid_key.get_kid
    invalid_key.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm

    with pytest.raises(AttributeError) as exc:
        encrypt_queue_message("hello world", invalid_key, _ENCRYPTION_PROTOCOL_V1)

    assert str(exc.value) == _ERROR_OBJECT_INVALID.format("key encryption key", "wrap_key")
