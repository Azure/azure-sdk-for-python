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

from azure.communication.administration import CommunicationIdentityClient
from azure.communication.chat.aio import (
    ChatClient,
    CommunicationUserCredential
)
from azure.communication.chat import (
    ChatThreadParticipant,
    ChatMessagePriority
)
from azure.communication.administration._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor
from helper import URIIdentityReplacer
from chat_e2e_helper import ChatURIReplacer
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor, ResponseReplacerProcessor


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

        # create user
        self.user = self.identity_client.create_user()
        token_response = self.identity_client.issue_token(self.user, scopes=["chat"])
        self.token = token_response.token

        # create another user
        self.new_user = self.identity_client.create_user()

        # create ChatClient
        self.chat_client = ChatClient(self.endpoint, CommunicationUserCredential(self.token))

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
        participants = [ChatThreadParticipant(
            user=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        self.chat_thread_client = await self.chat_client.create_chat_thread(topic, participants)
        self.thread_id = self.chat_thread_client.thread_id

    async def _send_message(self):
        # send a message
        priority = ChatMessagePriority.NORMAL
        content = 'hello world'
        sender_display_name = 'sender name'
        create_message_result_id = await self.chat_thread_client.send_message(
            content,
            priority=priority,
            sender_display_name=sender_display_name)
        self.message_id = create_message_result_id

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
                priority = ChatMessagePriority.NORMAL
                content = 'hello world'
                sender_display_name = 'sender name'

                create_message_result_id = await self.chat_thread_client.send_message(
                    content,
                    priority=priority,
                    sender_display_name=sender_display_name)

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
                await self._send_message()
                message = await self.chat_thread_client.get_message(self.message_id)
                assert message.id == self.message_id

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
                if self.is_live:
                    await asyncio.sleep(2)

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
                await self._send_message()

                content = "updated message content"
                await self.chat_thread_client.update_message(self.message_id, content=content)

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_message(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                await self._send_message()

                await self.chat_thread_client.delete_message(self.message_id)

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_participants(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                chat_thread_participants = self.chat_thread_client.list_participants()

                items = []
                async for item in chat_thread_participants:
                    items.append(item)

                assert len(items) == 1

            # delete chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_participant(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                share_history_time = datetime.utcnow()
                share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
                new_participant = ChatThreadParticipant(
                    user=self.new_user,
                    display_name='name',
                    share_history_time=share_history_time)

                await self.chat_thread_client.add_participant(new_participant)

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
                new_participant = ChatThreadParticipant(
                        user=self.new_user,
                        display_name='name',
                        share_history_time=share_history_time)
                participants = [new_participant]

                await self.chat_thread_client.add_participants(participants)

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
                new_participant = ChatThreadParticipant(
                        user=self.new_user,
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
    async def test_send_read_receipt(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                await self._send_message()

                await self.chat_thread_client.send_read_receipt(self.message_id)

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_read_receipts(self):
        async with self.chat_client:
            await self._create_thread()

            async with self.chat_thread_client:
                await self._send_message()

                # send read receipts first
                await self.chat_thread_client.send_read_receipt(self.message_id)
                if self.is_live:
                    await asyncio.sleep(2)

                # list read receipts
                read_receipts = self.chat_thread_client.list_read_receipts()

                items = []
                async for item in read_receipts:
                    items.append(item)

                assert len(items) > 0

            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)
