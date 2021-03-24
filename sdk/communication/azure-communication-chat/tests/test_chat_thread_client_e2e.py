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

from azure.communication.identity import CommunicationIdentityClient
from azure.communication.chat import (
    ChatClient,
    ChatThreadParticipant,
    ChatMessageType,
    CommunicationTokenCredential
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
        tokenresponse = self.identity_client.get_token(self.user, scopes=["chat"])
        self.token = tokenresponse.token

        # create another user
        self.new_user = self.identity_client.create_user()
        tokenresponse = self.identity_client.get_token(self.new_user, scopes=["chat"])
        self.token_new_user = tokenresponse.token

        # create ChatClient
        self.chat_client = ChatClient(self.endpoint, CommunicationTokenCredential(self.token))
        self.chat_client_new_user = ChatClient(self.endpoint, CommunicationTokenCredential(self.token_new_user))

    def tearDown(self):
        super(ChatThreadClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            self.identity_client.delete_user(self.user)
            self.identity_client.delete_user(self.new_user)
            self.chat_client.delete_chat_thread(self.thread_id)

    def _create_thread(
            self,
            **kwargs
    ):
        # create chat thread, and ChatThreadClient
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [ChatThreadParticipant(
            user=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        create_chat_thread_result = self.chat_client.create_chat_thread(topic, thread_participants=participants)
        self.chat_thread_client = self.chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
        self.thread_id = self.chat_thread_client.thread_id

    def _create_thread_w_two_users(
            self,
            **kwargs
    ):
        # create chat thread, and ChatThreadClient
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [
            ChatThreadParticipant(
                user=self.user,
                display_name='name',
                share_history_time=share_history_time
            ),
            ChatThreadParticipant(
                user=self.new_user,
                display_name='name',
                share_history_time=share_history_time
            )
        ]
        create_chat_thread_result = self.chat_client.create_chat_thread(topic, thread_participants=participants)
        self.chat_thread_client = self.chat_client.get_chat_thread_client(create_chat_thread_result.chat_thread.id)
        self.thread_id = self.chat_thread_client.thread_id

    def _send_message(self):
        # send a message
        content = 'hello world'
        sender_display_name = 'sender name'
        create_message_result = self.chat_thread_client.send_message(
            content,
            sender_display_name=sender_display_name)
        message_id = create_message_result.id
        return message_id

    @pytest.mark.live_test_only
    def test_update_topic(self):
        self._create_thread()
        topic = "update topic"
        self.chat_thread_client.update_topic(topic=topic)

    @pytest.mark.live_test_only
    def test_send_message(self):
        self._create_thread()

        content = 'hello world'
        sender_display_name = 'sender name'

        create_message_result = self.chat_thread_client.send_message(
            content,
            sender_display_name=sender_display_name)
        create_message_result_id = create_message_result.id

        assert create_message_result_id is not None

    @pytest.mark.live_test_only
    def test_get_message(self):
        self._create_thread()
        message_id = self._send_message()
        message = self.chat_thread_client.get_message(message_id)
        assert message.id == message_id
        assert message.type == ChatMessageType.TEXT
        assert message.content.message == 'hello world'

    @pytest.mark.live_test_only
    def test_list_messages(self):
        self._create_thread()
        self._send_message()

        chat_messages = self.chat_thread_client.list_messages(results_per_page=1)

        for chat_message in chat_messages.by_page():
            li = list(chat_message)
            assert len(li) <= 1

    @pytest.mark.live_test_only
    def test_update_message(self):
        self._create_thread()
        message_id = self._send_message()

        content = "updated message content"
        self.chat_thread_client.update_message(message_id, content=content)

    @pytest.mark.live_test_only
    def test_delete_message(self):
        self._create_thread()
        message_id = self._send_message()

        self.chat_thread_client.delete_message(message_id)

    @pytest.mark.live_test_only
    def test_list_participants(self):
        self._create_thread()

        # add another participant
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        new_participant = ChatThreadParticipant(
            user=self.new_user,
            display_name='name',
            share_history_time=share_history_time)

        self.chat_thread_client.add_participants([new_participant])

        # fetch list of participants
        chat_thread_participants = self.chat_thread_client.list_participants(results_per_page=1, skip=1)

        participant_count = 0

        for chat_thread_participant_page in chat_thread_participants.by_page():
            li = list(chat_thread_participant_page)
            assert len(li) <= 1
            participant_count += len(li)
            li[0].user.id = self.user.identifier
        assert participant_count == 1


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

        failed_participants = self.chat_thread_client.add_participants(participants)

        # no error occured while adding participants
        assert len(failed_participants) == 0


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
        message_id = self._send_message()

        self.chat_thread_client.send_read_receipt(message_id)


    def _wait_on_thread(self, chat_client, thread_id, message_id):
        # print("Read Receipts Sent: ", read_receipts_sent)
        chat_thread_client = chat_client.get_chat_thread_client(thread_id)
        for _ in range(10):
            read_receipts_paged = chat_thread_client.list_read_receipts()
            chat_message_ids = []
            for page in read_receipts_paged.by_page():
                for item in page:
                    chat_message_ids.append(item.chat_message_id)

            if message_id in chat_message_ids:
                return
            else:
                print("Sleeping for additional 2 secs")
                time.sleep(2)
        raise Exception("Read receipts not updated in 20 seconds. Failing.")


    @pytest.mark.live_test_only
    def test_list_read_receipts(self):
        self._create_thread_w_two_users()

        # first user send 2 messages
        # send messages and read receipts
        for i in range(2):
            message_id = self._send_message()
            self.chat_thread_client.send_read_receipt(message_id)

            if self.is_live:
                self._wait_on_thread(chat_client=self.chat_client, thread_id=self.thread_id, message_id=message_id)

        # get chat thread client for second user
        chat_thread_client_new_user = self.chat_client_new_user.get_chat_thread_client(self.thread_id)
        # second user sends 1 message
        message_result_new_user = chat_thread_client_new_user.send_message(
            "content",
            sender_display_name="sender_display_name")
        message_id_new_user = message_result_new_user.id
        # send read receipt
        chat_thread_client_new_user.send_read_receipt(message_id_new_user)

        if self.is_live:
            self._wait_on_thread(chat_client=self.chat_client_new_user, thread_id=self.thread_id, message_id=message_id_new_user)

        # list read receipts
        read_receipts = self.chat_thread_client.list_read_receipts(results_per_page=2, skip=0)

        items = []
        for page in read_receipts.by_page():
            for item in page:
                items.append(item)

        assert len(items) == 2

    @pytest.mark.live_test_only
    def test_get_properties(self):
        self._create_thread()
        get_thread_result = self.chat_thread_client.get_properties()
        assert get_thread_result.id == self.thread_id
