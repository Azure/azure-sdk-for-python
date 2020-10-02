# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from datetime import datetime
from msrest.serialization import TZ_UTC
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.chat import (
    ChatThreadClient,
    ChatMessagePriority,
    ChatThreadMember,
    CommunicationUser,
    CommunicationUserCredential
)
from unittest_helpers import mock_response

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

class TestChatThreadClient(unittest.TestCase):
    @classmethod
    @patch('azure.communication.chat.CommunicationUserCredential')
    def setUpClass(cls, credential):
        credential.get_token = Mock(return_value=AccessToken("some_token", datetime.now().replace(tzinfo=TZ_UTC)))
        TestChatThreadClient.credential = credential

    def test_update_thread(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        topic = "update topic"
        try:
            chat_thread_client.update_thread(topic=topic)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_send_message(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={"id": message_id})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        create_message_result = None
        try:
            priority=ChatMessagePriority.NORMAL
            content='hello world'
            sender_display_name='sender name'

            create_message_result = chat_thread_client.send_message(
                content,
                priority=priority,
                sender_display_name=sender_display_name)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        assert create_message_result.id == message_id

    def test_get_message(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"id": message_id})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        message = None
        try:
            message = chat_thread_client.get_message(message_id)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        assert message.id == message_id

    def test_list_messages(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [{"id": message_id}]})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        chat_messages = None
        try:
            chat_messages = chat_thread_client.list_messages(results_per_page=1)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for chat_message in chat_messages.by_page():
            l = list(chat_message)
            assert len(l) == 1
            assert l[0].id == message_id

    def test_list_messages_with_start_time(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "value": [
                    {"id": "message_id1", "createdOn": "2020-08-17T18:05:44Z"},
                    {"id": "message_id2", "createdOn": "2020-08-17T23:13:33Z"}
                    ]})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        chat_messages = None
        try:
            chat_messages = chat_thread_client.list_messages(
                start_time=datetime(2020, 8, 17, 18, 0, 0)
            )
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for chat_message in chat_messages.by_page():
            l = list(chat_message)
            assert len(l) == 2

    def test_update_message(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        try:
            content = "updated message content"
            chat_thread_client.update_message(message_id, content=content)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_delete_message(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        try:
            chat_thread_client.delete_message(message_id)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_list_members(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        member_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [{"id": member_id}]})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        chat_thread_members = None
        try:
            chat_thread_members = chat_thread_client.list_members()
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for chat_thread_member_page in chat_thread_members.by_page():
            l = list(chat_thread_member_page)
            assert len(l) == 1
            l[0].user.id = member_id

    def test_add_members(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        new_member_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=207)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        new_member = ChatThreadMember(
                user=CommunicationUser(new_member_id),
                display_name='name',
                share_history_time=datetime.utcnow())
        members = [new_member]

        try:
            chat_thread_client.add_members(members)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_remove_member(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        member_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        try:
            chat_thread_client.remove_member(CommunicationUser(member_id))
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_send_typing_notification(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        try:
            chat_thread_client.send_typing_notification()
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_send_read_receipt(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id="1596823919339"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=201)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        try:
            chat_thread_client.send_read_receipt(message_id)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')

    def test_list_read_receipts(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id="1596823919339"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [{"chatMessageId": message_id}]})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        read_receipts = None
        try:
            read_receipts = chat_thread_client.list_read_receipts()
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for read_receipt_page in read_receipts.by_page():
            l = list(read_receipt_page)
            assert len(l) == 1


if __name__ == '__main__':
    unittest.main()
