# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.exceptions import HttpResponseError, DecodeError, ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.storage.queue import (
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy
)

from azure.storage.queue.aio import (
    QueueClient,
    QueueServiceClient
)

from devtools_testutils.storage.aio import AsyncStorageTestCase
from settings.testcase import QueuePreparer

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'

# ------------------------------------------------------------------------------

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageQueueEncodingTestAsync(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name)
        return queue

    async def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue = self._get_queue_reference(qsc, prefix)
        try:
            created = await queue.create_queue()
        except ResourceExistsError:
            pass
        return queue

    async def _validate_encoding(self, queue, message):
        # Arrange
        try:
            created = await queue.create_queue()
        except ResourceExistsError:
            pass

        # Action.
        await queue.send_message(message)

        # Asserts
        dequeued = None
        async for m in queue.receive_messages():
            dequeued = m
        self.assertEqual(message, dequeued.content)

    # --------------------------------------------------------------------------
    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_text_xml(self, storage_account_name, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        message = u'<message1>'
        queue = qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_text_xml_whitespace(self, storage_account_name, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        message = u'  mess\t age1\n'
        queue = qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_text_xml_invalid_chars(self, storage_account_name, storage_account_key):
        # Action.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = self._get_queue_reference(qsc)
        message = u'\u0001'

        # Asserts
        with self.assertRaises(HttpResponseError):
            await queue.send_message(message)

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_text_base64(self, storage_account_name, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=TextBase64EncodePolicy(),
            message_decode_policy=TextBase64DecodePolicy(),
            transport=AiohttpTestTransport())

        message = '\u0001'

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_bytes_base64(self, storage_account_name, storage_account_key):
        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy(),
            transport=AiohttpTestTransport())

        message = b'xyz'

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_bytes_fails(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = self._get_queue_reference(qsc)
        # Action.
        with self.assertRaises(TypeError) as e:
            message = b'xyz'
            await queue.send_message(message)

            # Asserts
            self.assertTrue(str(e.exception).startswith('Message content must not be bytes. Use the BinaryBase64EncodePolicy to send bytes.'))

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_text_fails(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy(),
            transport=AiohttpTestTransport())

        # Action.
        with self.assertRaises(TypeError) as e:
            message = u'xyz'
            await queue.send_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be bytes'))

    @QueuePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_message_base64_decode_fails(self, storage_account_name, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=None,
            message_decode_policy=BinaryBase64DecodePolicy(),
            transport=AiohttpTestTransport())
        try:
            await queue.create_queue()
        except ResourceExistsError:
            pass
        message = u'xyz'
        await queue.send_message(message)

        # Action.
        with self.assertRaises(DecodeError) as e:
            await queue.peek_messages()

        # Asserts
        self.assertNotEqual(-1, str(e.exception).find('Message content is not valid base 64'))

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
