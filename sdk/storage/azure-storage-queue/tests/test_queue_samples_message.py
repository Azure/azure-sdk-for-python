# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from azure.core.exceptions import ResourceExistsError
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

    def test_set_access_policy(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # [START create_queue_client_from_connection_string]
        from azure.storage.queue import QueueClient
        queue_client = QueueClient.from_connection_string(self.connection_string, "queuetest")
        # [END create_queue_client_from_connection_string]

        # Create the queue
        try:
            queue_client.create_queue()
        except ResourceExistsError:
            pass
        queue_client.enqueue_message(u"hello world")

        try:
            # [START set_access_policy]
            # Create an access policy
            from azure.storage.queue import AccessPolicy, QueuePermissions
            access_policy = AccessPolicy()
            access_policy.start = datetime.utcnow() - timedelta(hours=1)
            access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
            access_policy.permission = QueuePermissions.READ
            identifiers = {'my-access-policy-id': access_policy}

            # Set the access policy
            queue_client.set_queue_access_policy(identifiers)
            # [END set_access_policy]

            # Use the access policy to generate a SAS token
            # [START queue_client_sas_token]
            sas_token = queue_client.generate_shared_access_signature(
                policy_id='my-access-policy-id'
            )
            # [END queue_client_sas_token]

            # Authenticate with the sas token
            # [START create_queue_client]
            q = QueueClient(
                queue_url=queue_client.url,
                credential=sas_token
            )
            # [END create_queue_client]

            # Use the newly authenticated client to receive messages
            my_message = q.receive_messages()
            assert my_message is not None

        finally:
            # Delete the queue
            queue_client.delete_queue()

    @record
    def test_queue_metadata(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "metaqueue")

        # Create the queue
        queue.create_queue()

        try:
            # [START set_queue_metadata]
            metadata = {'foo': 'val1', 'bar': 'val2', 'baz': 'val3'}
            queue.set_queue_metadata(metadata=metadata)
            # [END set_queue_metadata]

            # [START get_queue_properties]
            response = queue.get_queue_properties().metadata
            # [END get_queue_properties]
            assert response == metadata

        finally:
            # Delete the queue
            queue.delete_queue()

    @record
    def test_enqueue_and_receive_messages(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "messagequeue")

        # Create the queue
        queue.create_queue()

        try:
            # [START enqueue_messages]
            queue.enqueue_message(u"message1")
            queue.enqueue_message(u"message2", visibility_timeout=30)  # wait 30s before becoming visible
            queue.enqueue_message(u"message3")
            queue.enqueue_message(u"message4")
            queue.enqueue_message(u"message5")
            # [END enqueue_messages]

            # [START receive_messages]
            # Receive messages one-by-one
            messages = queue.receive_messages()
            for msg in messages:
                print(msg.content)

            # Receive messages by batch
            messages = queue.receive_messages(messages_per_page=5)
            for msg_batch in messages.by_page():
                for msg in msg_batch:
                    print(msg.content)
                    queue.delete_message(msg)
            # [END receive_messages]

            # Only prints 4 messages because message 2 is not visible yet
            # >>message1
            # >>message3
            # >>message4
            # >>message5

        finally:
            # Delete the queue
            queue.delete_queue()

    @record
    def test_delete_and_clear_messages(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "delqueue")

        # Create the queue
        queue.create_queue()

        try:
            # Enqueue messages
            queue.enqueue_message(u"message1")
            queue.enqueue_message(u"message2")
            queue.enqueue_message(u"message3")
            queue.enqueue_message(u"message4")
            queue.enqueue_message(u"message5")

            # [START delete_message]
            # Get the message at the front of the queue
            msg = next(queue.receive_messages())

            # Delete the specified message
            queue.delete_message(msg)
            # [END delete_message]

            # [START clear_messages]
            queue.clear_messages()
            # [END clear_messages]

        finally:
            # Delete the queue
            queue.delete_queue()

    @record
    def test_peek_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "peekqueue")

        # Create the queue
        queue.create_queue()

        try:
            # Enqueue messages
            queue.enqueue_message(u"message1")
            queue.enqueue_message(u"message2")
            queue.enqueue_message(u"message3")
            queue.enqueue_message(u"message4")
            queue.enqueue_message(u"message5")

            # [START peek_message]
            # Peek at one message at the front of the queue
            msg = queue.peek_messages()

            # Peek at the last 5 messages
            messages = queue.peek_messages(max_messages=5)

            # Print the last 5 messages
            for message in messages:
                print(message.content)
            # [END peek_message]

        finally:
            # Delete the queue
            queue.delete_queue()

    @record
    def test_update_message(self):

        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "updatequeue")

        # Create the queue
        queue.create_queue()

        try:
            # [START update_message]
            # Enqueue a message
            queue.enqueue_message(u"update me")

            # Receive the message
            messages = queue.receive_messages()

            # Update the message
            list_result = next(messages)
            message = queue.update_message(
                list_result.id,
                pop_receipt=list_result.pop_receipt,
                visibility_timeout=0,
                content=u"updated")
            # [END update_message]
            assert message.content == "updated"

        finally:
            # Delete the queue
            queue.delete_queue()
