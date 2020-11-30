# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
import time
from datetime import datetime
from devtools_testutils import AzureTestCase
from msrest.serialization import TZ_UTC

from azure.communication.administration import CommunicationIdentityClient
from azure.communication.chat import (
    ChatClient,
    CommunicationUserCredential,
    ChatThreadParticipant,
    ChatMessagePriority
)
from azure.communication.chat._shared.utils import parse_connection_str

from azure_devtools.scenario_tests import RecordingProcessor
from helper import URIIdentityReplacer
from chat_e2e_helper import ChatURIReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)


class ChatThreadClientTest(CommunicationTestCase):
    def setUp(self):
        super(ChatThreadClientTest, self).setUp()
        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "senderId", "chatMessageId", "nextLink", "participants", "multipleStatus", "value"]),
            URIIdentityReplacer(),
            ChatURIReplacer()])

        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

        # create user and issue token
        self.user = self.identity_client.create_user()
        tokenresponse = self.identity_client.issue_token(self.user, scopes=["chat"])
        self.token = tokenresponse.token

        # create another user
        self.new_user = self.identity_client.create_user()

        # create ChatClient
        self.chat_client = ChatClient(self.endpoint, CommunicationUserCredential(self.token))

    def tearDown(self):
        super(ChatThreadClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            self.identity_client.delete_user(self.user)
            self.identity_client.delete_user(self.new_user)
            self.chat_client.delete_chat_thread(self.thread_id)

    def _create_thread(self):
        # create chat thread, and ChatThreadClient
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [ChatThreadParticipant(
            user=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        self.chat_thread_client = self.chat_client.create_chat_thread(topic, participants)
        self.thread_id = self.chat_thread_client.thread_id

    @pytest.mark.live_test_only
    def _send_message(self):
        # send a message
        priority = ChatMessagePriority.NORMAL
        content = 'hello world'
        sender_display_name = 'sender name'
        create_message_result_id = self.chat_thread_client.send_message(
            content,
            priority=priority,
            sender_display_name=sender_display_name)
        self.message_id = create_message_result_id

    @pytest.mark.live_test_only
    def test_update_topic(self):
        self._create_thread()
        topic = "update topic"
        self.chat_thread_client.update_topic(topic=topic)

    @pytest.mark.live_test_only
    def test_send_message(self):
        self._create_thread()

        priority = ChatMessagePriority.NORMAL
        content = 'hello world'
        sender_display_name = 'sender name'

        create_message_result_id = self.chat_thread_client.send_message(
            content,
            priority=priority,
            sender_display_name=sender_display_name)

        assert create_message_result_id is not None

    @pytest.mark.live_test_only
    def test_get_message(self):
        self._create_thread()
        self._send_message()
        message = self.chat_thread_client.get_message(self.message_id)
        assert message.id == self.message_id

    @pytest.mark.live_test_only
    def test_list_messages(self):
        self._create_thread()
        self._send_message()
        if self.is_live:
            time.sleep(2)

        chat_messages = self.chat_thread_client.list_messages(results_per_page=1)

        for chat_message in chat_messages.by_page():
            li = list(chat_message)
            assert len(li) <= 1

    @pytest.mark.live_test_only
    def test_update_message(self):
        self._create_thread()
        self._send_message()

        content = "updated message content"
        self.chat_thread_client.update_message(self.message_id, content=content)

    @pytest.mark.live_test_only
    def test_delete_message(self):
        self._create_thread()
        self._send_message()

        self.chat_thread_client.delete_message(self.message_id)

    @pytest.mark.live_test_only
    def test_list_participants(self):
        self._create_thread()
        if self.is_live:
            time.sleep(2)

        chat_thread_participants = self.chat_thread_client.list_participants()

        for chat_thread_participant_page in chat_thread_participants.by_page():
            li = list(chat_thread_participant_page)
            assert len(li) == 1
            li[0].user.id = self.user.identifier

    @pytest.mark.live_test_only
    def test_add_participant(self):
        self._create_thread()

        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        new_participant = ChatThreadParticipant(
            user=self.new_user,
            display_name='name',
            share_history_time=share_history_time)

        self.chat_thread_client.add_participant(new_participant)

    @pytest.mark.live_test_only
    def test_add_participants(self):
        self._create_thread()

        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        new_participant = ChatThreadParticipant(
                user=self.new_user,
                display_name='name',
                share_history_time=share_history_time)
        participants = [new_participant]

        self.chat_thread_client.add_participants(participants)

    @pytest.mark.live_test_only
    def test_remove_participant(self):
        self._create_thread()

        # add participant first
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        new_participant = ChatThreadParticipant(
                user=self.new_user,
                display_name='name',
                share_history_time=share_history_time)
        participants = [new_participant]

        self.chat_thread_client.add_participants(participants)

        # test remove participant
        self.chat_thread_client.remove_participant(self.new_user)

    @pytest.mark.live_test_only
    def test_send_typing_notification(self):
        self._create_thread()

        self.chat_thread_client.send_typing_notification()

    @pytest.mark.live_test_only
    def test_send_read_receipt(self):
        self._create_thread()
        self._send_message()

        self.chat_thread_client.send_read_receipt(self.message_id)

    @pytest.mark.live_test_only
    def test_list_read_receipts(self):
        self._create_thread()
        self._send_message()

        # send read receipts first
        self.chat_thread_client.send_read_receipt(self.message_id)
        if self.is_live:
            time.sleep(2)

        # list read receipts
        read_receipts = self.chat_thread_client.list_read_receipts()

        items = []
        for item in read_receipts:
            items.append(item)
        assert len(items) > 0
