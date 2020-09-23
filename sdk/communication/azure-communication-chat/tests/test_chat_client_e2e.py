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
    ChatThreadMember
)
from azure.communication.chat._shared.utils import parse_connection_str

from azure_devtools.scenario_tests import RecordingProcessor
from helper import URIIdentityReplacer
from chat_e2e_helper import ChatURIReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)


class ChatClientTest(CommunicationTestCase):
    def setUp(self):
        super(ChatClientTest, self).setUp()

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "createdBy", "members", "multipleStatus", "value"]),
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

        # create ChatClient
        self.chat_client = ChatClient(self.endpoint, CommunicationUserCredential(self.token))

    def tearDown(self):
        super(ChatClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            self.identity_client.delete_user(self.user)
            self.chat_client.delete_chat_thread(self.thread_id)

    def _create_thread(self):
        # create chat thread
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        members = [ChatThreadMember(
            user=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        chat_thread_client = self.chat_client.create_chat_thread(topic, members)
        self.thread_id = chat_thread_client.thread_id

    @pytest.mark.live_test_only
    def test_create_chat_thread(self):
        self._create_thread()
        assert self.thread_id is not None

    @pytest.mark.live_test_only
    def test_get_chat_thread(self):
        self._create_thread()
        get_thread_result = self.chat_client.get_chat_thread(self.thread_id)
        assert get_thread_result.id == self.thread_id

    @pytest.mark.live_test_only
    def test_list_chat_threads(self):
        self._create_thread()
        if self.is_live:
            time.sleep(2)

        chat_thread_infos = self.chat_client.list_chat_threads(results_per_page=1)
        for chat_thread_page in chat_thread_infos.by_page():
            li = list(chat_thread_page)
            assert len(li) <= 1

    @pytest.mark.live_test_only
    def test_get_thread_client(self):
        self._create_thread()
        chat_thread_client = self.chat_client.get_chat_thread_client(self.thread_id)
        assert chat_thread_client.thread_id == self.thread_id

    @pytest.mark.live_test_only
    def test_delete_chat_thread(self):
        self._create_thread()
        self.chat_client.delete_chat_thread(self.thread_id)
