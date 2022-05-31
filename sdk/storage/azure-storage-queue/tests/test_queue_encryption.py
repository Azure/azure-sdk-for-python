# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import six
from base64 import (
    b64decode,
)
from json import (
    loads,
    dumps,
)

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.storage.queue._shared import decode_base64_to_bytes
from azure.storage.queue._shared.encryption import (
    _ERROR_OBJECT_INVALID,
    _GCM_REGION_DATA_LENGTH,
    _GCM_NONCE_LENGTH,
    _GCM_TAG_LENGTH,
    _EncryptedRegionInfo,
    _EncryptionAgent,
    _EncryptionAlgorithm,
    _EncryptionData,
    _WrappedContentKey,
)

from azure.storage.queue import (
    VERSION,
    QueueServiceClient,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
)
from encryption_test_helper import (
    KeyWrapper,
    KeyResolver,
    RSAKeyWrapper,
)
from settings.testcase import QueuePreparer
from devtools_testutils.storage import StorageTestCase

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'encryptionqueue'
# ------------------------------------------------------------------------------

def _decode_base64_to_bytes(data):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')
    return b64decode(data)

class StorageQueueEncryptionTest(StorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX, **kwargs):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name, **kwargs)
        return queue

    def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX, **kwargs):
        queue = self._get_queue_reference(qsc, prefix, **kwargs)
        try:
            created = queue.create_queue()
        except ResourceExistsError:
            pass
        return queue

    # --------------------------------------------------------------------------

    @QueuePreparer()
    def test_get_messages_encrypted_kek(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = self._create_queue(qsc)
        queue.send_message(u'encrypted_message_2')

        # Act
        li = next(queue.receive_messages())

        # Assert
        self.assertEqual(li.content, u'encrypted_message_2')

    @QueuePreparer()
    def test_get_messages_encrypted_resolver(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = self._create_queue(qsc)
        queue.send_message(u'encrypted_message_2')
        key_resolver = KeyResolver()
        key_resolver.put_key(qsc.key_encryption_key)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        # Act
        li = next(queue.receive_messages())

        # Assert
        self.assertEqual(li.content, u'encrypted_message_2')

    @QueuePreparer()
    def test_peek_messages_encrypted_kek(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = self._create_queue(qsc)
        queue.send_message(u'encrypted_message_3')

        # Act
        li = queue.peek_messages()

        # Assert
        self.assertEqual(li[0].content, u'encrypted_message_3')

    @QueuePreparer()
    def test_peek_messages_encrypted_resolver(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = self._create_queue(qsc)
        queue.send_message(u'encrypted_message_4')
        key_resolver = KeyResolver()
        key_resolver.put_key(qsc.key_encryption_key)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        # Act
        li = queue.peek_messages()

        # Assert
        self.assertEqual(li[0].content, u'encrypted_message_4')

    @pytest.mark.live_test_only
    @QueuePreparer()
    def test_peek_messages_encrypted_kek_RSA(self, storage_account_name, storage_account_key):

        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = RSAKeyWrapper('key2')
        queue = self._create_queue(qsc)
        queue.send_message(u'encrypted_message_3')

        # Act
        li = queue.peek_messages()

        # Assert
        self.assertEqual(li[0].content, u'encrypted_message_3')

    @pytest.mark.live_test_only
    @QueuePreparer()
    def test_update_encrypted_message(self, storage_account_name, storage_account_key):
        # TODO: Recording doesn't work
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        queue.send_message(u'Update Me')

        messages = queue.receive_messages()
        list_result1 = next(messages)
        list_result1.content = u'Updated'

        # Act
        message = queue.update_message(list_result1)
        list_result2 = next(messages)

        # Assert
        self.assertEqual(u'Updated', list_result2.content)

    @QueuePreparer()
    def test_update_encrypted_binary_message(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc, message_encode_policy=BinaryBase64EncodePolicy(), message_decode_policy=BinaryBase64DecodePolicy())
        queue.key_encryption_key = KeyWrapper('key1')

        binary_message = self.get_random_bytes(100)
        queue.send_message(binary_message)
        messages = []
        for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]

        # Act
        binary_message = self.get_random_bytes(100)
        list_result1.content = binary_message
        queue.update_message(list_result1)

        for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]


        # Assert
        self.assertEqual(binary_message, list_result2.content)

    @pytest.mark.live_test_only
    @QueuePreparer()
    def test_update_encrypted_raw_text_message(self, storage_account_name, storage_account_key):
        # TODO: Recording doesn't work
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc, message_encode_policy=None, message_decode_policy=None)
        queue.key_encryption_key = KeyWrapper('key1')

        raw_text = u'Update Me'
        queue.send_message(raw_text)
        messages = queue.receive_messages()
        list_result1 = next(messages)

        # Act
        raw_text = u'Updated'
        list_result1.content = raw_text
        queue.update_message(list_result1)

        list_result2 = next(messages)

        # Assert
        self.assertEqual(raw_text, list_result2.content)

    @pytest.mark.live_test_only
    @QueuePreparer()
    def test_update_encrypted_json_message(self, storage_account_name, storage_account_key):
        # TODO: Recording doesn't work
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc, message_encode_policy=None, message_decode_policy=None)
        queue.key_encryption_key = KeyWrapper('key1')

        message_dict = {'val1': 1, 'val2': '2'}
        json_text = dumps(message_dict)
        queue.send_message(json_text)
        messages = queue.receive_messages()
        list_result1 = next(messages)

        # Act
        message_dict['val1'] = 0
        message_dict['val2'] = 'updated'
        json_text = dumps(message_dict)
        list_result1.content = json_text
        queue.update_message(list_result1)

        list_result2 = next(messages)

        # Assert
        self.assertEqual(message_dict, loads(list_result2.content))

    @QueuePreparer()
    def test_invalid_value_kek_wrap(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.get_kid = None

        with self.assertRaises(AttributeError) as e:
            queue.send_message(u'message')

        self.assertEqual(str(e.exception), _ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid'))

        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.get_kid = None
        with self.assertRaises(AttributeError):
            queue.send_message(u'message')

        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.wrap_key = None
        with self.assertRaises(AttributeError):
            queue.send_message(u'message')

    @QueuePreparer()
    def test_missing_attribute_kek_wrap(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)

        valid_key = KeyWrapper('key1')

        # Act
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute wrap_key
        queue.key_encryption_key = invalid_key_1
        with self.assertRaises(AttributeError):
            queue.send_message(u'message')

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.wrap_key = valid_key.wrap_key
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute get_key_wrap_algorithm
        queue.key_encryption_key = invalid_key_2
        with self.assertRaises(AttributeError):
            queue.send_message(u'message')

        invalid_key_3 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_3.wrap_key = valid_key.wrap_key
        # No attribute get_kid
        queue.key_encryption_key = invalid_key_3
        with self.assertRaises(AttributeError):
            queue.send_message(u'message')

    @QueuePreparer()
    def test_invalid_value_kek_unwrap(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        queue.send_message(u'message')

        # Act
        queue.key_encryption_key.unwrap_key = None
        with self.assertRaises(HttpResponseError):
            queue.peek_messages()

        queue.key_encryption_key.get_kid = None
        with self.assertRaises(HttpResponseError):
            queue.peek_messages()

    @QueuePreparer()
    def test_missing_attribute_kek_unrwap(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        queue.send_message(u'message')

        # Act
        valid_key = KeyWrapper('key1')
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.unwrap_key = valid_key.unwrap_key
        # No attribute get_kid
        queue.key_encryption_key = invalid_key_1
        with self.assertRaises(HttpResponseError) as e:
            queue.peek_messages()

        assert "Decryption failed." in str(e.exception)

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute unwrap_key
        queue.key_encryption_key = invalid_key_2
        with self.assertRaises(HttpResponseError):
            queue.peek_messages()

    @QueuePreparer()
    def test_validate_encryption(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        kek = KeyWrapper('key1')
        queue.key_encryption_key = kek
        queue.send_message(u'message')

        # Act
        queue.key_encryption_key = None  # Message will not be decrypted
        li = queue.peek_messages()
        message = li[0].content
        message = loads(message)

        encryption_data = message['EncryptionData']

        wrapped_content_key = encryption_data['WrappedContentKey']
        wrapped_content_key = _WrappedContentKey(
            wrapped_content_key['Algorithm'],
            b64decode(wrapped_content_key['EncryptedKey'].encode(encoding='utf-8')),
            wrapped_content_key['KeyId'])

        encryption_agent = encryption_data['EncryptionAgent']
        encryption_agent = _EncryptionAgent(
            encryption_agent['EncryptionAlgorithm'],
            encryption_agent['Protocol'])

        encryption_data = _EncryptionData(
            b64decode(encryption_data['ContentEncryptionIV'].encode(encoding='utf-8')),
            None,
            encryption_agent,
            wrapped_content_key,
            {'EncryptionLibrary': VERSION})

        message = message['EncryptedMessageContents']
        content_encryption_key = kek.unwrap_key(
            encryption_data.wrapped_content_key.encrypted_key,
            encryption_data.wrapped_content_key.algorithm)

        # Create decryption cipher
        backend = backends.default_backend()
        algorithm = AES(content_encryption_key)
        mode = CBC(encryption_data.content_encryption_IV)
        cipher = Cipher(algorithm, mode, backend)

        # decode and decrypt data
        decrypted_data = decode_base64_to_bytes(message)
        decryptor = cipher.decryptor()
        decrypted_data = (decryptor.update(decrypted_data) + decryptor.finalize())

        # unpad data
        unpadder = PKCS7(128).unpadder()
        decrypted_data = (unpadder.update(decrypted_data) + unpadder.finalize())

        decrypted_data = decrypted_data.decode(encoding='utf-8')

        # Assert
        self.assertEqual(decrypted_data, u'message')

    @QueuePreparer()
    def test_put_with_strict_mode(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        kek = KeyWrapper('key1')
        queue.key_encryption_key = kek
        queue.require_encryption = True

        queue.send_message(u'message')
        queue.key_encryption_key = None

        # Assert
        with self.assertRaises(ValueError) as e:
            queue.send_message(u'message')

        self.assertEqual(str(e.exception), "Encryption required but no key was provided.")

    @QueuePreparer()
    def test_get_with_strict_mode(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        queue.send_message(u'message')

        queue.require_encryption = True
        queue.key_encryption_key = KeyWrapper('key1')
        with self.assertRaises(ValueError) as e:
            next(queue.receive_messages())

        self.assertTrue('Message was either not encrypted or metadata was incorrect.' in str(e.exception))

    @QueuePreparer()
    def test_encryption_add_encrypted_64k_message(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        message = u'a' * 1024 * 64

        # Act
        queue.send_message(message)

        # Assert
        queue.key_encryption_key = KeyWrapper('key1')
        with self.assertRaises(HttpResponseError):
            queue.send_message(message)

    @QueuePreparer()
    def test_encryption_nonmatching_kid(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        queue.send_message(u'message')

        # Act
        queue.key_encryption_key.kid = 'Invalid'

        # Assert
        with self.assertRaises(HttpResponseError) as e:
            next(queue.receive_messages())

        assert "Decryption failed." in str(e.exception)

    @QueuePreparer()
    def test_get_message_encrypted_kek_v2(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        queue = self._create_queue(qsc)
        content = 'Hello World Encrypted!'

        # Act
        queue.send_message(content)
        message = queue.receive_message()

        # Assert
        self.assertEqual(content, message.content)

    @QueuePreparer()
    def test_get_message_encrypted_resolver_v2(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        key_resolver = KeyResolver()
        key_resolver.put_key(qsc.key_encryption_key)

        queue = self._create_queue(qsc)
        content = 'Hello World Encrypted!'

        # Act
        queue.send_message(content)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        message = queue.receive_message()

        # Assert
        self.assertEqual(content, message.content)

    @pytest.mark.live_test_only
    @QueuePreparer()
    def test_get_message_encrypted_kek_RSA_v2(self, storage_account_name, storage_account_key):
        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.

        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=RSAKeyWrapper('key2'))
        queue = self._create_queue(qsc)
        content = 'Hello World Encrypted!'

        # Act
        queue.send_message(content)
        message = queue.receive_message()

        # Assert
        self.assertEqual(content, message.content)

    @QueuePreparer()
    def test_update_encrypted_message_v2(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            requires_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        queue = self._create_queue(qsc)
        queue.send_message('Update Me')

        message = queue.receive_message()
        message.content = 'Updated'

        # Act
        queue.update_message(message)
        message = queue.receive_message()

        # Assert
        self.assertEqual('Updated', message.content)

    @QueuePreparer()
    def test_update_encrypted_binary_message_v2(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            requires_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        queue = self._create_queue(
            qsc,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())
        queue.key_encryption_key = KeyWrapper('key1')

        queue.send_message(b'Update Me')
        message = queue.receive_message()
        message.content = b'Updated'

        # Act
        queue.update_message(message)
        message = queue.receive_message()

        # Assert
        self.assertEqual(b'Updated', message.content)

    @QueuePreparer()
    def test_validate_encryption_v2(self, storage_account_name, storage_account_key):
        # Arrange
        kek = KeyWrapper('key1')
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)
        queue = self._create_queue(qsc)
        content = 'Hello World Encrypted!'
        queue.send_message(content)

        # Act
        queue.require_encryption = False
        queue.key_encryption_key = None  # Message will not be decrypted
        message = queue.receive_message().content
        message = loads(message)

        encryption_data = message['EncryptionData']
        self.assertIsNotNone(encryption_data)

        wrapped_content_key = encryption_data['WrappedContentKey']
        wrapped_content_key = _WrappedContentKey(
            wrapped_content_key['Algorithm'],
            b64decode(wrapped_content_key['EncryptedKey'].encode(encoding='utf-8')),
            wrapped_content_key['KeyId'])
        self.assertEqual(kek.get_key_wrap_algorithm(), wrapped_content_key.algorithm)
        self.assertEqual(kek.get_kid(), wrapped_content_key.key_id)

        encryption_agent = encryption_data['EncryptionAgent']
        encryption_agent = _EncryptionAgent(
            encryption_agent['EncryptionAlgorithm'],
            encryption_agent['Protocol'])
        self.assertEqual(_EncryptionAlgorithm.AES_GCM_256, encryption_agent.encryption_algorithm)
        self.assertEqual('2.0', encryption_agent.protocol)

        encrypted_region_info = encryption_data['EncryptedRegionInfo']
        encrypted_region_info = _EncryptedRegionInfo(
            encrypted_region_info['EncryptedRegionDataLength'],
            encrypted_region_info['NonceLength'],
            encrypted_region_info['TagLength'])
        self.assertEqual(_GCM_REGION_DATA_LENGTH, encrypted_region_info.encrypted_region_data_length)
        self.assertEqual(_GCM_NONCE_LENGTH, encrypted_region_info.nonce_length)
        self.assertEqual(_GCM_TAG_LENGTH, encrypted_region_info.tag_length)

        encryption_data = _EncryptionData(
            None,
            encrypted_region_info,
            encryption_agent,
            wrapped_content_key,
            {'EncryptionLibrary': VERSION})

        message = message['EncryptedMessageContents']
        message = decode_base64_to_bytes(message)
        content_encryption_key = kek.unwrap_key(
            encryption_data.wrapped_content_key.encrypted_key,
            encryption_data.wrapped_content_key.algorithm)

        nonce_length = encryption_data.encrypted_region_info.nonce_length

        # First bytes are the nonce
        nonce = message[:nonce_length]
        ciphertext_with_tag = message[nonce_length:]

        aesgcm = AESGCM(content_encryption_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        decrypted_data = decrypted_data.decode(encoding='utf-8')

        # Assert
        self.assertEqual(content, decrypted_data)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
