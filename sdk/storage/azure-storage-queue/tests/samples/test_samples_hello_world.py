# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    record
)


class TestHelloWorldSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING

    @record
    def test_create_client_with_connection_string(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = queue_service.get_service_properties()

        assert properties is not None

    @record
    def test_queue_and_messages_example(self):
        # Instantiate the QueueClient from a connection string
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue")

        # Create the queue
        queue.create_queue()

        # Enqueue messages
        queue.enqueue_message("I'm using queues!")
        queue.enqueue_message("This is my second message")

        # Dequeue the messages
        response = next(queue.dequeue_messages(num_messages=2))

        # Print the content of the messages
        for message in response:
            print(message.content)

        # Delete the queue
        queue.delete_queue()
