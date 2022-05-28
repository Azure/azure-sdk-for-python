# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: queue_samples_message.py

DESCRIPTION:
    These samples demonstrate the following: creating and setting an access policy to generate a
    sas token, getting a queue client from a queue URL, setting and getting queue
    metadata, sending messages and receiving them individually or by batch, deleting and
    clearing all messages, and peeking and updating messages.

USAGE:
    python queue_samples_message.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""


from datetime import datetime, timedelta
import os


class QueueMessageSamples(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    def set_access_policy(self):
        # [START create_queue_client_from_connection_string]
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue1")
        # [END create_queue_client_from_connection_string]

        # Create the queue
        queue.create_queue()

        # Send a message
        queue.send_message(u"hello world")

        try:
            # [START set_access_policy]
            # Create an access policy
            from azure.storage.queue import AccessPolicy, QueueSasPermissions
            access_policy = AccessPolicy()
            access_policy.start = datetime.utcnow() - timedelta(hours=1)
            access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
            access_policy.permission = QueueSasPermissions(read=True)
            identifiers = {'my-access-policy-id': access_policy}

            # Set the access policy
            queue.set_queue_access_policy(identifiers)
            # [END set_access_policy]

            # Use the access policy to generate a SAS token
            # [START queue_client_sas_token]
            from azure.storage.queue import generate_queue_sas
            sas_token = generate_queue_sas(
                queue.account_name,
                queue.queue_name,
                queue.credential.account_key,
                policy_id='my-access-policy-id'
            )
            # [END queue_client_sas_token]

            # Authenticate with the sas token
            # [START create_queue_client]
            token_auth_queue = QueueClient.from_queue_url(
                queue_url=queue.url,
                credential=sas_token
            )
            # [END create_queue_client]

            # Use the newly authenticated client to receive messages
            my_message = token_auth_queue.receive_messages()

        finally:
            # Delete the queue
            queue.delete_queue()

    def queue_metadata(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue2")

        # Create the queue
        queue.create_queue()

        try:
            # [START set_queue_metadata]
            metadata = {'foo': 'val1', 'bar': 'val2', 'baz': 'val3'}
            queue.set_queue_metadata(metadata=metadata)
            # [END set_queue_metadata]

            # [START get_queue_properties]
            properties = queue.get_queue_properties().metadata
            # [END get_queue_properties]

        finally:
            # Delete the queue
            queue.delete_queue()

    def send_and_receive_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue3")

        # Create the queue
        queue.create_queue()

        try:
            # [START send_messages]
            queue.send_message(u"message1")
            queue.send_message(u"message2", visibility_timeout=30)  # wait 30s before becoming visible
            queue.send_message(u"message3")
            queue.send_message(u"message4")
            queue.send_message(u"message5")
            # [END send_messages]

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

    def list_message_pages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue4")

        # Create the queue
        queue.create_queue()

        try:
            queue.send_message(u"message1")
            queue.send_message(u"message2")
            queue.send_message(u"message3")
            queue.send_message(u"message4")
            queue.send_message(u"message5")
            queue.send_message(u"message6")

            # [START receive_messages_listing]
            # Store two messages in each page
            message_batches = queue.receive_messages(messages_per_page=2).by_page()

            # Iterate through the page lists
            print(list(next(message_batches)))
            print(list(next(message_batches)))

            # There are two iterations in the last page as well.
            last_page = next(message_batches)
            for message in last_page:
                print(message)
            # [END receive_messages_listing]

        finally:
            queue.delete_queue()

    def receive_one_message_from_queue(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue5")

        # Create the queue
        queue.create_queue()

        try:
            queue.send_message(u"message1")
            queue.send_message(u"message2")
            queue.send_message(u"message3")

            # [START receive_one_message]
            # Pop two messages from the front of the queue
            message1 = queue.receive_message()
            message2 = queue.receive_message()
            # We should see message 3 if we peek
            message3 = queue.peek_messages()[0]

            print(message1.content)
            print(message2.content)
            print(message3.content)
            # [END receive_one_message]

        finally:
            queue.delete_queue()

    def delete_and_clear_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue6")

        # Create the queue
        queue.create_queue()

        try:
            # Send messages
            queue.send_message(u"message1")
            queue.send_message(u"message2")
            queue.send_message(u"message3")
            queue.send_message(u"message4")
            queue.send_message(u"message5")

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

    def peek_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue7")

        # Create the queue
        queue.create_queue()

        try:
            # Send messages
            queue.send_message(u"message1")
            queue.send_message(u"message2")
            queue.send_message(u"message3")
            queue.send_message(u"message4")
            queue.send_message(u"message5")

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

    def update_message(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue8")

        # Create the queue
        queue.create_queue()

        try:
            # [START update_message]
            # Send a message
            queue.send_message(u"update me")

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

        finally:
            # Delete the queue
            queue.delete_queue()

    def receive_messages_with_max_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "myqueue9")

        # Create the queue
        queue.create_queue()

        try:
            queue.send_message(u"message1")
            queue.send_message(u"message2")
            queue.send_message(u"message3")
            queue.send_message(u"message4")
            queue.send_message(u"message5")
            queue.send_message(u"message6")
            queue.send_message(u"message7")
            queue.send_message(u"message8")
            queue.send_message(u"message9")
            queue.send_message(u"message10")

            # Receive messages one-by-one
            messages = queue.receive_messages(max_messages=5)
            for msg in messages:
                print(msg.content)
                queue.delete_message(msg)

            # Only prints 5 messages because 'max_messages'=5
            # >>message1
            # >>message2
            # >>message3
            # >>message4
            # >>message5

        finally:
            # Delete the queue
            queue.delete_queue()


if __name__ == '__main__':
    sample = QueueMessageSamples()
    sample.set_access_policy()
    sample.queue_metadata()
    sample.send_and_receive_messages()
    sample.list_message_pages()
    sample.receive_one_message_from_queue()
    sample.delete_and_clear_messages()
    sample.peek_messages()
    sample.update_message()
    sample.receive_messages_with_max_messages()