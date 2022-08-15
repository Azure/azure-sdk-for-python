# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import asyncio
import os
from datetime import datetime
from msrest.serialization import TZ_UTC

from azure.communication.identity import CommunicationIdentityClient
from azure.communication.chat.aio import (
    ChatClient,
    CommunicationTokenCredential
)
from azure.communication.chat import (
    ChatParticipant,
    ChatMessageType
)
from azure.communication.identity._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor
from _shared.helper import URIIdentityReplacer
from chat_e2e_helper import ChatURIReplacer
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor, ResponseReplacerProcessor
from _shared.utils import get_http_logging_policy


class ChatThreadClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(ChatThreadClientTestAsync, self).setUp()

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "senderId", "chatMessageId", "nextLink", "participants", "multipleStatus", "value"]),
            URIIdentityReplacer(),
            ResponseReplacerProcessor(keys=[self._resource_name]),
            ChatURIReplacer()])

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

        self.identity_client = CommunicationIdentityClient.from_connection_string(self.connection_str)

        self.users = []
        self.user_tokens = []
        self.chat_clients = []

        # create user 1
        self.user = self.identity_client.create_user()
        token_response = self.identity_client.get_token(self.user, scopes=["chat"])
        self.token = token_response.token

        # create user 2
        self.new_user = self.identity_client.create_user()
        token_response = self.identity_client.get_token(self.new_user, scopes=["chat"])
        self.token_new_user = token_response.token

        # create ChatClient
        self.chat_client = ChatClient(
            self.endpoint, 
            CommunicationTokenCredential(self.token), 
            http_logging_policy=get_http_logging_policy()
        )
        self.chat_client_new_user = ChatClient(
            self.endpoint, 
            CommunicationTokenCredential(self.token_new_user), 
            http_logging_policy=get_http_logging_policy()
        )

    def tearDown(self):
        super(ChatThreadClientTestAsync, self).tearDown()

        # delete created users
        if not self.is_playback():
            self.identity_client.delete_user(self.user)
            self.identity_client.delete_user(self.new_user)

    async def _create_thread(self):
        # create chat thread
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [ChatParticipant(
            identifier=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        create_chat_thread_result = await self.chat_client.create_chat_thread(topic, thread_participants=participants)
        self.chat_thread_client = self.chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
        self.thread_id = self.chat_thread_client.thread_id

    async def _create_thread_w_two_users(self):
        # create chat thread
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [
            ChatParticipant(
                identifier=self.user,
                display_name='name',
                share_history_time=share_history_time
            ),
            ChatParticipant(
                identifier=self.new_user,
                display_name='name',
                share_history_time=share_history_time
            )
        ]
        create_chat_thread_result = await self.chat_client.create_chat_thread(topic, thread_participants=participants)
        self.chat_thread_client = self.chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
        self.thread_id = self.chat_thread_client.thread_id


    async def _send_message(self):
        # send a message
        content = 'hello world'
        sender_display_name = 'sender name'
        create_message_result = await self.chat_thread_client.send_message(
            content,
            sender_display_name=sender_display_name)
        message_id = create_message_result.id
        return message_id

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_topic(self):
        async with self.chat_client:
            await self._create_thread()
            topic = "update topic"

            async with self.chat_thread_client:
                await self.chat_thread_client.update_topic(topic=topic)

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_send_message(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                content = 'hello world'
                sender_display_name = 'sender name'

                create_message_result = await self.chat_thread_client.send_message(
                    content,
                    sender_display_name=sender_display_name)
                create_message_result_id = create_message_result.id

                self.assertTrue(create_message_result_id)

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_message(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                message_id = await self._send_message()
                message = await self.chat_thread_client.get_message(message_id)
                assert message.id == message_id
                assert message.type == ChatMessageType.TEXT
                assert message.content.message == 'hello world'

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_messages(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                await self._send_message()

                chat_messages = self.chat_thread_client.list_messages(results_per_page=1)

                items = []
                async for item in chat_messages:
                    items.append(item)

                assert len(items) > 0

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_message(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                message_id = await self._send_message()

                content = "updated message content"
                await self.chat_thread_client.update_message(message_id, content=content)

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_message(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                message_id = await self._send_message()

                await self.chat_thread_client.delete_message(message_id)

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_participants(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                # add another participant
                share_history_time = datetime.utcnow()
                share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
                new_participant = ChatParticipant(
                    identifier=self.new_user,
                    display_name='name',
                    share_history_time=share_history_time)

                await self.chat_thread_client.add_participants([new_participant])

                chat_thread_participants = self.chat_thread_client.list_participants(results_per_page=1, skip=1)

                items = []
                async for item in chat_thread_participants:
                    items.append(item)

                assert len(items) == 1

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_participants(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                share_history_time = datetime.utcnow()
                share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
                new_participant = ChatParticipant(
                        identifier=self.new_user,
                        display_name='name',
                        share_history_time=share_history_time)
                participants = [new_participant]

                failed_participants = await self.chat_thread_client.add_participants(participants)

                # no error occured while adding participants
                assert len(failed_participants) == 0

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_remove_participant(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                # add participant first
                share_history_time = datetime.utcnow()
                share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
                new_participant = ChatParticipant(
                        identifier=self.new_user,
                        display_name='name',
                        share_history_time=share_history_time)
                participants = [new_participant]

                await self.chat_thread_client.add_participants(participants)

                # test remove participant
                await self.chat_thread_client.remove_participant(self.new_user)

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_send_typing_notification(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                await self.chat_thread_client.send_typing_notification()

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_send_typing_notification_with_sender_display_name(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                await self.chat_thread_client.send_typing_notification(sender_display_name="John")

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_send_read_receipt(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                message_id = await self._send_message()

                await self.chat_thread_client.send_read_receipt(message_id)

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    async def _wait_on_thread(self, chat_client, thread_id, message_id):
        # print("Read Receipts Sent: ", read_receipts_sent)
        chat_thread_client = chat_client.get_chat_thread_client(thread_id)
        for _ in range(10):
            read_receipts_paged = chat_thread_client.list_read_receipts()
            chat_message_ids = []
            async for page in read_receipts_paged.by_page():
                async for item in page:
                    chat_message_ids.append(item.chat_message_id)

            if message_id in chat_message_ids:
                return
            else:
                print("Sleeping for additional 2 secs")
                await asyncio.sleep(2)
        raise Exception("Read receipts not updated in 20 seconds. Failing.")

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_read_receipts(self):
        async with self.chat_client:
            await self._create_thread_w_two_users()

            async with self.chat_thread_client:

                # first user sends 2 messages
                for i in range(2):
                    message_id = await self._send_message()
                    # send read receipts first
                    await self.chat_thread_client.send_read_receipt(message_id)

                    if self.is_live:
                        await self._wait_on_thread(chat_client=self.chat_client, thread_id=self.thread_id, message_id=message_id)



                # get chat thread client for second user
                chat_thread_client_new_user = self.chat_client_new_user.get_chat_thread_client(self.thread_id)

                # second user sends 1 message
                message_result_new_user = await chat_thread_client_new_user.send_message(
                    "content",
                    sender_display_name="sender_display_name")
                message_id_new_user = message_result_new_user.id
                # send read receipt
                await chat_thread_client_new_user.send_read_receipt(message_id_new_user)

                if self.is_live:
                    await self._wait_on_thread(chat_client=self.chat_client_new_user, thread_id=self.thread_id, message_id=message_id_new_user)

                # list read receipts
                read_receipts = self.chat_thread_client.list_read_receipts(results_per_page=2, skip=0)

                items = []
                async for page in read_receipts.by_page():
                    async for item in page:
                        items.append(item)

                assert len(items) == 2

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_properties(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                get_thread_result = await self.chat_thread_client.get_properties()
                assert get_thread_result.id == self.thread_id

                # delete created users and chat threads
                if not self.is_playback():
                    await self.chat_client.delete_chat_thread(self.thread_id)
