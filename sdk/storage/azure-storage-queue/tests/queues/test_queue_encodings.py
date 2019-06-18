# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.common import (
    AzureHttpError,
    AzureException,
)

from azure.storage.queue.queue_client import QueueClient
from azure.storage.queue.queue_service_client import QueueServiceClient
from tests.testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'


# ------------------------------------------------------------------------------

class StorageQueueEncodingTest(StorageTestCase):
    def setUp(self):
        super(StorageQueueEncodingTest, self).setUp()

        self.qs = self._create_storage_service(QueueClient, self.settings)
        self.test_queues = []

    def tearDown(self):
        if not self.is_playback():
            for queue_name in self.test_queues:
                try:
                    self.qs.delete_queue(queue_name)
                except:
                    pass
        return super(StorageQueueEncodingTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self):
        queue_name = self.get_resource_name(TEST_QUEUE_PREFIX + str(len(self.test_queues)))
        self.test_queues.append(queue_name)
        return queue_name

    def _create_queue(self):
        queue_name = self._get_queue_reference()
        self.qs.create_queue(queue_name)
        return queue_name

    def _validate_encoding(self, qs, message):
        # Arrange
        queue_name = self._create_queue()

        # Action.
        qs.put_message(queue_name, message)

        # Asserts
        messages = qs.get_messages(queue_name)
        self.assertEqual(message, messages[0].content)

    # --------------------------------------------------------------------------

    @record
    def test_message_text_xml(self):
        # Arrange.
        message = u'<message1>'

        # Asserts
        self._validate_encoding(self.qs, message)

    @record
    def test_message_text_xml_whitespace(self):
        # Arrange.
        message = u'  mess\t age1\n'

        # Asserts
        self._validate_encoding(self.qs, message)

    @record
    def test_message_text_xml_invalid_chars(self):
        # Action.
        queue_name = self._get_queue_reference()
        message = u'\u0001'

        # Asserts
        with self.assertRaises(AzureHttpError):
            self.qs.put_message(queue_name, message)

    @record
    def test_message_text_base64(self):
        # Arrange.
        qs2 = self._create_storage_service(QueueService, self.settings)
        qs2.encode_function = QueueMessageFormat.text_base64encode
        qs2.decode_function = QueueMessageFormat.text_base64decode
        message = u'\u0001'

        # Asserts
        self._validate_encoding(qs2, message)

    @record
    def test_message_bytes_base64(self):
        # Arrange.
        qs2 = self._create_storage_service(QueueService, self.settings)
        qs2.encode_function = QueueMessageFormat.binary_base64encode
        qs2.decode_function = QueueMessageFormat.binary_base64decode
        message = b'xyz'

        # Asserts
        self._validate_encoding(qs2, message)

    @record
    def test_message_bytes_fails(self):
        # Arrange
        queue_name = self._get_queue_reference()

        # Action.
        try:
            message = b'xyz'
            self.qs.put_message(queue_name, message)
            self.fail('Passing binary to text encoder should fail.')
        except TypeError as e:
            self.assertTrue(str(e).startswith('message should be of type'))

            # Asserts

    @record
    def test_message_text_fails(self):
        # Arrange
        qs2 = self._create_storage_service(QueueService, self.settings)
        qs2.encode_function = QueueMessageFormat.binary_base64encode
        qs2.decode_function = QueueMessageFormat.binary_base64decode

        queue_name = self._get_queue_reference()

        # Action.
        try:
            message = u'xyz'
            qs2.put_message(queue_name, message)
            self.fail('Passing text to binary encoder should fail.')
        except TypeError as e:
            self.assertEqual(str(e), 'message should be of type bytes.')

            # Asserts

    @record
    def test_message_base64_decode_fails(self):
        # Arrange
        qs2 = self._create_storage_service(QueueService, self.settings)
        qs2.encode_function = QueueMessageFormat.text_xmlencode
        qs2.decode_function = QueueMessageFormat.binary_base64decode

        queue_name = self._create_queue()
        message = u'xyz'
        qs2.put_message(queue_name, message)

        # Action.
        try:
            qs2.peek_messages(queue_name)
            self.fail('Decoding unicode string as base64 should fail.')
        except AzureException as e:
            self.assertNotEqual(-1, str(e).find('message is not a valid base64 value.'))

            # Asserts


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
