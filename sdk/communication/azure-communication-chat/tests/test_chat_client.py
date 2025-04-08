# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import time

from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AccessToken
from datetime import datetime, timezone
from azure.communication.chat import ChatClient, ChatParticipant
from azure.communication.chat._shared.models import CommunicationUserIdentifier

from unittest_helpers import mock_response
from datetime import datetime
import calendar

from unittest.mock import Mock, patch


def _convert_datetime_to_utc_int(input):
    return int(calendar.timegm(input.utctimetuple()))


class TestChatClient(unittest.TestCase):
    @classmethod
    @patch("azure.communication.identity._shared.user_credential.CommunicationTokenCredential")
    def setUpClass(cls, credential):
        credential.get_token = Mock(
            return_value=AccessToken(
                "some_token", _convert_datetime_to_utc_int(datetime.now().replace(tzinfo=timezone.utc))
            )
        )
        TestChatClient.credential = credential

    def test_create_chat_thread(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        chat_thread_client = None
        raised = False

        def mock_send(*_, **__):
            return mock_response(
                status_code=201,
                json_payload={
                    "chatThread": {
                        "id": thread_id,
                        "topic": "test topic",
                        "createdOn": "2020-12-03T21:09:17Z",
                        "createdBy": "8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041",
                    }
                },
            )

        chat_client = ChatClient("https://endpoint", TestChatClient.credential, transport=Mock(send=mock_send))

        topic = "test topic"
        user = CommunicationUserIdentifier("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
        participants = [ChatParticipant(identifier=user, display_name="name", share_history_time=datetime.utcnow())]
        try:
            create_chat_thread_result = chat_client.create_chat_thread(topic, thread_participants=participants)
        except:
            raised = True
            raise

        self.assertFalse(raised, "Expected is no excpetion raised")
        assert create_chat_thread_result.chat_thread.id == thread_id

    def test_create_chat_thread_w_repeatability_request_id(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        chat_thread_client = None
        raised = False
        idempotency_token = "b66d6031-fdcc-41df-8306-e524c9f226b8"

        def mock_send(*_, **__):
            return mock_response(
                status_code=201,
                json_payload={
                    "chatThread": {
                        "id": thread_id,
                        "topic": "test topic",
                        "createdOn": "2020-12-03T21:09:17Z",
                        "createdBy": "8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041",
                    }
                },
            )

        chat_client = ChatClient("https://endpoint", TestChatClient.credential, transport=Mock(send=mock_send))

        topic = "test topic"
        user = CommunicationUserIdentifier("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
        participants = [ChatParticipant(identifier=user, display_name="name", share_history_time=datetime.utcnow())]
        try:
            create_chat_thread_result = chat_client.create_chat_thread(
                topic=topic, thread_participants=participants, idempotency_token=idempotency_token
            )
        except:
            raised = True
            raise

        self.assertFalse(raised, "Expected is no excpetion raised")
        assert create_chat_thread_result.chat_thread.id == thread_id

    def test_create_chat_thread_raises_error(self):
        def mock_send(*_, **__):
            return mock_response(status_code=400, json_payload={"msg": "some error"})

        chat_client = ChatClient("https://endpoint", TestChatClient.credential, transport=Mock(send=mock_send))

        topic = ("test topic",)
        user = CommunicationUserIdentifier("8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
        thread_participants = [
            ChatParticipant(identifier=user, display_name="name", share_history_time=datetime.utcnow())
        ]

        self.assertRaises(
            HttpResponseError, chat_client.create_chat_thread, topic=topic, thread_participants=thread_participants
        )

    def test_create_chat_thread_with_invalid_participant_raises_error(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"

        def mock_send(*_, **__):
            return mock_response(
                status_code=201,
                json_payload={
                    "chatThread": {
                        "id": thread_id,
                        "topic": "Lunch",
                        "createdOn": "2020-06-06T05:55:41.6460000Z",
                        "createdByCommunicationIdentifier": {
                            "rawId": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10a",
                            "communicationUser": {
                                "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10a"
                            },
                        },
                    },
                    "invalidParticipants": [
                        {
                            "target": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10c",
                            "code": "403",
                            "message": "Permissions check failed",
                        },
                        {
                            "target": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10d",
                            "code": "404",
                            "message": "Not found",
                        },
                    ],
                },
            )

        chat_client = ChatClient("https://endpoint", TestChatClient.credential, transport=Mock(send=mock_send))

        topic = ("test topic",)
        user = CommunicationUserIdentifier("57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041")
        thread_participants = [
            ChatParticipant(identifier=user, display_name="name", share_history_time=datetime.utcnow())
        ]

        create_chat_thread_result = chat_client.create_chat_thread(topic, thread_participants=thread_participants)
        assert create_chat_thread_result.errors is not None
        assert len(create_chat_thread_result.errors) is 2

    def test_delete_chat_thread(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)

        chat_client = ChatClient("https://endpoint", TestChatClient.credential, transport=Mock(send=mock_send))

        try:
            chat_client.delete_chat_thread(thread_id)
        except:
            raised = True

        self.assertFalse(raised, "Expected is no excpetion raised")

    def test_list_chat_threads(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [{"id": thread_id}]})

        chat_client = ChatClient("https://endpoint", TestChatClient.credential, transport=Mock(send=mock_send))

        chat_threads = None
        try:
            chat_threads = chat_client.list_chat_threads()
        except:
            raised = True

        self.assertFalse(raised, "Expected is no excpetion raised")
        for chat_thread_item_page in chat_threads.by_page():
            l = list(chat_thread_item_page)
            assert len(l) == 1
            assert l[0].id == thread_id

    def test_get_thread_client(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        chat_client = ChatClient("https://endpoint", TestChatClient.credential)
        chat_thread_client = chat_client.get_chat_thread_client(thread_id)

        assert chat_thread_client.thread_id == thread_id


if __name__ == "__main__":
    unittest.main()
