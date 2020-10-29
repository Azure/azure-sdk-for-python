# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: queue_samples_message_async.py

DESCRIPTION:
    These samples demonstrate the following: creating and setting an access policy to generate a
    sas token, getting a queue client from a queue URL, setting and getting queue
    metadata, sending messages and receiving them individually or by batch, deleting and
    clearing all messages, and peeking and updating messages.

USAGE:
    python queue_samples_message_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

from datetime import datetime, timedelta
import asyncio
import os


class QueueMessageSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    async def set_access_policy_async(self):
        # [START async_create_queue_client_from_connection_string]
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue1")
        # [END async_create_queue_client_from_connection_string]

        # Create the queue
        async with queue:
            await queue.create_queue()

            # Send a message
            await queue.send_message(u"hello world")

            try:
                # [START async_set_access_policy]
                # Create an access policy
                from azure.storage.queue import AccessPolicy, QueueSasPermissions
                access_policy = AccessPolicy()
                access_policy.start = datetime.utcnow() - timedelta(hours=1)
                access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
                access_policy.permission = QueueSasPermissions(read=True)
                identifiers = {'my-access-policy-id': access_policy}

                # Set the access policy
                await queue.set_queue_access_policy(identifiers)
                # [END async_set_access_policy]

                # Use the access policy to generate a SAS token
                from azure.storage.queue import generate_queue_sas
                sas_token = generate_queue_sas(
                    queue.account_name,
                    queue.queue_name,
                    queue.credential.account_key,
                    policy_id='my-access-policy-id'
                )

                # Authenticate with the sas token
                # [START async_create_queue_client]
                token_auth_queue = QueueClient.from_queue_url(
                    queue_url=queue.url,
                    credential=sas_token
                )
                # [END async_create_queue_client]

                # Use the newly authenticated client to receive messages
                my_messages = token_auth_queue.receive_messages()

            finally:
                # Delete the queue
                await queue.delete_queue()

    async def queue_metadata_async(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue2")

        # Create the queue
        async with queue:
            await queue.create_queue()

            try:
                # [START async_set_queue_metadata]
                metadata = {'foo': 'val1', 'bar': 'val2', 'baz': 'val3'}
                await queue.set_queue_metadata(metadata=metadata)
                # [END async_set_queue_metadata]

                # [START async_get_queue_properties]
                properties = await queue.get_queue_properties()
                # [END async_get_queue_properties]

            finally:
                # Delete the queue
                await queue.delete_queue()

    async def send_and_receive_messages_async(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue3")

        # Create the queue
        async with queue:
            await queue.create_queue()

            try:
                # [START async_send_messages]
                await asyncio.gather(
                    queue.send_message(u"message1"),
                    queue.send_message(u"message2", visibility_timeout=30),  # wait 30s before becoming visible
                    queue.send_message(u"message3"),
                    queue.send_message(u"message4"),
                    queue.send_message(u"message5")
                )
                # [END async_send_messages]

                # [START async_receive_messages]
                # Receive messages one-by-one
                messages = queue.receive_messages()
                async for msg in messages:
                    print(msg.content)

                # Receive messages by batch
                messages = queue.receive_messages(messages_per_page=5)
                async for msg_batch in messages.by_page():
                    for msg in msg_batch:
                        print(msg.content)
                        await queue.delete_message(msg)
                # [END async_receive_messages]

                # Only prints 4 messages because message 2 is not visible yet
                # >>message1
                # >>message3
                # >>message4
                # >>message5

            finally:
                # Delete the queue
                await queue.delete_queue()

    async def receive_one_message_from_queue(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue3")

        # Create the queue
        async with queue:
            await queue.create_queue()

            try:
                await asyncio.gather(
                    queue.send_message(u"message1"),
                    queue.send_message(u"message2"),
                    queue.send_message(u"message3"))

                # [START receive_one_message]
                # Pop two messages from the front of the queue
                message1 = await queue.receive_message()
                message2 = await queue.receive_message()
                # We should see message 3 if we peek
                message3 = await queue.peek_messages()

                print(message1.content)
                print(message2.content)
                print(message3[0].content)
                # [END receive_one_message]

            finally:
                await queue.delete_queue()

    async def delete_and_clear_messages_async(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue4")

        # Create the queue
        async with queue:
            await queue.create_queue()

            try:
                # Send messages
                await asyncio.gather(
                    queue.send_message(u"message1"),
                    queue.send_message(u"message2"),
                    queue.send_message(u"message3"),
                    queue.send_message(u"message4"),
                    queue.send_message(u"message5")
                )

                # [START async_delete_message]
                # Get the message at the front of the queue
                messages = queue.receive_messages()
                async for msg in messages:
                    # Delete the specified message
                    await queue.delete_message(msg)
                # [END async_delete_message]
                    break

                # [START async_clear_messages]
                await queue.clear_messages()
                # [END async_clear_messages]

            finally:
                # Delete the queue
                await queue.delete_queue()

    async def peek_messages_async(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue5")

        # Create the queue
        async with queue:
            await queue.create_queue()

            try:
                # Send messages
                await asyncio.gather(
                    queue.send_message(u"message1"),
                    queue.send_message(u"message2"),
                    queue.send_message(u"message3"),
                    queue.send_message(u"message4"),
                    queue.send_message(u"message5")
                )

                # [START async_peek_message]
                # Peek at one message at the front of the queue
                msg = await queue.peek_messages()

                # Peek at the last 5 messages
                messages = await queue.peek_messages(max_messages=5)

                # Print the last 5 messages
                for message in messages:
                    print(message.content)
                # [END async_peek_message]

            finally:
                # Delete the queue
                await queue.delete_queue()

    async def update_message_async(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue6")

        # Create the queue
        async with queue:
            await queue.create_queue()

            try:
                # [START async_update_message]
                # Send a message
                await queue.send_message(u"update me")

                # Receive the message
                messages = queue.receive_messages()

                # Update the message
                async for message in messages:
                    message = await queue.update_message(
                        message,
                        visibility_timeout=0,
                        content=u"updated")
                # [END async_update_message]
                    break

            finally:
                # Delete the queue
                await queue.delete_queue()


async def main():
    sample = QueueMessageSamplesAsync()
    await sample.set_access_policy_async()
    await sample.queue_metadata_async()
    await sample.send_and_receive_messages_async()
    await sample.receive_one_message_from_queue()
    await sample.delete_and_clear_messages_async()
    await sample.peek_messages_async()
    await sample.update_message_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
