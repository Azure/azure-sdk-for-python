# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio

from azure.core.exceptions import HttpResponseError, DecodeError, ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.storage.queue import (
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
    TextXMLEncodePolicy,
    TextXMLDecodePolicy,
    NoEncodePolicy,
    NoDecodePolicy
)

from azure.storage.queue.aio import (
    QueueClient,
    QueueServiceClient
)

from queuetestcase import (
    QueueTestCase,
    record,
    TestMode
)

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


class StorageQueueEncodingTestAsync(QueueTestCase):
    def setUp(self):
        super(StorageQueueEncodingTestAsync, self).setUp()

        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        self.qsc = QueueServiceClient(account_url=queue_url, credential=credentials, transport=AiohttpTestTransport())
        self.test_queues = []

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            for queue in self.test_queues:
                try:
                    loop.run_until_complete(self.qsc.delete_queue(queue.queue_name))
                except:
                    pass
        return super(StorageQueueEncodingTestAsync, self).tearDown()

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

    async def _validate_encoding(self, queue, message):
        # Arrange
        try:
            created = await queue.create_queue()
        except ResourceExistsError:
            pass

        # Action.
        await queue.enqueue_message(message)

        # Asserts
        dequeued = None
        async for m in queue.receive_messages():
            dequeued = m
        self.assertEqual(message, dequeued.content)

    # --------------------------------------------------------------------------

    async def _test_message_text_xml(self):
        # Arrange.
        message = u'<message1>'
        queue = self.qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        await self._validate_encoding(queue, message)

    @record
    def test_message_text_xml(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_text_xml())

    async def _test_message_text_xml_whitespace(self):
        # Arrange.
        message = u'  mess\t age1\n'
        queue = self.qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        await self._validate_encoding(queue, message)

    @record
    def test_message_text_xml_whitespace(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_text_xml_whitespace())

    async def _test_message_text_xml_invalid_chars(self):
        # Action.
        queue = self._get_queue_reference()
        message = u'\u0001'

        # Asserts
        with self.assertRaises(HttpResponseError):
            await queue.enqueue_message(message)

    @record
    def test_message_text_xml_invalid_chars(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_text_xml_invalid_chars())

    async def _test_message_text_base64(self):
        # Arrange.
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=TextBase64EncodePolicy(),
            message_decode_policy=TextBase64DecodePolicy(),
            transport=AiohttpTestTransport())

        message = '\u0001'

        # Asserts
        await self._validate_encoding(queue, message)

    @record
    def test_message_text_base64(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_text_base64())

    async def _test_message_bytes_base64(self):
        # Arrange.
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy(),
            transport=AiohttpTestTransport())

        message = b'xyz'

        # Asserts
        await self._validate_encoding(queue, message)

    @record
    def test_message_bytes_base64(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_bytes_base64())

    async def _test_message_bytes_fails(self):
        # Arrange
        queue = self._get_queue_reference()

        # Action.
        with self.assertRaises(TypeError) as e:
            message = b'xyz'
            await queue.enqueue_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be text'))

    @record
    def test_message_bytes_fails(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_bytes_fails())

    async def _test_message_text_fails(self):
        # Arrange
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy(),
            transport=AiohttpTestTransport())

        # Action.
        with self.assertRaises(TypeError) as e:
            message = u'xyz'
            await queue.enqueue_message(message)

        # Asserts
        self.assertTrue(str(e.exception).startswith('Message content must be bytes'))

    @record
    def test_message_text_fails(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_text_fails())

    async def _test_message_base64_decode_fails(self):
        # Arrange
        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        queue = QueueClient(
            queue_url=queue_url,
            queue=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=credentials,
            message_encode_policy=TextXMLEncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy(),
            transport=AiohttpTestTransport())
        try:
            await queue.create_queue()
        except ResourceExistsError:
            pass
        message = u'xyz'
        await queue.enqueue_message(message)

        # Action.
        with self.assertRaises(DecodeError) as e:
            await queue.peek_messages()

        # Asserts
        self.assertNotEqual(-1, str(e.exception).find('Message content is not valid base 64'))

    @record
    def test_message_base64_decode_fails(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_message_base64_decode_fails())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
