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
from azure.communication.identity._shared.user_credential import CommunicationTokenCredential
from azure.communication.chat._shared.user_token_refresh_options import CommunicationTokenRefreshOptions
from azure.communication.chat import (
    ChatClient,
    ChatThreadParticipant
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
        refresh_options = CommunicationTokenRefreshOptions(self.token)
        self.chat_client = ChatClient(self.endpoint, CommunicationTokenCredential(refresh_options))

    def tearDown(self):
        super(ChatClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            self.identity_client.delete_user(self.user)
            self.chat_client.delete_chat_thread(self.thread_id)

    def _create_thread(self, repeatability_request_id=None):
        # create chat thread
        topic = "test topic"
        share_history_time = datetime.utcnow()
        share_history_time = share_history_time.replace(tzinfo=TZ_UTC)
        participants = [ChatThreadParticipant(
            user=self.user,
            display_name='name',
            share_history_time=share_history_time
        )]
        create_chat_thread_result = self.chat_client.create_chat_thread(topic,
                                                                        thread_participants=participants,
                                                                        repeatability_request_id=repeatability_request_id)
        self.thread_id = create_chat_thread_result.chat_thread.id

    @pytest.mark.live_test_only
    def test_access_token_validation(self):
        """
        This is to make sure that consecutive calls made using the same chat_client or chat_thread_client
        does not throw an exception due to mismatch in the generation of azure.core.credentials.AccessToken
        """
        from azure.communication.identity._shared.user_token_refresh_options import \
            CommunicationTokenRefreshOptions as IdentityCommunicationTokenRefreshOptions

        # create ChatClient
        refresh_options = IdentityCommunicationTokenRefreshOptions(self.token)
        chat_client = ChatClient(self.endpoint, CommunicationTokenCredential(refresh_options))
        raised = False
        try:
            # create chat thread
            topic1 = "test topic1"
            create_chat_thread1_result = chat_client.create_chat_thread(topic1)
            self.thread_id = create_chat_thread1_result.chat_thread.id

            # get chat thread
            chat_thread1 = chat_client.get_chat_thread(create_chat_thread1_result.chat_thread.id)

            # get chat thread client
            chat_thread1_client = chat_client.get_chat_thread_client(self.thread_id)

            # list all chat threads
            chat_thead_infos = chat_client.list_chat_threads()
            for chat_threads_info_page in chat_thead_infos.by_page():
                for chat_thread_info in chat_threads_info_page:
                    print("ChatThreadInfo: ", chat_thread_info)
        except:
           raised = True

        assert raised is True

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
        repeatability_request_id = str(uuid4())
        # create thread
        self._create_thread(repeatability_request_id=repeatability_request_id)
        thread_id = self.thread_id

        # re-create thread with same repeatability_request_id
        self._create_thread(repeatability_request_id=repeatability_request_id)

        # test idempotency
        assert thread_id == self.thread_id

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
