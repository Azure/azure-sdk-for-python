# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: chat_thread_client_sample.py
DESCRIPTION:
    These samples demonstrate create a chat thread client, to update
    chat thread, get chat message, list chat messages, update chat message, send
    read receipt, list read receipts, delete chat message, add participants, remove
    participants, list participants, send typing notification
    You need to use azure.communication.configuration module to get user access
    token and user identity before run this sample

USAGE:
    python chat_thread_client_sample.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
    2) TOKEN - the user access token, from token_response.token
    3) USER_ID - the user id, from token_response.identity
"""


import os


class ChatThreadClientSamples(object):
    from azure.communication.administration import CommunicationIdentityClient
    connection_string = os.environ.get("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING", None)
    if not connection_string:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING env before run this sample.")

    identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
    user = identity_client.create_user()
    tokenresponse = identity_client.issue_token(user, scopes=["chat"])
    token = tokenresponse.token

    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _thread_id = None
    _message_id = None
    new_user = identity_client.create_user()

    def create_chat_thread_client(self):
        # [START create_chat_thread_client]
        from datetime import datetime
        from azure.communication.chat import (
            ChatClient,
            ChatThreadParticipant,
            CommunicationUser,
            CommunicationUserCredential
        )
        chat_client = ChatClient(self.endpoint, CommunicationUserCredential(self.token))
        topic = "test topic"
        participants = [ChatThreadParticipant(
            user=self.user,
            display_name='name',
            share_history_time=datetime.utcnow()
        )]
        chat_thread_client = chat_client.create_chat_thread(topic, participants)
        # [END create_chat_thread_client]
        self._thread_id = chat_thread_client.thread_id
        print("chat_thread_client created")

    def update_topic(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START update_topic]
        topic = "updated thread topic"
        chat_thread_client.update_topic(topic=topic)
        # [END update_topic]

        print("update_chat_thread succeeded")

    def send_message(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START send_message]
        from azure.communication.chat import ChatMessagePriority

        priority = ChatMessagePriority.NORMAL
        content = 'hello world'
        sender_display_name = 'sender name'

        send_message_result_id = chat_thread_client.send_message(
            content,
            priority=priority,
            sender_display_name=sender_display_name)
        # [END send_message]

        self._message_id = send_message_result_id
        print("send_chat_message succeeded, message id:", self._message_id)

    def get_message(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START get_message]
        chat_message = chat_thread_client.get_message(self._message_id)
        # [END get_message]

        print("get_chat_message succeeded, message id:", chat_message.id, \
            "content: ", chat_message.content)

    def list_messages(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START list_messages]
        from datetime import datetime, timedelta
        start_time = datetime.utcnow() - timedelta(days=1)
        chat_messages = chat_thread_client.list_messages(results_per_page=1, start_time=start_time)

        print("list_messages succeeded with results_per_page is 1, and start time is yesterday UTC")
        for chat_message_page in chat_messages.by_page():
            l = list(chat_message_page)
            print("page size: ", len(l))
        # [END list_messages]

    def update_message(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START update_message]
        content = "updated content"
        chat_thread_client.update_message(self._message_id, content=content)
        # [END update_message]

        print("update_chat_message succeeded")

    def send_read_receipt(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START send_read_receipt]
        chat_thread_client.send_read_receipt(self._message_id)
        # [END send_read_receipt]

        print("send_read_receipt succeeded")

    def list_read_receipts(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START list_read_receipts]
        read_receipts = chat_thread_client.list_read_receipts()
        print("list_read_receipts succeeded, receipts:")
        for read_receipt in read_receipts:
            print(read_receipt)
        # [END list_read_receipts]

    def delete_message(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START delete_message]
        chat_thread_client.delete_message(self._message_id)
        # [END delete_message]
        print("delete_chat_message succeeded")

    def list_participants(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START list_participants]
        chat_thread_participants = chat_thread_client.list_participants()
        print("list_chat_participants succeeded, participants: ")
        for chat_thread_participant in chat_thread_participants:
            print(chat_thread_participant)
        # [END list_participants]

    def add_participant(self):
        from azure.communication.chat import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        # [START add_participant]
        from azure.communication.chat import ChatThreadParticipant
        from datetime import datetime
        new_chat_thread_participant = ChatThreadParticipant(
                user=self.new_user,
                display_name='name',
                share_history_time=datetime.utcnow())
        chat_thread_client.add_participant(new_chat_thread_participant)
        # [END add_participant]
        print("add_chat_participant succeeded")

    def add_participants(self):
        from azure.communication.chat import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        # [START add_participants]
        from azure.communication.chat import ChatThreadParticipant
        from datetime import datetime
        new_participant = ChatThreadParticipant(
                user=self.new_user,
                display_name='name',
                share_history_time=datetime.utcnow())
        thread_participants = [new_participant]
        chat_thread_client.add_participants(thread_participants)
        # [END add_participants]
        print("add_chat_participants succeeded")

    def remove_participant(self):
        from azure.communication.chat import ChatThreadClient
        from azure.communication.chat import CommunicationUserCredential, CommunicationUser
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        # [START remove_participant]
        chat_thread_client.remove_participant(self.new_user)
        # [END remove_participant]

        print("remove_chat_participant succeeded")

    def send_typing_notification(self):
        from azure.communication.chat import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)
        # [START send_typing_notification]
        chat_thread_client.send_typing_notification()
        # [END send_typing_notification]

        print("send_typing_notification succeeded")

    def clean_up(self):
        print("cleaning up: deleting created users.")
        self.identity_client.delete_user(self.user)
        self.identity_client.delete_user(self.new_user)

if __name__ == '__main__':
    sample = ChatThreadClientSamples()
    sample.create_chat_thread_client()
    sample.update_topic()
    sample.send_message()
    sample.get_message()
    sample.list_messages()
    sample.update_message()
    sample.send_read_receipt()
    sample.list_read_receipts()
    sample.delete_message()
    sample.add_participant()
    sample.add_participants()
    sample.list_participants()
    sample.remove_participant()
    sample.send_typing_notification()
    sample.clean_up()
