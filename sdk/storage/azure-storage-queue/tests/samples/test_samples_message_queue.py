# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    record,
    TestMode
)


class TestMessageQueueSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING
    storage_url = "{}://{}.queue.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    def test_set_access_policy(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Create an access policy
        from azure.storage.queue import AccessPolicy, QueuePermissions
        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = QueuePermissions.READ
        identifiers = {'my-access-policy-id': access_policy}

        # Create the queue client and set the access policy
        from azure.storage.queue import QueueClient, QueueServiceClient
        queue_client = QueueClient.from_connection_string(self.connection_string, "queuetest")

        # Create the queue
        queue_client.create_queue()
        queue_client.enqueue_message('hello world')

        # Set the access policy
        queue_client.set_queue_access_policy(identifiers)

        # Use the access policy to generate a SAS token
        sas_token = queue_client.generate_shared_access_signature(
            policy_id='my-access-policy-id'
        )

        # Authenticate with the sas token
        q = QueueClient(
            queue_url=queue_client.url,
            credential=sas_token
        )

        # Use the newly authenticated client to dequeue messages
        my_message = q.dequeue_messages()
        assert my_message is not None

        # Delete the queue
        queue_client.delete_queue()

    @record
    def test_queue_metadata(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "metaqueue")

        # Create the queue
        queue.create_queue()

        # Set the queue metadata
        metadata = {'foo': 'val1', 'bar': 'val2', 'baz': 'val3'}
        queue.set_queue_metadata(metadata=metadata)

        # Get the queue metadata
        response = queue.get_queue_properties().metadata

        assert response == metadata

        # Delete the queue
        queue.delete_queue()

    @record
    def test_enqueue_and_dequeue_messages(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "messagequeue")

        # Create the queue
        queue.create_queue()

        # Enqueue messages
        queue.enqueue_message("message1")
        queue.enqueue_message("message2", visibility_timeout=30)  # wait 30s before becoming visible
        queue.enqueue_message("message3")
        queue.enqueue_message("message4")
        queue.enqueue_message("message5")

        # Dequeue one message from the front of the queue
        one_msg = queue.dequeue_messages()

        # Dequeue the last 5 messages
        messages = next(queue.dequeue_messages(num_messages=5))

        # Print the messages
        for msg in messages:
            print(msg.content)

        # Only prints 4 messages because message 2 is not visible yet
        # >>message1
        # >>message3
        # >>message4
        # >>message5

        # Delete the queue
        queue.delete_queue()

    @record
    def test_delete_and_clear_messages(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "delqueue")

        # Create the queue
        queue.create_queue()

        # Enqueue messages
        queue.enqueue_message("message1")
        queue.enqueue_message("message2")
        queue.enqueue_message("message3")
        queue.enqueue_message("message4")
        queue.enqueue_message("message5")

        # Get the message at the front of the queue
        msg = next(queue.dequeue_messages())

        # Delete the specified message
        queue.delete_message(msg[0])

        # Clear all messages
        queue.clear_messages()

        # Delete the queue
        queue.delete_queue()

    @record
    def test_peek_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "peekqueue")

        # Create the queue
        queue.create_queue()

        # Enqueue messages
        queue.enqueue_message("message1")
        queue.enqueue_message("message2")
        queue.enqueue_message("message3")
        queue.enqueue_message("message4")
        queue.enqueue_message("message5")

        # Peek at one message at the front of the queue
        msg = queue.peek_messages()

        # Peek at the last 5 messages
        messages = queue.peek_messages(max_messages=5)

        # Print the last 5 messages
        for message in messages:
            print(message.content)

        # Delete the queue
        queue.delete_queue()

    @record
    def test_update_message(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "updatequeue")

        # Create the queue
        queue.create_queue()

        # Enqueue a message
        queue.enqueue_message("update me")

        # Dequeue the message
        messages = queue.dequeue_messages()

        # Update the message
        list_result = next(messages)[0]
        message = queue.update_message(
            list_result.id,
            pop_receipt=list_result.pop_receipt,
            visibility_timeout=0,
            content="updated")

        assert message.content == "updated"

        # Delete the queue
        queue.delete_queue()
