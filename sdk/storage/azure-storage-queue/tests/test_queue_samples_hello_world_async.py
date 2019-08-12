# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio

try:
    import settings_real as settings
except ImportError:
    import queue_settings_fake as settings
from multidict import CIMultiDict, CIMultiDictProxy
from queuetestcase import (
    QueueTestCase,
    record,
    TestMode
)



class TestQueueHelloWorldSamplesAsync(QueueTestCase):

    connection_string = settings.CONNECTION_STRING

    async def _test_create_client_with_connection_string(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = await queue_service.get_service_properties()

        assert properties is not None

    def test_create_client_with_connection_string(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_client_with_connection_string())

    async def _test_queue_and_messages_example(self):
        # Instantiate the QueueClient from a connection string
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myasyncqueue")

        # Create the queue
        # [START async_create_queue]
        await queue.create_queue()
        # [END async_create_queue]

        try:
            # Enqueue messages
            await asyncio.gather(
                queue.enqueue_message(u"I'm using queues!"),
                queue.enqueue_message(u"This is my second message"))

            # Receive the messages
            response = queue.receive_messages(messages_per_page=2)

            # Print the content of the messages
            async for message in response:
                print(message.content)

        finally:
            # [START async_delete_queue]
            await queue.delete_queue()
            # [END async_delete_queue]

    def test_queue_and_messages_example(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_queue_and_messages_example())