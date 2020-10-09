# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: chat_thread_client_sample_async.py
DESCRIPTION:
    These samples demonstrate create a chat thread client, to update
    chat thread, get chat message, list chat messages, update chat message, send
    read receipt, list read receipts, delete chat message, add members, remove
    members, list members, send typing notification
    You need to use azure.communication.configuration module to get user access
    token and user identity before run this sample

USAGE:
    python chat_thread_client_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
    2) TOKEN - the user access token, from token_response.token
    3) USER_ID - the user id, from token_response.identity
"""


import os
import asyncio


class ChatThreadClientSamplesAsync(object):
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

    async def create_chat_thread_client_async(self):
        # [START create_chat_thread_client]
        from datetime import datetime
        from azure.communication.chat.aio import ChatClient, CommunicationUserCredential
        from azure.communication.chat import ChatThreadMember, CommunicationUser

        chat_client = ChatClient(self.endpoint, CommunicationUserCredential(self.token))

        async with chat_client:
            topic = "test topic"
            members = [ChatThreadMember(
                user=self.user,
                display_name='name',
                share_history_time=datetime.utcnow()
            )]
            chat_thread_client = await chat_client.create_chat_thread(topic, members)
        # [END create_chat_thread_client]

        self._thread_id = chat_thread_client.thread_id
        print("thread created, id: " + self._thread_id)

    async def update_thread_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START update_thread]
            topic = "updated thread topic"
            await chat_thread_client.update_thread(topic=topic)
            # [END update_thread]

        print("update_thread succeeded")

    async def send_message_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START send_message]
            from azure.communication.chat import ChatMessagePriority

            priority=ChatMessagePriority.NORMAL
            content='hello world'
            sender_display_name='sender name'

            send_message_result = await chat_thread_client.send_message(
                content,
                priority=priority,
                sender_display_name=sender_display_name)
            # [END send_message]
            self._message_id = send_message_result.id
            print("send_message succeeded, message id:", self._message_id)

    async def get_message_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START get_message]
            chat_message = await chat_thread_client.get_message(self._message_id)
            # [END get_message]
            print("get_message succeeded, message id:", chat_message.id, \
                "content: ", chat_message.content)

    async def list_messages_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START list_messages]
            from datetime import datetime, timedelta
            start_time = datetime.utcnow() - timedelta(days=1)
            chat_messages = chat_thread_client.list_messages(results_per_page=1, start_time=start_time)
            print("list_messages succeeded with results_per_page is 1, and start time is yesterday UTC")
            async for chat_message_page in chat_messages.by_page():
                l = [ i async for i in chat_message_page]
                print("page size: ", len(l))
            # [END list_messages]

    async def update_message_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START update_message]
            content = "updated message content"
            await chat_thread_client.update_message(self._message_id, content=content)
            # [END update_message]
            print("update_message succeeded")

    async def send_read_receipt_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START send_read_receipt]
            await chat_thread_client.send_read_receipt(self._message_id)
            # [END send_read_receipt]

        print("send_read_receipt succeeded")

    async def list_read_receipts_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START list_read_receipts]
            read_receipts = chat_thread_client.list_read_receipts()
            # [END list_read_receipts]
            print("list_read_receipts succeeded, receipts:")
            async for read_receipt in read_receipts:
                print(read_receipt)

    async def delete_message_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START delete_message]
            await chat_thread_client.delete_message(self._message_id)
            # [END delete_message]
            print("delete_message succeeded")

    async def list_members_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START list_members]
            chat_thread_members = chat_thread_client.list_members()
            print("list_members succeeded, members:")
            async for chat_thread_member in chat_thread_members:
                print(chat_thread_member)
            # [END list_members]

    async def add_members_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START add_members]
            from azure.communication.chat import ChatThreadMember, CommunicationUser
            from datetime import datetime
            new_member = ChatThreadMember(
                    user=self.new_user,
                    display_name='name',
                    share_history_time=datetime.utcnow())
            members = [new_member]
            await chat_thread_client.add_members(members)
            # [END add_members]
            print("add_members succeeded")

    async def remove_member_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START remove_member]
            await chat_thread_client.remove_member(self.new_user)
            # [END remove_member]
            print("remove_member_async succeeded")

    async def send_typing_notification_async(self):
        from azure.communication.chat.aio import ChatThreadClient, CommunicationUserCredential
        chat_thread_client = ChatThreadClient(self.endpoint, CommunicationUserCredential(self.token), self._thread_id)

        async with chat_thread_client:
            # [START send_typing_notification]
            await chat_thread_client.send_typing_notification()
            # [END send_typing_notification]
        print("send_typing_notification succeeded")

    def clean_up(self):
        print("cleaning up: deleting created users.")
        self.identity_client.delete_user(self.user)
        self.identity_client.delete_user(self.new_user)


async def main():
    sample = ChatThreadClientSamplesAsync()
    await sample.create_chat_thread_client_async()
    await sample.update_thread_async()
    await sample.send_message_async()
    await sample.get_message_async()
    await sample.list_messages_async()
    await sample.update_message_async()
    await sample.send_read_receipt_async()
    await sample.list_read_receipts_async()
    await sample.delete_message_async()
    await sample.add_members_async()
    await sample.list_members_async()
    await sample.remove_member_async()
    await sample.send_typing_notification_async()
    sample.clean_up()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
