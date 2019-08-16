# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio
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
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7

from azure.core.exceptions import HttpResponseError, ResourceExistsError

from azure.storage.queue._shared.encryption import (
    _ERROR_OBJECT_INVALID,
    _WrappedContentKey,
    _EncryptionAgent,
    _EncryptionData,
)

from azure.storage.queue import (
    VERSION,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
    NoEncodePolicy,
    NoDecodePolicy
)

from azure.storage.queue.aio import (
    QueueServiceClient,
    QueueClient
)

from encryption_test_helper import (
    KeyWrapper,
    KeyResolver,
    RSAKeyWrapper,
)
from queuetestcase import (
    QueueTestCase,
    record,
    TestMode,
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'encryptionqueue'


# ------------------------------------------------------------------------------

def _decode_base64_to_bytes(data):
        if isinstance(data, six.text_type):
            data = data.encode('utf-8')
        return b64decode(data)

class StorageQueueEncryptionTestAsync(QueueTestCase):
    def setUp(self):
        super(StorageQueueEncryptionTestAsync, self).setUp()

        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        self.qsc = QueueServiceClient(account_url=queue_url, credential=credentials)
        self.test_queues = []

    def tearDown(self):
        loop = asyncio.get_event_loop()
        if not self.is_playback():
            for queue in self.test_queues:
                try:
                    loop.run_until_complete(self.qsc.delete_queue(queue.queue_name))
                except:
                    pass
        return super(StorageQueueEncryptionTestAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = self.qsc.get_queue_client(queue_name)
        self.test_queues.append(queue)
        return queue

    async def _create_queue(self, prefix=TEST_QUEUE_PREFIX):
        queue = self._get_queue_reference(prefix)
        try:
            created = await queue.create_queue()
        except ResourceExistsError:
            pass
        return queue
    # --------------------------------------------------------------------------

    async def _test_get_messages_encrypted_kek(self):
        # Arrange
        self.qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue()
        await queue.enqueue_message(u'encrypted_message_2')

        # Act
        li = None
        async for m in queue.receive_messages():
            li = m

        # Assert
        self.assertEqual(li.content, u'encrypted_message_2')

    def test_get_messages_encrypted_kek(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_messages_encrypted_kek())

    async def _test_get_messages_encrypted_resolver(self):
        # Arrange
        self.qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue()
        await queue.enqueue_message(u'encrypted_message_2')
        key_resolver = KeyResolver()
        key_resolver.put_key(self.qsc.key_encryption_key)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        # Act
        li = None
        async for m in queue.receive_messages():
            li = m

        # Assert
        self.assertEqual(li.content, u'encrypted_message_2')

    def test_get_messages_encrypted_resolver(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_messages_encrypted_resolver())

    async def _test_peek_messages_encrypted_kek(self):
        # Arrange
        self.qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue()
        await queue.enqueue_message(u'encrypted_message_3')

        # Act
        li = await queue.peek_messages()

        # Assert
        self.assertEqual(li[0].content, u'encrypted_message_3')

    def test_peek_messages_encrypted_kek(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_peek_messages_encrypted_kek())

    async def _test_peek_messages_encrypted_resolver(self):
        # Arrange
        self.qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue()
        await queue.enqueue_message(u'encrypted_message_4')
        key_resolver = KeyResolver()
        key_resolver.put_key(self.qsc.key_encryption_key)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        # Act
        li = await queue.peek_messages()

        # Assert
        self.assertEqual(li[0].content, u'encrypted_message_4')

    def test_peek_messages_encrypted_resolver(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_peek_messages_encrypted_resolver())

    async def _test_peek_messages_encrypted_kek_RSA(self):

        # We can only generate random RSA keys, so this must be run live or 
        # the playback test will fail due to a change in kek values.
        if TestMode.need_recording_file(self.test_mode):
            return

            # Arrange
        self.qsc.key_encryption_key = RSAKeyWrapper('key2')
        queue = await self._create_queue()
        await queue.enqueue_message(u'encrypted_message_3')

        # Act
        li = await queue.peek_messages()

        # Assert
        self.assertEqual(li[0].content, u'encrypted_message_3')

    def test_peek_messages_encrypted_kek_RSA(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_peek_messages_encrypted_kek_RSA())

    async def _test_update_encrypted_message(self):
        # TODO: Recording doesn't work
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.enqueue_message(u'Update Me')

        messages = []
        async for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]
        list_result1.content = u'Updated'

        # Act
        message = await queue.update_message(list_result1)
        async for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Assert
        self.assertEqual(u'Updated', list_result2.content)

    def test_update_encrypted_message(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_encrypted_message())

    async def _test_update_encrypted_binary_message(self):
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        queue._config.message_encode_policy = BinaryBase64EncodePolicy()
        queue._config.message_decode_policy = BinaryBase64DecodePolicy()

        binary_message = self.get_random_bytes(100)
        await queue.enqueue_message(binary_message)
        messages = []
        async for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]

        # Act
        binary_message = self.get_random_bytes(100)
        list_result1.content = binary_message
        await queue.update_message(list_result1)

        async for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Assert
        self.assertEqual(binary_message, list_result2.content)

    def test_update_encrypted_binary_message(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_encrypted_binary_message())

    async def _test_update_encrypted_raw_text_message(self):
        # TODO: Recording doesn't work
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        queue._config.message_encode_policy = NoEncodePolicy()
        queue._config.message_decode_policy = NoDecodePolicy()

        raw_text = u'Update Me'
        await queue.enqueue_message(raw_text)
        messages = []
        async for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]

        # Act
        raw_text = u'Updated'
        list_result1.content = raw_text
        async for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Assert
        self.assertEqual(raw_text, list_result2.content)

    def test_update_encrypted_raw_text_message(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_encrypted_raw_text_message())

    async def _test_update_encrypted_json_message(self):
        # TODO: Recording doesn't work
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        queue._config.message_encode_policy = NoEncodePolicy()
        queue._config.message_decode_policy = NoDecodePolicy()

        message_dict = {'val1': 1, 'val2': '2'}
        json_text = dumps(message_dict)
        await queue.enqueue_message(json_text)
        messages = []
        async for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]

        # Act
        message_dict['val1'] = 0
        message_dict['val2'] = 'updated'
        json_text = dumps(message_dict)
        list_result1.content = json_text
        await queue.update_message(list_result1)

        async for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Assert
        self.assertEqual(message_dict, loads(list_result2.content))

    def test_update_encrypted_json_message(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_encrypted_json_message())

    async def _test_invalid_value_kek_wrap(self):
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.get_kid = None

        with self.assertRaises(AttributeError) as e:
            await  queue.enqueue_message(u'message')

        self.assertEqual(str(e.exception), _ERROR_OBJECT_INVALID.format('key encryption key', 'get_kid'))

        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.get_kid = None
        with self.assertRaises(AttributeError):
            await  queue.enqueue_message(u'message')

        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.wrap_key = None
        with self.assertRaises(AttributeError):
            await queue.enqueue_message(u'message')

    def test_invalid_value_kek_wrap(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_invalid_value_kek_wrap())

    async def _test_missing_attribute_kek_wrap(self):
        # Arrange
        queue = await self._create_queue()

        valid_key = KeyWrapper('key1')

        # Act
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute wrap_key
        queue.key_encryption_key = invalid_key_1
        with self.assertRaises(AttributeError):
            await queue.enqueue_message(u'message')

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.wrap_key = valid_key.wrap_key
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute get_key_wrap_algorithm
        queue.key_encryption_key = invalid_key_2
        with self.assertRaises(AttributeError):
            await queue.enqueue_message(u'message')

        invalid_key_3 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_3.wrap_key = valid_key.wrap_key
        # No attribute get_kid
        queue.key_encryption_key = invalid_key_3
        with self.assertRaises(AttributeError):
            await queue.enqueue_message(u'message')

    def test_missing_attribute_kek_wrap(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_missing_attribute_kek_wrap())

    async def _test_invalid_value_kek_unwrap(self):
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.enqueue_message(u'message')

        # Act
        queue.key_encryption_key.unwrap_key = None
        with self.assertRaises(HttpResponseError):
            await queue.peek_messages()

        queue.key_encryption_key.get_kid = None
        with self.assertRaises(HttpResponseError):
            await queue.peek_messages()
    
    def test_invalid_value_kek_unwrap(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_invalid_value_kek_unwrap())

    async def _test_missing_attribute_kek_unrwap(self):
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.enqueue_message(u'message')

        # Act
        valid_key = KeyWrapper('key1')
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.unwrap_key = valid_key.unwrap_key
        # No attribute get_kid
        queue.key_encryption_key = invalid_key_1
        with self.assertRaises(HttpResponseError) as e:
            await queue.peek_messages()

        self.assertEqual(str(e.exception), "Decryption failed.")

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute unwrap_key
        queue.key_encryption_key = invalid_key_2
        with self.assertRaises(HttpResponseError):
            await queue.peek_messages()
    
    def test_missing_attribute_kek_unrwap(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_missing_attribute_kek_unrwap())

    async def _test_validate_encryption(self):
        # Arrange
        queue = await self._create_queue()
        kek = KeyWrapper('key1')
        queue.key_encryption_key = kek
        await queue.enqueue_message(u'message')

        # Act
        queue.key_encryption_key = None  # Message will not be decrypted
        li = await queue.peek_messages()
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
        decrypted_data = _decode_base64_to_bytes(message)
        decryptor = cipher.decryptor()
        decrypted_data = (decryptor.update(decrypted_data) + decryptor.finalize())

        # unpad data
        unpadder = PKCS7(128).unpadder()
        decrypted_data = (unpadder.update(decrypted_data) + unpadder.finalize())

        decrypted_data = decrypted_data.decode(encoding='utf-8')

        # Assert
        self.assertEqual(decrypted_data, u'message')
    
    def test_validate_encryption(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_validate_encryption())

    async def _test_put_with_strict_mode(self):
        # Arrange
        queue = await self._create_queue()
        kek = KeyWrapper('key1')
        queue.key_encryption_key = kek
        queue.require_encryption = True

        await queue.enqueue_message(u'message')
        queue.key_encryption_key = None

        # Assert
        with self.assertRaises(ValueError) as e:
            await queue.enqueue_message(u'message')

        self.assertEqual(str(e.exception), "Encryption required but no key was provided.")
    
    def test_put_with_strict_mode(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_with_strict_mode())

    async def _test_get_with_strict_mode(self):
        # Arrange
        queue = await self._create_queue()
        await queue.enqueue_message(u'message')

        queue.require_encryption = True
        queue.key_encryption_key = KeyWrapper('key1')
        with self.assertRaises(ValueError) as e:
            messages = []
            async for m in queue.receive_messages():
                messages.append(m)
            _ = messages[0]
        self.assertEqual(str(e.exception), 'Message was not encrypted.')
    
    def test_get_with_strict_mode(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_with_strict_mode())

    async def _test_encryption_add_encrypted_64k_message(self):
        # Arrange
        queue = await self._create_queue()
        message = u'a' * 1024 * 64

        # Act
        await queue.enqueue_message(message)

        # Assert
        queue.key_encryption_key = KeyWrapper('key1')
        with self.assertRaises(HttpResponseError):
            await queue.enqueue_message(message)
        
    def test_encryption_add_encrypted_64k_message(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_encryption_add_encrypted_64k_message())

    async def _test_encryption_nonmatching_kid(self):
        # Arrange
        queue = await self._create_queue()
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.enqueue_message(u'message')

        # Act
        queue.key_encryption_key.kid = 'Invalid'

        # Assert
        with self.assertRaises(HttpResponseError) as e:
            messages = []
            async for m in queue.receive_messages():
                messages.append(m)

        self.assertEqual(str(e.exception), "Decryption failed.")

    def test_encryption_nonmatching_kid(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_encryption_nonmatching_kid())


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
