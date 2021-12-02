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
from uuid import uuid4

from azure.communication.identity import CommunicationIdentityClient
from azure.communication.chat import (
    ChatClient,
    CommunicationTokenCredential,
    ChatParticipant
)
from azure.communication.chat._shared.utils import parse_connection_str

from azure_devtools.scenario_tests import RecordingProcessor
from _shared.helper import URIIdentityReplacer
from chat_e2e_helper import ChatURIReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)
from _shared.utils import get_http_logging_policy


class ChatClientTest(CommunicationTestCase):
    def setUp(self):
        super(ChatClientTest, self).setUp()

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["id", "token", "createdBy", "participants", "multipleStatus", "value"]),
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

        # create ChatClient
        self.chat_client = ChatClient(
            self.endpoint, 
            CommunicationTokenCredential(self.token), 
            http_logging_policy=get_http_logging_policy()
        )

    def tearDown(self):
        super(ChatClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            self.chat_client.delete_chat_thread(self.thread_id)
            self.identity_client.delete_user(self.user)

    def _create_thread(self, idempotency_token=None):
        # create chat thread
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [ChatParticipant(
            identifier=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        create_chat_thread_result = self.chat_client.create_chat_thread(topic,
                                                                        thread_participants=participants,
                                                                        idempotency_token=idempotency_token)
        self.thread_id = create_chat_thread_result.chat_thread.id

    @pytest.mark.live_test_only
    def test_access_token_validation(self):
        """
        This is to make sure that consecutive calls made using the same chat_client or chat_thread_client
        does not throw an exception due to mismatch in the generation of azure.core.credentials.AccessToken
        """

        # create ChatClient
        chat_client = ChatClient(
            self.endpoint, 
            CommunicationTokenCredential(self.token),
            http_logging_policy=get_http_logging_policy()
        )
        raised = False
        try:
            # create chat thread
            topic1 = "test topic1"
            create_chat_thread1_result = chat_client.create_chat_thread(topic1)
            self.thread_id = create_chat_thread1_result.chat_thread.id

            # get chat thread client
            chat_thread1_client = chat_client.get_chat_thread_client(self.thread_id)

            # list all chat threads
            chat_thead_infos = chat_client.list_chat_threads()
            for chat_threads_info_page in chat_thead_infos.by_page():
                for chat_thread_info in chat_threads_info_page:
                    print("ChatThreadInfo: ", chat_thread_info)
        except:
           raised = True

        assert raised is False

    @pytest.mark.live_test_only
    def test_create_chat_thread(self):
        self._create_thread()
        assert self.thread_id is not None

    @pytest.mark.live_test_only
    def test_create_chat_thread_w_no_participants(self):
        # create chat thread
        topic = "test topic"
        create_chat_thread_result = self.chat_client.create_chat_thread(topic)
        self.thread_id = create_chat_thread_result.chat_thread.id
        assert create_chat_thread_result.chat_thread is not None
        assert create_chat_thread_result.errors is None

    @pytest.mark.live_test_only
    def test_create_chat_thread_w_repeatability_request_id(self):
        idempotency_token = str(uuid4())
        # create thread
        self._create_thread(idempotency_token=idempotency_token)
        thread_id = self.thread_id

        # re-create thread with same idempotency_token
        self._create_thread(idempotency_token=idempotency_token)

        # test idempotency
        assert thread_id == self.thread_id

    @pytest.mark.live_test_only
    def test_list_chat_threads(self):
        self._create_thread()
        if self.is_live:
            time.sleep(2)

        chat_threads = self.chat_client.list_chat_threads(results_per_page=1)
        for chat_thread_item_page in chat_threads.by_page():
            li = list(chat_thread_item_page)
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
