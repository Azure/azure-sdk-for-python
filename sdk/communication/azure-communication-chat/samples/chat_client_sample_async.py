
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: chat_client_sample_async.py
DESCRIPTION:
    These samples demonstrate create a chat client, get a chat thread client,
    create a chat thread, get a chat thread by id, list chat threads, delete
    a chat thread by id.
    You need to use azure.communication.configuration module to get user access
    token and user identity before run this sample

USAGE:
    python chat_client_sample_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
    2) TOKEN - the user access token, from token_response.token
    3) USER_ID - the user id, from token_response.identity
"""

import os
import asyncio


class ChatClientSamplesAsync(object):
    from azure.communication.identity import CommunicationIdentityClient
    connection_string = os.environ.get("COMMUNICATION_SAMPLES_CONNECTION_STRING", None)
    if not connection_string:
        raise ValueError("Set COMMUNICATION_SAMPLES_CONNECTION_STRING env before run this sample.")

    identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
    user = identity_client.create_user()
    tokenresponse = identity_client.get_token(user, scopes=["chat"])
    token = tokenresponse.token

    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _thread_id = None

    def create_chat_client(self):
        token = self.token
        endpoint = self.endpoint
        thread_id = self._thread_id

        # [START create_chat_client]
        from azure.communication.chat.aio import ChatClient, CommunicationTokenCredential

        # set `endpoint` to an existing ACS endpoint
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        # [END create_chat_client]
        print("chat_client created")

    async def create_thread_async(self):
        token = self.token
        endpoint = self.endpoint
        thread_id = self._thread_id

        # [START create_thread]
        from datetime import datetime
        from azure.communication.chat.aio import ChatClient, CommunicationTokenCredential
        from azure.communication.chat import ChatParticipant

        # set `endpoint` to an existing ACS endpoint
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        async with chat_client:

            topic = "test topic"
            participants = [ChatParticipant(
                identifier=self.user,
                display_name='name',
                share_history_time=datetime.utcnow()
            )]
            # creates a new chat_thread everytime
            create_chat_thread_result = await chat_client.create_chat_thread(topic, thread_participants=participants)

            # creates a new chat_thread if not exists
            idempotency_token = 'b66d6031-fdcc-41df-8306-e524c9f226b8'  # unique identifier
            create_chat_thread_result_w_repeatability_id = await chat_client.create_chat_thread(
                topic,
                thread_participants=participants,
                idempotency_token=idempotency_token)
            # [END create_thread]

            self._thread_id = create_chat_thread_result.chat_thread.id
            print("thread created, id: " + self._thread_id)

    def get_chat_thread_client(self):
        token = self.token
        endpoint = self.endpoint
        thread_id = self._thread_id

        # [START get_chat_thread_client]
        from azure.communication.chat.aio import ChatClient, CommunicationTokenCredential

        # set `endpoint` to an existing ACS endpoint
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))

        # set `thread_id` to an existing chat thread id
        chat_thread_client = chat_client.get_chat_thread_client(thread_id)
        # [END get_chat_thread_client]

        print("chat_thread_client created with thread id: ", chat_thread_client.thread_id)


    async def list_threads_async(self):
        token = self.token
        endpoint = self.endpoint
        thread_id = self._thread_id

        # [START list_threads]
        from azure.communication.chat.aio import ChatClient, CommunicationTokenCredential

        # set `endpoint` to an existing ACS endpoint
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        async with chat_client:

            from datetime import datetime, timedelta
            start_time = datetime.utcnow() - timedelta(days=2)
            chat_threads = chat_client.list_chat_threads(results_per_page=5, start_time=start_time)
            print("list_threads succeeded with results_per_page is 5, and were created since 2 days ago.")
            async for chat_thread_item_page in chat_threads.by_page():
                async for chat_thread_item in chat_thread_item_page:
                    print("thread id: ", chat_thread_item.id)
        # [END list_threads]

    async def delete_thread_async(self):
        token = self.token
        endpoint = self.endpoint
        thread_id = self._thread_id

        # [START delete_thread]
        from azure.communication.chat.aio import ChatClient, CommunicationTokenCredential

        # set `endpoint` to an existing ACS endpoint
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        async with chat_client:
            # set `thread_id` to an existing chat thread id
            await chat_client.delete_chat_thread(thread_id)
        # [END delete_thread]
            print("delete_thread succeeded")

    def clean_up(self):
        print("cleaning up: deleting created user.")
        self.identity_client.delete_user(self.user)


async def main():
    sample = ChatClientSamplesAsync()
    sample.create_chat_client()
    await sample.create_thread_async()
    sample.get_chat_thread_client()
    await sample.list_threads_async()
    await sample.delete_thread_async()
    sample.clean_up()

if __name__ == '__main__':
    asyncio.run(main())
