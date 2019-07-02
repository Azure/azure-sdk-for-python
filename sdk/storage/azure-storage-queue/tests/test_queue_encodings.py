# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.exceptions import HttpResponseError, DecodeError, ResourceExistsError
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
    QueueTestCase,
    record,
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'


# ------------------------------------------------------------------------------

class StorageQueueEncodingTest(QueueTestCase):
    def setUp(self):
        super(StorageQueueEncodingTest, self).setUp()

        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        self.qsc = QueueServiceClient(account_url=queue_url, credential=credentials)
        self.test_queues = []

    def tearDown(self):
        if not self.is_playback():
            for queue in self.test_queues:
                try:
                    self.qsc.delete_queue(queue.queue_name)
                except:
                    pass
        return super(StorageQueueEncodingTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = self.qsc.get_queue_client(queue_name)
        self.test_queues.append(queue)
        return queue

    def _create_queue(self, prefix=TEST_QUEUE_PREFIX):
        queue = self._get_queue_reference(prefix)
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

    @record
    def test_message_text_xml(self):
        # Arrange.
        message = u'<message1>'
        queue = self.qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        self._validate_encoding(queue, message)

    @record
    def test_message_text_xml_whitespace(self):
        # Arrange.
        message = u'  mess\t age1\n'
        queue = self.qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        self._validate_encoding(queue, message)

    @record
    def test_message_text_xml_invalid_chars(self):
        # Action.
        queue = self._get_queue_reference()
        message = u'\u0001'

        # Asserts
        with self.assertRaises(HttpResponseError):
            queue.enqueue_message(message)

    @record
    def test_message_text_base64(self):
        # Arrange.
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=TextBase64EncodePolicy(),
            message_decode_policy=TextBase64DecodePolicy())

        message = u'\u0001'

        # Asserts
        self._validate_encoding(queue, message)

    @record
    def test_message_bytes_base64(self):
        # Arrange.
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())

        message = b'xyz'

        # Asserts
        self._validate_encoding(queue, message)

    @record
    def test_message_bytes_fails(self):
        # Arrange
        queue = self._get_queue_reference()

        # Action.
        with self.assertRaises(TypeError) as e:
            message = b'xyz'
            queue.enqueue_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be text'))

    @record
    def test_message_text_fails(self):
        # Arrange
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())

        # Action.
        with self.assertRaises(TypeError) as e:
            message = u'xyz'
            queue.enqueue_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be bytes'))

    @record
    def test_message_base64_decode_fails(self):
        # Arrange
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
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
