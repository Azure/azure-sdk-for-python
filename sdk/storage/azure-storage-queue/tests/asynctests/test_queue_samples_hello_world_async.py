# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

try:
    import settings_real as settings
except ImportError:
    import queue_settings_fake as settings

from queuetestcase import (
    QueueTestCase,
    record
)


class TestQueueHelloWorldSamples(QueueTestCase):

    connection_string = settings.CONNECTION_STRING

    @record
    @pytest.mark.asyncio
    async def test_create_client_with_connection_string(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @record
    @pytest.mark.asyncio
    async def test_queue_and_messages_example(self):
        # Instantiate the QueueClient from a connection string
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue")

        # Create the queue
        # [START create_queue]
        await queue.create_queue()
        # [END create_queue]

        try:
            # Enqueue messages
            await queue.enqueue_message(u"I'm using queues!")
            await queue.enqueue_message(u"This is my second message")

            # Receive the messages
            response = await queue.receive_messages(messages_per_page=2)

            # Print the content of the messages
            for message in response:
                print(message.content)

        finally:
            # [START delete_queue]
            await queue.delete_queue()
            # [END delete_queue]
