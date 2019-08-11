# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from azure.core.exceptions import ResourceExistsError
import asyncio
try:
    import settings_real as settings
except ImportError:
    import queue_settings_fake as settings

from queuetestcase import (
    QueueTestCase,
    record,
    TestMode
)


class TestMessageQueueSamples(QueueTestCase):

    connection_string = settings.CONNECTION_STRING
    storage_url = "{}://{}.queue.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    async def _test_set_access_policy(self):

        # [START async_create_queue_client_from_connection_string]
        from azure.storage.queue.aio import QueueClient
        queue_client = QueueClient.from_connection_string(self.connection_string, "asyncqueuetest")
        # [END async_create_queue_client_from_connection_string]

        # Create the queue
        try:
            await queue_client.create_queue()
        except ResourceExistsError:
            pass
        await queue_client.enqueue_message(u"hello world")

        try:
            # [START async_set_access_policy]
            # Create an access policy
            from azure.storage.queue.aio import AccessPolicy, QueuePermissions
            access_policy = AccessPolicy()
            access_policy.start = datetime.utcnow() - timedelta(hours=1)
            access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
            access_policy.permission = QueuePermissions.READ
            identifiers = {'my-access-policy-id': access_policy}

            # Set the access policy
            await queue_client.set_queue_access_policy(identifiers)
            # [END async_set_access_policy]

            # Use the access policy to generate a SAS token
            sas_token = queue_client.generate_shared_access_signature(
                policy_id='my-access-policy-id'
            )
            # [END async_set_access_policy]

            # Authenticate with the sas token
            # [START async_create_queue_client]
            from azure.storage.queue.aio import QueueClient
            q = QueueClient(
                queue_url=queue_client.url,
                credential=sas_token
            )
            # [END async_create_queue_client]

            # Use the newly authenticated client to receive messages
            my_messages = q.receive_messages()

        finally:
            # Delete the queue
            await queue_client.delete_queue()

    def test_set_access_policy(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_policy())

    async def _test_queue_metadata(self):

        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "asyncmetaqueue")

        # Create the queue
        await queue.create_queue()

        try:
            # [START async_set_queue_metadata]
            metadata = {'foo': 'val1', 'bar': 'val2', 'baz': 'val3'}
            await queue.set_queue_metadata(metadata=metadata)
            # [END async_set_queue_metadata]

            # [START async_get_queue_properties]
            response = await queue.get_queue_properties()
            # [END async_get_queue_properties]
            assert response.metadata == metadata

        finally:
            # Delete the queue
            await queue.delete_queue()

    def test_queue_metadata(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_queue_metadata())

    async def _test_enqueue_and_receive_messages(self):

        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "asyncmessagequeue")

        # Create the queue
        await queue.create_queue()

        try:
            # [START async_enqueue_messages]
            await asyncio.gather(
                queue.enqueue_message(u"message1"),
                queue.enqueue_message(u"message2", visibility_timeout=30),  # wait 30s before becoming visible
                queue.enqueue_message(u"message3"),
                queue.enqueue_message(u"message4"),
                queue.enqueue_message(u"message5"))
            # [END async_enqueue_messages]

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

    def test_enqueue_and_receive_messages(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_enqueue_and_receive_messages())

    async def _test_delete_and_clear_messages(self):

        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "asyncdelqueue")

        # Create the queue
        await queue.create_queue()

        try:
            # Enqueue messages
            await asyncio.gather(
                queue.enqueue_message(u"message1"),
                queue.enqueue_message(u"message2"),
                queue.enqueue_message(u"message3"),
                queue.enqueue_message(u"message4"),
                queue.enqueue_message(u"message5"))

            # [START async_delete_message]
            # Get the message at the front of the queue
            messages = queue.receive_messages()
            async for msg in messages:

                # Delete the specified message
                await queue.delete_message(msg)
            # [END async_delete_message]

            # [START async_clear_messages]
            await queue.clear_messages()
            # [END async_clear_messages]

        finally:
            # Delete the queue
            await queue.delete_queue()

    def test_delete_and_clear_messages(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_and_clear_messages())

    async def _test_peek_messages(self):
        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "asyncpeekqueue")

        # Create the queue
        await queue.create_queue()

        try:
            # Enqueue messages
            await asyncio.gather(
                queue.enqueue_message(u"message1"),
                queue.enqueue_message(u"message2"),
                queue.enqueue_message(u"message3"),
                queue.enqueue_message(u"message4"),
                queue.enqueue_message(u"message5"))

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

    def test_peek_messages(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_peek_messages())

    async def _test_update_message(self):

        # Instantiate a queue client
        from azure.storage.queue.aio import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "asyncupdatequeue")

        # Create the queue
        await queue.create_queue()

        try:
            # [START async_update_message]
            # Enqueue a message
            await queue.enqueue_message(u"update me")

            # Receive the message
            messages = queue.receive_messages()

            # Update the message
            async for message in messages:
                message = await queue.update_message(
                    message,
                    visibility_timeout=0,
                    content=u"updated")
            # [END update_message]
                assert message.content == "updated"
                break

        finally:
            # Delete the queue
            await queue.delete_queue()

    def test_update_message(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_message())
