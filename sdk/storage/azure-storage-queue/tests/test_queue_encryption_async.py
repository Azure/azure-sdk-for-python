# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import unittest
from base64 import b64decode, b64encode
from json import dumps, loads
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.storage.queue import BinaryBase64DecodePolicy, BinaryBase64EncodePolicy, VERSION
from azure.storage.queue.aio import QueueServiceClient
from azure.storage.queue._encryption import (
    _dict_to_encryption_data,
    _EncryptionAgent,
    _EncryptionData,
    _ERROR_OBJECT_INVALID,
    _GCM_NONCE_LENGTH,
    _GCM_TAG_LENGTH,
    _validate_and_unwrap_cek,
    _WrappedContentKey,
)
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from encryption_test_helper import KeyResolver, KeyWrapper, mock_urandom, RSAKeyWrapper
from settings.testcase import QueuePreparer

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'encryptionqueue'
# ------------------------------------------------------------------------------

def _decode_base64_to_bytes(data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        return b64decode(data)

@mock.patch('os.urandom', mock_urandom)
class TestAsyncStorageQueueEncryption(AsyncStorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX, **kwargs):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name, **kwargs)
        return queue

    async def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX, **kwargs):
        queue = self._get_queue_reference(qsc, prefix, **kwargs)
        try:
            created = await queue.create_queue()
        except ResourceExistsError:
            pass
        return queue
    # --------------------------------------------------------------------------

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_encrypted_kek(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue(qsc)
        await queue.send_message('encrypted_message_2')

        # Act
        li = None
        async for m in queue.receive_messages():
            li = m

        # Assert
        assert li.content == 'encrypted_message_2'

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_encrypted_resolver(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue(qsc)
        await queue.send_message('encrypted_message_2')
        key_resolver = KeyResolver()
        key_resolver.put_key(qsc.key_encryption_key)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        # Act
        li = None
        async for m in queue.receive_messages():
            li = m

        # Assert
        assert li.content == 'encrypted_message_2'

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_peek_messages_encrypted_kek(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue(qsc)
        await queue.send_message('encrypted_message_3')

        # Act
        li = await queue.peek_messages()

        # Assert
        assert li[0].content == 'encrypted_message_3'

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_peek_messages_encrypted_resolver(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        qsc.key_encryption_key = KeyWrapper('key1')
        queue = await self._create_queue(qsc)
        await queue.send_message('encrypted_message_4')
        key_resolver = KeyResolver()
        key_resolver.put_key(qsc.key_encryption_key)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        # Act
        li = await queue.peek_messages()

        # Assert
        assert li[0].content == 'encrypted_message_4'

    @pytest.mark.live_test_only
    @QueuePreparer()
    async def test_peek_messages_encrypted_kek_RSA(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.

        # Arrange
        qsc.key_encryption_key = RSAKeyWrapper('key2')
        queue = await self._create_queue(qsc)
        await queue.send_message('encrypted_message_3')

        # Act
        li = await queue.peek_messages()

        # Assert
        assert li[0].content == 'encrypted_message_3'

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_encrypted_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.send_message('Update Me')

        messages = []
        async for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]
        list_result1.content = 'Updated'

        # Act
        message = await queue.update_message(list_result1)
        async for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Assert
        assert 'Updated' == list_result2.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_encrypted_binary_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(
            qsc, message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())
        queue.key_encryption_key = KeyWrapper('key1')

        binary_message = self.get_random_bytes(100)
        await queue.send_message(binary_message)
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
        assert binary_message == list_result2.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_encrypted_raw_text_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc, message_encode_policy=None, message_decode_policy=None)
        queue.key_encryption_key = KeyWrapper('key1')

        raw_text = 'Update Me'
        await queue.send_message(raw_text)
        messages = []
        async for m in queue.receive_messages():
            messages.append(m)
        list_result1 = messages[0]

        # Act
        raw_text = 'Updated'
        list_result1.content = raw_text
        async for m in queue.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Assert
        assert raw_text == list_result2.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_encrypted_json_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc, message_encode_policy=None, message_decode_policy=None)
        queue.key_encryption_key = KeyWrapper('key1')

        message_dict = {'val1': 1, 'val2': '2'}
        json_text = dumps(message_dict)
        await queue.send_message(json_text)
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
        assert message_dict == loads(list_result2.content)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_invalid_value_kek_wrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.get_kid = None

        with pytest.raises(AttributeError) as e:
            await  queue.send_message('message')

        assert str(e.value.args[0]), _ERROR_OBJECT_INVALID.format('key encryption key' == 'get_kid')

        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.get_kid = None
        with pytest.raises(AttributeError):
            await  queue.send_message('message')

        queue.key_encryption_key = KeyWrapper('key1')
        queue.key_encryption_key.wrap_key = None
        with pytest.raises(AttributeError):
            await queue.send_message('message')

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_missing_attribute_kek_wrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)

        valid_key = KeyWrapper('key1')

        # Act
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_1.get_kid = valid_key.get_kid
        # No attribute wrap_key
        queue.key_encryption_key = invalid_key_1
        with pytest.raises(AttributeError):
            await queue.send_message('message')

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.wrap_key = valid_key.wrap_key
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute get_key_wrap_algorithm
        queue.key_encryption_key = invalid_key_2
        with pytest.raises(AttributeError):
            await queue.send_message('message')

        invalid_key_3 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_3.get_key_wrap_algorithm = valid_key.get_key_wrap_algorithm
        invalid_key_3.wrap_key = valid_key.wrap_key
        # No attribute get_kid
        queue.key_encryption_key = invalid_key_3
        with pytest.raises(AttributeError):
            await queue.send_message('message')

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_invalid_value_kek_unwrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.send_message('message')

        # Act
        queue.key_encryption_key.unwrap_key = None
        with pytest.raises(HttpResponseError):
            await queue.peek_messages()

        queue.key_encryption_key.get_kid = None
        with pytest.raises(HttpResponseError):
            await queue.peek_messages()

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_missing_attribute_kek_unwrap(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.send_message('message')

        # Act
        valid_key = KeyWrapper('key1')
        invalid_key_1 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_1.unwrap_key = valid_key.unwrap_key
        # No attribute get_kid
        queue.key_encryption_key = invalid_key_1
        with pytest.raises(HttpResponseError) as e:
            await queue.peek_messages()

        assert "Decryption failed." in str(e.value.args[0])

        invalid_key_2 = lambda: None  # functions are objects, so this effectively creates an empty object
        invalid_key_2.get_kid = valid_key.get_kid
        # No attribute unwrap_key
        queue.key_encryption_key = invalid_key_2
        with pytest.raises(HttpResponseError):
            await queue.peek_messages()

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_validate_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        kek = KeyWrapper('key1')
        queue.key_encryption_key = kek
        await queue.send_message('message')

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
        decrypted_data = _decode_base64_to_bytes(message)
        decryptor = cipher.decryptor()
        decrypted_data = (decryptor.update(decrypted_data) + decryptor.finalize())

        # unpad data
        unpadder = PKCS7(128).unpadder()
        decrypted_data = (unpadder.update(decrypted_data) + unpadder.finalize())

        decrypted_data = decrypted_data.decode(encoding='utf-8')

        # Assert
        assert decrypted_data == 'message'

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_put_with_strict_mode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        kek = KeyWrapper('key1')
        queue.key_encryption_key = kek
        queue.require_encryption = True

        await queue.send_message('message')
        queue.key_encryption_key = None

        # Assert
        with pytest.raises(ValueError) as e:
            await queue.send_message('message')

        assert str(e.value.args[0]) == "Encryption required but no key was provided."

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_with_strict_mode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        await queue.send_message('message')

        queue.require_encryption = True
        queue.key_encryption_key = KeyWrapper('key1')
        with pytest.raises(ValueError) as e:
            messages = []
            async for m in queue.receive_messages():
                messages.append(m)
            _ = messages[0]
        assert 'Message was either not encrypted or metadata was incorrect.' in str(e.value.args[0])

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_encryption_add_encrypted_64k_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        message = 'a' * 1024 * 64

        # Act
        await queue.send_message(message)

        # Assert
        queue.key_encryption_key = KeyWrapper('key1')
        with pytest.raises(HttpResponseError):
            await queue.send_message(message)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_encryption_nonmatching_kid(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue = await self._create_queue(qsc)
        queue.key_encryption_key = KeyWrapper('key1')
        await queue.send_message('message')

        # Act
        queue.key_encryption_key.kid = 'Invalid'

        # Assert
        with pytest.raises(HttpResponseError) as e:
            messages = []
            async for m in queue.receive_messages():
                messages.append(m)

        assert "Decryption failed." in str(e.value.args[0])

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_message_encrypted_kek_v2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        queue = await self._create_queue(qsc)
        content = 'Hello World Encrypted!'

        # Act
        await queue.send_message(content)
        message = await queue.receive_message()

        # Assert
        assert content == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_message_encrypted_resolver_v2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        key_resolver = KeyResolver()
        key_resolver.put_key(qsc.key_encryption_key)

        queue = await self._create_queue(qsc)
        content = 'Hello World Encrypted!'

        # Act
        await queue.send_message(content)
        queue.key_resolver_function = key_resolver.resolve_key
        queue.key_encryption_key = None  # Ensure that the resolver is used

        message = await queue.receive_message()

        # Assert
        assert content == message.content

    @pytest.mark.live_test_only
    @QueuePreparer()
    async def test_get_message_encrypted_kek_RSA_v2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # We can only generate random RSA keys, so this must be run live or
        # the playback test will fail due to a change in kek values.

        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=RSAKeyWrapper('key2'))
        queue = await self._create_queue(qsc)
        content = 'Hello World Encrypted!'

        # Act
        await queue.send_message(content)
        message = await queue.receive_message()

        # Assert
        assert content == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_encrypted_message_v2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        queue = await self._create_queue(qsc)
        await queue.send_message('Update Me')

        message = await queue.receive_message()
        message.content = 'Updated'

        # Act
        await queue.update_message(message)
        message = await queue.receive_message()

        # Assert
        assert 'Updated' == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_encrypted_binary_message_v2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            requires_encryption=True,
            encryption_version='2.0',
            key_encryption_key=KeyWrapper('key1'))
        queue = await self._create_queue(
            qsc,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())
        queue.key_encryption_key = KeyWrapper('key1')

        await queue.send_message(b'Update Me')
        message = await queue.receive_message()
        message.content = b'Updated'

        # Act
        await queue.update_message(message)
        message = await queue.receive_message()

        # Assert
        assert b'Updated' == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_encryption_v2_v1_downgrade(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        kek = KeyWrapper('key1')
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            requires_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)
        queue = await self._create_queue(qsc)
        await queue.send_message('Hello World Encrypted!')

        queue.require_encryption = False
        queue.key_encryption_key = None  # Message will not be decrypted
        message = await queue.receive_message()
        content = loads(message.content)

        # Modify metadata to look like V1
        encryption_data = content['EncryptionData']
        encryption_data['EncryptionAgent']['Protocol'] = '1.0'
        encryption_data['EncryptionAgent']['EncryptionAlgorithm'] = 'AES_CBC_256'
        iv = b64encode(os.urandom(16))
        encryption_data['ContentEncryptionIV'] = iv.decode('utf-8')
        content['EncryptionData'] = encryption_data

        message.content = dumps(content)

        # Act / Assert
        # Update without encryption
        await queue.update_message(message)

        # Re-enable encryption for receive
        queue.require_encryption = True
        queue.key_encryption_key = kek

        with pytest.raises(HttpResponseError) as e:
            await queue.receive_message()

        assert 'Decryption failed.' in str(e.value.args[0])

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_validate_encryption_v2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        kek = KeyWrapper('key1')
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)
        queue = await self._create_queue(qsc)
        content = 'Hello World Encrypted!'
        await queue.send_message(content)

        # Act
        queue.require_encryption = False
        queue.key_encryption_key = None  # Message will not be decrypted
        message = (await queue.receive_message()).content
        message = loads(message)

        encryption_data = _dict_to_encryption_data(message['EncryptionData'])
        encryption_agent = encryption_data.encryption_agent
        assert '2.0' == encryption_agent.protocol
        assert 'AES_GCM_256' == encryption_agent.encryption_algorithm

        encrypted_region_info = encryption_data.encrypted_region_info
        assert _GCM_NONCE_LENGTH == encrypted_region_info.nonce_length
        assert _GCM_TAG_LENGTH == encrypted_region_info.tag_length

        content_encryption_key = _validate_and_unwrap_cek(encryption_data, kek, None)

        nonce_length = encrypted_region_info.nonce_length

        message = message['EncryptedMessageContents']
        message = _decode_base64_to_bytes(message)

        # First bytes are the nonce
        nonce = message[:nonce_length]
        ciphertext_with_tag = message[nonce_length:]

        aesgcm = AESGCM(content_encryption_key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        decrypted_data = decrypted_data.decode(encoding='utf-8')

        # Assert
        assert content == decrypted_data

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_encryption_user_agent(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        app_id = 'TestAppId'
        content = 'Hello World Encrypted!'
        kek = KeyWrapper('key1')

        def assert_user_agent(request):
            start = f'{app_id} azstorage-clientsideencryption/2.0 '
            assert request.http_request.headers['User-Agent'].startswith(start)

        # Test method level keyword
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)
        queue = await self._create_queue(qsc)
        await queue.send_message(content, raw_request_hook=assert_user_agent, user_agent=app_id)

        # Test client constructor level keyword
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek,
            user_agent=app_id)

        queue = self._get_queue_reference(qsc)
        await queue.send_message(content, raw_request_hook=assert_user_agent)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
