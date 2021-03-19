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
    from azure.communication.identity import CommunicationIdentityClient
    from azure.communication.chat import (
        ChatClient,
        CommunicationTokenCredential
    )
    connection_string = os.environ.get("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING", None)
    if not connection_string:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING env before run this sample.")

    identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
    user = identity_client.create_user()
    tokenresponse = identity_client.get_token(user, scopes=["chat"])
    token = tokenresponse.token

    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _thread_id = None
    _message_id = None
    new_user = identity_client.create_user()

    _chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))

    def create_chat_thread_client(self):
        token = self.token
        endpoint = self.endpoint
        user = self.user
        # [START create_chat_thread_client]
        from datetime import datetime
        from azure.communication.identity import CommunicationUserIdentifier
        from azure.communication.chat import (
            ChatClient,
            ChatThreadParticipant,
            CommunicationTokenCredential
        )
        # retrieve `token` using CommunicationIdentityClient.get_token method
        # set `endpoint` to ACS service endpoint
        # create `user` using CommunicationIdentityClient.create_user method for new users;
        # else for existing users set `user` = CommunicationUserIdentifier(some_user_id)
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        topic = "test topic"
        participants = [ChatThreadParticipant(
            user=user,
            display_name='name',
            share_history_time=datetime.utcnow()
        )]
        create_chat_thread_result = chat_client.create_chat_thread(topic, thread_participants=participants)
        chat_thread_client = chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
        # [END create_chat_thread_client]
        self._thread_id = create_chat_thread_result.chat_thread.id
        print("chat_thread_client created")

    def get_chat_thread_properties(self):
        thread_id = self._thread_id
        token = self.token
        endpoint = self.endpoint
        # [START get_thread]
        from azure.communication.chat import ChatClient, CommunicationTokenCredential

        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        chat_thread_client = chat_client.get_chat_thread_client(thread_id)
        chat_thread_properties = chat_thread_client.get_properties()
        print('Expected Thread Id: ', thread_id, ' Actual Value: ', chat_thread_properties.id)
        # [END get_thread]

        print("get_chat_thread_properties succeeded, thread id: " + chat_thread.id + ", thread topic: " + chat_thread.topic)


    def update_topic(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        # [START update_topic]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)
        chat_thread_properties = chat_thread_client.get_properties()
        previous_topic = chat_thread_properties.topic

        topic = "updated thread topic"
        chat_thread_client.update_topic(topic=topic)

        chat_thread_properties = chat_thread_client.get_properties()
        updated_topic = chat_thread_properties.topic
        print("Chat Thread Topic Update: Previous value: ", previous_topic, ", Current value: ", updated_topic)
        # [END update_topic]

        print("update_chat_thread succeeded")

    def send_message(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        # [START send_message]
        from azure.communication.chat import ChatMessageType

        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # Scenario 1: Send message without specifying chat_message_type
        send_message_result = chat_thread_client.send_message(
            "Hello! My name is Fred Flinstone",
            sender_display_name="Fred Flinstone")
        send_message_result_id = send_message_result.id

        # Scenario 2: Send message specifying chat_message_type
        send_message_result_w_type = chat_thread_client.send_message(
            "Hello! My name is Wilma Flinstone",
            sender_display_name="Wilma Flinstone",
            chat_message_type=ChatMessageType.TEXT) # equivalent to setting chat_message_type='text'
        send_message_result_w_type_id = send_message_result_w_type.id
        # Verify message content
        print("First Message:", chat_thread_client.get_message(send_message_result_id).content.message)
        print("Second Message:", chat_thread_client.get_message(send_message_result_w_type_id).content.message)
        # [END send_message]

        self._message_id = send_message_result_id
        print("send_message succeeded, message_id=", send_message_result_id)
        print("send_message succeeded with type specified, message_id:", send_message_result_w_type_id)

    def get_message(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        message_id = self._message_id
        # [START get_message]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # set `message_id` to an existing message id
        chat_message = chat_thread_client.get_message(message_id)

        print("Message received: ChatMessage: content=", chat_message.content.message, ", id=", chat_message.id)
        # [END get_message]

        print("get_message succeeded, message id:", chat_message.id, \
            "content: ", chat_message.content.message)

    def list_messages(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        # [START list_messages]
        from datetime import datetime, timedelta

        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        start_time = datetime.utcnow() - timedelta(days=1)
        chat_messages = chat_thread_client.list_messages(results_per_page=1, start_time=start_time)

        print("list_messages succeeded with results_per_page is 1, and start time is yesterday UTC")
        for chat_message_page in chat_messages.by_page():
            for chat_message in chat_message_page:
                print("ChatMessage: message=", chat_message.content.message)
        # [END list_messages]
        print("list_messages succeeded")

    def update_message(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        message_id = self._message_id
        # [START update_message]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # set `message_id` to an existing message id
        previous_content = chat_thread_client.get_message(message_id).content.message
        content = "updated content"
        chat_thread_client.update_message(message_id, content=content)

        current_content = chat_thread_client.get_message(message_id).content.message

        print("Chat Message Updated: Previous value: ", previous_content, ", Current value: ", current_content)
        # [END update_message]

        print("update_message succeeded")

    def send_read_receipt(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        message_id = self._message_id
        # [START send_read_receipt]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # set `message_id` to an existing message id
        chat_thread_client.send_read_receipt(message_id)
        # [END send_read_receipt]

        print("send_read_receipt succeeded")

    def list_read_receipts(self):
        thread_id = self._thread_id
        chat_client = self._chat_client

        # [START list_read_receipts]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        read_receipts = chat_thread_client.list_read_receipts()

        for read_receipt_page in read_receipts.by_page():
            for read_receipt in read_receipt_page:
                print(read_receipt)
        # [END list_read_receipts]
        print("list_read_receipts succeeded")

    def delete_message(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        message_id = self._message_id

        # [START delete_message]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # set `message_id` to an existing message id
        chat_thread_client.delete_message(message_id)
        # [END delete_message]
        print("delete_message succeeded")

    def list_participants(self):
        thread_id = self._thread_id
        chat_client = self._chat_client

        # [START list_participants]

        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        chat_thread_participants = chat_thread_client.list_participants()

        for chat_thread_participant_page in chat_thread_participants.by_page():
            for chat_thread_participant in chat_thread_participant_page:
                print("ChatThreadParticipant: ", chat_thread_participant)
        # [END list_participants]
        print("list_participants succeeded")


    def add_participants_w_check(self):
        # initially remove already added user
        thread_id = self._thread_id
        chat_client = self._chat_client
        user = self.new_user
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        chat_thread_client.remove_participant(user)

        # [START add_participants]
        from azure.communication.chat import ChatThreadParticipant
        from datetime import datetime

        def decide_to_retry(error):
            """
            Custom logic to decide whether to retry to add or not
            """
            return True

        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # create `user` using CommunicationIdentityClient.create_user method for new users;
        # else for existing users set `user` = CommunicationUserIdentifier(some_user_id)
        new_participant = ChatThreadParticipant(
            user=user,
            display_name='name',
            share_history_time=datetime.utcnow())

        # create list containing one or more participants
        thread_participants = [new_participant]
        result = chat_thread_client.add_participants(thread_participants)

        # list of participants which were unsuccessful to be added to chat thread
        retry = [p for p, e in result if decide_to_retry(e)]
        if len(retry) > 0:
            chat_thread_client.add_participants(retry)
        # [END add_participants]
        print("add_participants_w_check succeeded")



    def remove_participant(self):
        thread_id = self._thread_id
        chat_client = self._chat_client
        identity_client = self.identity_client

        # [START remove_participant]
        from azure.communication.chat import ChatThreadParticipant
        from azure.communication.identity import CommunicationUserIdentifier
        from datetime import datetime

        # create 2 new users using CommunicationIdentityClient.create_user method
        user1 = identity_client.create_user()
        user2 = identity_client.create_user()

        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

        # add user1 and user2 to chat thread
        participant1 = ChatThreadParticipant(
                user=user1,
                display_name='Fred Flinstone',
                share_history_time=datetime.utcnow())

        participant2 = ChatThreadParticipant(
            user=user2,
            display_name='Wilma Flinstone',
            share_history_time=datetime.utcnow())

        thread_participants = [participant1, participant2]
        chat_thread_client.add_participants(thread_participants)

        # Option 1 : Iterate through all participants, find and delete Fred Flinstone
        chat_thread_participants = chat_thread_client.list_participants()

        for chat_thread_participant_page in chat_thread_participants.by_page():
            for chat_thread_participant in chat_thread_participant_page:
                print("ChatThreadParticipant: ", chat_thread_participant)
                if chat_thread_participant.user.identifier == user1.identifier:
                    print("Found Fred!")
                    chat_thread_client.remove_participant(chat_thread_participant.user)
                    print("Fred has been removed from the thread...")
                    break

        # Option 2: Directly remove Wilma Flinstone
        unique_identifier = user2.identifier # in real scenario the identifier would need to be retrieved from elsewhere
        chat_thread_client.remove_participant(CommunicationUserIdentifier(unique_identifier))
        print("Wilma has been removed from the thread...")
        # [END remove_participant]

        # clean up temporary users
        self.identity_client.delete_user(user1)
        self.identity_client.delete_user(user2)
        print("remove_chat_participant succeeded")

    def send_typing_notification(self):
        thread_id = self._thread_id
        chat_client = self._chat_client

        # [START send_typing_notification]
        # set `thread_id` to an existing thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id=thread_id)

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
    sample.add_participant_w_check()
    sample.add_participants_w_check()
    sample.list_participants()
    sample.remove_participant()
    sample.send_typing_notification()
    sample.clean_up()
