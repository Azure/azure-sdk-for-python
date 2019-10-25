# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
import os

class QueueMessageSamples(object):

    connection_string = os.getenv("CONNECTION_STRING")

    def set_access_policy(self):
        # [START create_queue_client_from_connection_string]
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "my_queue")
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
        queue = QueueClient.from_connection_string(self.connection_string, "my_queue")

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
        queue = QueueClient.from_connection_string(self.connection_string, "my_queue")

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

    def delete_and_clear_messages(self):
        # Instantiate a queue client
        from azure.storage.queue import QueueClient
        queue = QueueClient.from_connection_string(self.connection_string, "my_queue")

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
        queue = QueueClient.from_connection_string(self.connection_string, "my_queue")

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
        queue = QueueClient.from_connection_string(self.connection_string, "my_queue")

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
