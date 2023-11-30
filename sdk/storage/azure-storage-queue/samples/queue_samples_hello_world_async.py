# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: queue_samples_hello_world_async.py

DESCRIPTION:
    These samples demonstrate common scenarios like instantiating a client,
    creating a queue, and sending and receiving messages.

USAGE:
    python queue_samples_hello_world_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""


import asyncio
import os
import sys


class QueueHelloWorldSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    async def create_client_with_connection_string_async(self):
        if self.connection_string is None:
            print("Missing required environment variable(s). Please see specific test for more details." + '\n' +
                  "Test: create_client_with_connection_string_async")
            sys.exit(1)

        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # Get queue service properties
        async with queue_service:
            properties = await queue_service.get_service_properties()

    async def queue_and_messages_example_async(self):
        if self.connection_string is None:
            print("Missing required environment variable(s). Please see specific test for more details." + '\n' +
                  "Test: queue_and_messages_example_async")
            sys.exit(1)

        # Instantiate the QueueClient from a connection string
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(conn_str=self.connection_string, queue_name="myqueue")

        async with queue:
            # Create the queue
            # [START async_create_queue]
            await queue.create_queue()
            # [END async_create_queue]

            try:
                # Send messages
                await asyncio.gather(
                    queue.send_message("I'm using queues!"),
                    queue.send_message("This is my second message")
                )

                # Receive the messages
                response = queue.receive_messages(messages_per_page=2)

                # Print the content of the messages
                async for message in response:
                    print(message.content)

            finally:
                # [START async_delete_queue]
                await queue.delete_queue()
                # [END async_delete_queue]


async def main():
    sample = QueueHelloWorldSamplesAsync()
    await sample.create_client_with_connection_string_async()
    await sample.queue_and_messages_example_async()

if __name__ == '__main__':
    asyncio.run(main())
