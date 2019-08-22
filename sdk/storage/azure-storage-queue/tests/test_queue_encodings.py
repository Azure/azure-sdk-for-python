# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.exceptions import HttpResponseError, DecodeError, ResourceExistsError
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.queue import (
    QueueClient,
    QueueServiceClient,
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
    TextXMLEncodePolicy,
    TextXMLDecodePolicy,
    NoEncodePolicy,
    NoDecodePolicy)

from queuetestcase import (
    QueueTestCase
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'


# ------------------------------------------------------------------------------

class StorageQueueEncodingTest(QueueTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name)
        return queue

    def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue = self._get_queue_reference(qsc, prefix)
        try:
            created = queue.create_queue()
        except ResourceExistsError:
            pass
        return queue

    def _validate_encoding(self, queue, message):
        # Arrange
        try:
            created = queue.create_queue()
        except ResourceExistsError:
            pass

        # Action.
        queue.enqueue_message(message)

        # Asserts
        dequeued = next(queue.receive_messages())
        self.assertEqual(message, dequeued.content)

    # --------------------------------------------------------------------------

    @ResourceGroupPreparer()              
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_text_xml(self, resource_group, location, storage_account, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        message = u'<message1>'
        queue = qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        self._validate_encoding(queue, message)

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_text_xml_whitespace(self, resource_group, location, storage_account, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        message = u'  mess\t age1\n'
        queue = qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        self._validate_encoding(queue, message)

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_text_xml_invalid_chars(self, resource_group, location, storage_account, storage_account_key):
        # Action.
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        queue = self._get_queue_reference(qsc)
        message = u'\u0001'

        # Asserts
        with self.assertRaises(HttpResponseError):
            queue.enqueue_message(message)

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_text_base64(self, resource_group, location, storage_account, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        queue = QueueClient(
            queue_url=self._account_url(storage_account.name),
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=TextBase64EncodePolicy(),
            message_decode_policy=TextBase64DecodePolicy())

        message = u'\u0001'

        # Asserts
        self._validate_encoding(queue, message)

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_bytes_base64(self, resource_group, location, storage_account, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        queue = QueueClient(
            queue_url=self._account_url(storage_account.name),
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())

        message = b'xyz'

        # Asserts
        self._validate_encoding(queue, message)

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_bytes_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        queue = self._get_queue_reference(qsc)

        # Action.
        with self.assertRaises(TypeError) as e:
            message = b'xyz'
            queue.enqueue_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be text'))

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_text_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        queue = QueueClient(
            queue_url=self._account_url(storage_account.name),
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())

        # Action.
        with self.assertRaises(TypeError) as e:
            message = u'xyz'
            queue.enqueue_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be bytes'))

    @ResourceGroupPreparer()          
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_message_base64_decode_fails(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        queue = QueueClient(
            queue_url=self._account_url(storage_account.name),
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=TextXMLEncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())
        try:
            queue.create_queue()
        except ResourceExistsError:
            pass
        message = u'xyz'
        queue.enqueue_message(message)

        # Action.
        with self.assertRaises(DecodeError) as e:
            queue.peek_messages()

        # Asserts
        self.assertNotEqual(-1, str(e.exception).find('Message content is not valid base 64'))


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
