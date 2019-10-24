# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from multidict import CIMultiDict, CIMultiDictProxy
from asyncqueuetestcase import (
    AsyncQueueTestCase
)



class TestQueueHelloWorldSamplesAsync(AsyncQueueTestCase):

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_create_client_with_connection_string(self, resource_group, location, storage_account, storage_account_key):
        conn_str = self.connection_string(storage_account, storage_account_key)
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str)

        # Get queue service properties
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_queue_and_messages_example(self, resource_group, location, storage_account, storage_account_key):
        conn_str = self.connection_string(storage_account, storage_account_key)
        # Instantiate the QueueClient from a connection string
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(conn_str, "myasyncqueue")

        # Create the queue
        # [START async_create_queue]
        await queue.create_queue()
        # [END async_create_queue]

        try:
            # Send messages
            await asyncio.gather(
                queue.send_message(u"I'm using queues!"),
                queue.send_message(u"This is my second message"))

            # Receive the messages
            response = queue.receive_messages(messages_per_page=2)

            # Print the content of the messages
            async for message in response:
                print(message.content)

        finally:
            # [START async_delete_queue]
            await queue.delete_queue()
            # [END async_delete_queue]
