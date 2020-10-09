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
    ChatThreadMember
)
from azure.communication.administration._shared.utils import parse_connection_str
from azure_devtools.scenario_tests import RecordingProcessor
from helper import URIIdentityReplacer
from chat_e2e_helper import ChatURIReplacer
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import BodyReplacerProcessor, ResponseReplacerProcessor


class ChatClientTestAsync(AsyncCommunicationTestCase):
    def setUp(self):
        super(ChatClientTestAsync, self).setUp()

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "createdBy", "members", "multipleStatus", "value"]),
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

        # create ChatClient
        self.chat_client = ChatClient(self.endpoint, CommunicationUserCredential(self.token))

    def tearDown(self):
        super(ChatClientTestAsync, self).tearDown()

        # delete created users
        if not self.is_playback():
            self.identity_client.delete_user(self.user)

    async def _create_thread(self):
        # create chat thread
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        members = [ChatThreadMember(
            user=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        chat_thread_client = await self.chat_client.create_chat_thread(topic, members)
        self.thread_id = chat_thread_client.thread_id

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_chat_thread_async(self):
        async with self.chat_client:
            await self._create_thread()
            assert self.thread_id is not None

            # delete created users and chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_chat_thread(self):
        async with self.chat_client:
            await self._create_thread()
            get_thread_result = await self.chat_client.get_chat_thread(self.thread_id)
            assert get_thread_result.id == self.thread_id

            # delete created users and chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_list_chat_threads(self):
        async with self.chat_client:
            await self._create_thread()
            if self.is_live:
                await asyncio.sleep(2)

            chat_thread_infos = self.chat_client.list_chat_threads(results_per_page=1)

            items = []
            async for item in chat_thread_infos:
                items.append(item)
            assert len(items) == 1

            # delete created users and chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_thread_client(self):
        async with self.chat_client:
            await self._create_thread()
            chat_thread_client = self.chat_client.get_chat_thread_client(self.thread_id)
            assert chat_thread_client.thread_id == self.thread_id

            # delete created users and chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_chat_thread(self):
        async with self.chat_client:
            await self._create_thread()
            await self.chat_client.delete_chat_thread(self.thread_id)

            # delete created users and chat threads
            if not self.is_playback():
                await self.chat_client.delete_chat_thread(self.thread_id)
