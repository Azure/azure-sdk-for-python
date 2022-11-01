# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import pytest
from azure.core.exceptions import DecodeError, HttpResponseError, ResourceExistsError
from azure.storage.queue import BinaryBase64DecodePolicy, BinaryBase64EncodePolicy, TextBase64DecodePolicy, TextBase64EncodePolicy
from azure.storage.queue.aio import QueueClient, QueueServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import QueuePreparer

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'

# ------------------------------------------------------------------------------


class TestAsyncStorageQueueEncoding(AsyncStorageRecordedTestCase):
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
        assert message == dequeued.content

    # --------------------------------------------------------------------------
    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_text_xml(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        message = '<message1>'
        queue = qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_text_xml_whitespace(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        message = '  mess\t age1\n'
        queue = qsc.get_queue_client(self.get_resource_name(TEST_QUEUE_PREFIX))

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_text_xml_invalid_chars(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._get_queue_reference(qsc)
        message = '\u0001'

        # Asserts
        with pytest.raises(HttpResponseError):
            await queue.send_message(message)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_text_base64(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=TextBase64EncodePolicy(),
            message_decode_policy=TextBase64DecodePolicy())

        message = '\u0001'

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_bytes_base64(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange.
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key)
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())

        message = b'xyz'

        # Asserts
        await self._validate_encoding(queue, message)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_bytes_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = await self._create_queue(qsc)
        # Action.
        with pytest.raises(TypeError) as e:
            message = b'xyz'
            await queue.send_message(message)

            # Asserts
            assert str(e.exception.startswith(
                'Message content must not be bytes. '
                'Use the BinaryBase64EncodePolicy to send bytes.'))

    @QueuePreparer()
    async def test_message_text_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=BinaryBase64EncodePolicy(),
            message_decode_policy=BinaryBase64DecodePolicy())

        # Action.
        with pytest.raises(TypeError) as e:
            message = 'xyz'
            await queue.send_message(message)

        # Asserts
        assert str(e.value).startswith('Message content must be bytes')

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_message_base64_decode_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = QueueClient(
            account_url=self.account_url(storage_account_name, "queue"),
            queue_name=self.get_resource_name(TEST_QUEUE_PREFIX),
            credential=storage_account_key,
            message_encode_policy=None,
            message_decode_policy=BinaryBase64DecodePolicy())
        try:
            await queue.create_queue()
        except ResourceExistsError:
            pass
        message = 'xyz'
        await queue.send_message(message)

        # Action.
        with pytest.raises(DecodeError) as e:
            await queue.peek_messages()

        # Asserts
        assert -1 != str(e.value).find('Message content is not valid base 64')

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
