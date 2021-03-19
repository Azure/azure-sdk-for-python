# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import time

from datetime import datetime
from msrest.serialization import TZ_UTC
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.chat import (
    ChatThreadClient,
    ChatThreadParticipant,
    ChatMessageType
)
from azure.communication.chat._shared.models import(
    CommunicationUserIdentifier
)
from unittest_helpers import mock_response

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

def _convert_datetime_to_utc_int(input):
    epoch = time.mktime(datetime(1970, 1, 1).timetuple())
    input_datetime_as_int = epoch - time.mktime(input.timetuple())
    return input_datetime_as_int

class TestChatThreadClient(unittest.TestCase):
    @classmethod
    @patch('azure.communication.identity._shared.user_credential.CommunicationTokenCredential')
    def setUpClass(cls, credential):
        credential.get_token = Mock(return_value=AccessToken(
            "some_token", _convert_datetime_to_utc_int(datetime.now().replace(tzinfo=TZ_UTC))
        ))
        TestChatThreadClient.credential = credential

    def test_update_topic(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        topic = "update topic"
        try:
            chat_thread_client.update_topic(topic=topic)
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
            content='hello world'
            sender_display_name='sender name'
            create_message_result = chat_thread_client.send_message(
                content=content,
                sender_display_name=sender_display_name)
            create_message_result_id = create_message_result.id
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        assert create_message_result_id == message_id

    def test_send_message_w_type(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False
        message_str = "Hi I am Bob."

        chat_message_types = [ChatMessageType.TEXT, ChatMessageType.HTML, "text", "html"]

        for chat_message_type in chat_message_types:

            def mock_send(*_, **__):
                return mock_response(status_code=201, json_payload={
                    "id": message_id,
                    "type": chat_message_type,
                    "sequenceId": "3",
                    "version": message_id,
                    "content": {
                        "message": message_str,
                        "topic": "Lunch Chat thread",
                        "participants": [
                            {
                                "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b",
                                "displayName": "Bob",
                                "shareHistoryTime": "2020-10-30T10:50:50Z"
                            }
                        ],
                        "initiator": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"
                    },
                    "senderDisplayName": "Bob",
                    "createdOn": "2021-01-27T01:37:33Z",
                    "senderId": "8:acs:46849534-eb08-4ab7-bde7-c36928cd1547_00000007-e155-1f06-1db7-3a3a0d00004b"
                })

            chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id,
                                                  transport=Mock(send=mock_send))

            try:
                content='hello world'
                sender_display_name='sender name'
                create_message_result = chat_thread_client.send_message(
                    content=content,
                    chat_message_type=chat_message_type,
                    sender_display_name=sender_display_name)
                create_message_result_id = create_message_result.id
            except:
                raised = True

            self.assertFalse(raised, 'Expected is no excpetion raised')
            assert create_message_result_id == message_id

    def test_send_message_w_invalid_type_throws_error(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False
        message_str = "Hi I am Bob."

        # the payload is irrelevant - it'll fail before
        def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                        "id": message_id
                    })
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        create_message_result = None

        chat_message_types = [ChatMessageType.PARTICIPANT_ADDED, ChatMessageType.PARTICIPANT_REMOVED,
                              ChatMessageType.TOPIC_UPDATED, "participant_added", "participant_removed", "topic_updated",
                              "ChatMessageType.TEXT", "ChatMessageType.HTML",
                              "ChatMessageType.PARTICIPANT_ADDED", "ChatMessageType.PARTICIPANT_REMOVED",
                              "ChatMessageType.TOPIC_UPDATED"]
        for chat_message_type in chat_message_types:
            try:
                content='hello world'
                sender_display_name='sender name'
                create_message_result = chat_thread_client.send_message(
                    content=content,
                    chat_message_type=chat_message_type,
                    sender_display_name=sender_display_name)
            except:
                raised = True

            self.assertTrue(raised, 'Expected is excpetion raised')


    def test_get_message(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        raised = False
        message_str = "Hi I am Bob."

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                        "id": message_id,
                        "type": "text",
                        "sequenceId": "3",
                        "version": message_id,
                        "content": {
                            "message": message_str,
                            "topic": "Lunch Chat thread",
                            "participants": [
                                {
                                    "communicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                        "deletedOn": "2021-01-27T01:37:33Z",
                        "editedOn": "2021-01-27T01:37:33Z"
                    })
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        message = None
        try:
            message = chat_thread_client.get_message(message_id)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        assert message.id == message_id
        assert message.content.message == message_str
        assert message.type == ChatMessageType.TEXT
        assert len(message.content.participants) > 0

    def test_list_messages(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id='1596823919339'
        message_str = "Hi I am Bob."
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [{
                        "id": message_id,
                        "type": "text",
                        "sequenceId": "3",
                        "version": message_id,
                        "content": {
                            "message": message_str,
                            "topic": "Lunch Chat thread",
                            "participants": [
                                {
                                    "communicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                        "deletedOn": "2021-01-27T01:37:33Z",
                        "editedOn": "2021-01-27T01:37:33Z"
                    }]})
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
        message_id = '1596823919339'
        message_str = "Hi I am Bob."

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "value": [
                    {
                        "id": message_id,
                        "type": "text",
                        "sequenceId": "2",
                        "version": message_id,
                        "content": {
                            "message": message_str,
                            "topic": "Lunch Chat thread",
                            "participants": [
                                {
                                    "communicationIdentifier": {"rawId": "string", "communicationUser": {
                                        "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                                "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                        "deletedOn": "2021-01-27T01:37:33Z",
                        "editedOn": "2021-01-27T01:37:33Z"
                    },
                    {
                        "id": message_id,
                        "type": "text",
                        "sequenceId": "3",
                        "version": message_id,
                        "content": {
                            "message": message_str,
                            "topic": "Lunch Chat thread",
                            "participants": [
                                {
                                    "communicationIdentifier": {"rawId": "string", "communicationUser": {
                                        "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                                    "displayName": "Bob",
                                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                                }
                            ],
                            "initiatorCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                                "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}}
                        },
                        "senderDisplayName": "Bob",
                        "createdOn": "2021-01-27T01:37:33Z",
                        "senderCommunicationIdentifier": {"rawId": "string", "communicationUser": {
                            "id": "8:acs:8540c0de-899f-5cce-acb5-3ec493af3800_0e59221d-0c1d-46ae-9544-c963ce56c10b"}},
                        "deletedOn": "2021-01-27T01:37:33Z",
                        "editedOn": "2021-01-27T01:37:33Z"
                    }
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
            return mock_response(status_code=204)
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

    def test_list_participants(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [
                {
                    "communicationIdentifier": {
                        "rawId": participant_id,
                        "communicationUser": {
                            "id": participant_id
                        }
                    },
                    "displayName": "Bob",
                    "shareHistoryTime": "2020-10-30T10:50:50Z"
                }
            ]})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        chat_thread_participants = None
        try:
            chat_thread_participants = chat_thread_client.list_participants()
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for chat_thread_participant_page in chat_thread_participants.by_page():
            l = list(chat_thread_participant_page)
            assert len(l) == 1
            l[0].user.id = participant_id

    def test_list_participants_with_results_per_page(self):
        thread_id = "19:81181a8abbf54b5695f87a0042ddcba9@thread.v2"
        participant_id_1 = "8:acs:9b665d53-8164-4923-ad5d-5e983b07d2e7_00000006-5399-552c-b274-5a3a0d0000dc"
        participant_id_2 = "8:acs:9b665d53-8164-4923-ad5d-5e983b07d2e7_00000006-9d32-35c9-557d-5a3a0d0002f1"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "value": [
                    {
                        "communicationIdentifier": {
                            "rawId": participant_id_1,
                            "communicationUser": {
                                "id": participant_id_1
                            }
                        },
                        "displayName": "Bob",
                        "shareHistoryTime": "2020-10-30T10:50:50Z"
                    },
                    {
                        "communicationIdentifier": {
                            "rawId": participant_id_2,
                            "communicationUser": {
                                "id": participant_id_2
                            }
                        },
                        "displayName": "Bob",
                        "shareHistoryTime": "2020-10-30T10:50:50Z"
                    }
                ]})

        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id,
                                              transport=Mock(send=mock_send))

        chat_thread_participants = None
        try:
            chat_thread_participants = chat_thread_client.list_participants(results_per_page=2)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for chat_thread_participant_page in chat_thread_participants.by_page():
            l = list(chat_thread_participant_page)
            assert len(l) == 2


    def test_add_participants(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        new_participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=201)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        new_participant = ChatThreadParticipant(
                user=CommunicationUserIdentifier(new_participant_id),
                display_name='name',
                share_history_time=datetime.utcnow())
        participants = [new_participant]

        try:
            result = chat_thread_client.add_participants(participants)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertTrue(len(result) == 0)

    def test_add_participants_w_failed_participants_returns_nonempty_list(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        new_participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False
        error_message = "some error message"

        def mock_send(*_, **__):
            return mock_response(status_code=201,json_payload={
                "invalidParticipants": [
                    {
                        "code": "string",
                        "message": error_message,
                        "target": new_participant_id,
                        "details": []
                    }
                ]
            })
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        new_participant = ChatThreadParticipant(
                user=CommunicationUserIdentifier(new_participant_id),
                display_name='name',
                share_history_time=datetime.utcnow())
        participants = [new_participant]

        try:
            result = chat_thread_client.add_participants(participants)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertTrue(len(result) == 1)

        failed_participant = result[0][0]
        communication_error = result[0][1]

        self.assertEqual(new_participant.user.identifier, failed_participant.user.identifier)
        self.assertEqual(new_participant.display_name, failed_participant.display_name)
        self.assertEqual(new_participant.share_history_time, failed_participant.share_history_time)
        self.assertEqual(error_message, communication_error.message)


    def test_remove_participant(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        participant_id="8:acs:57b9bac9-df6c-4d39-a73b-26e944adf6ea_9b0110-08007f1041"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=204)
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        try:
            chat_thread_client.remove_participant(user=CommunicationUserIdentifier(participant_id))
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
            return mock_response(status_code=200)
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
            return mock_response(status_code=200, json_payload={
                "value": [
                    {
                        "chatMessageId": message_id,
                        "senderCommunicationIdentifier": {
                            "rawId": "string",
                            "communicationUser": {
                                "id": "string"
                            }
                        }
                    }
                ]
            })
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

    def test_list_read_receipts_with_results_per_page(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        message_id_1="1596823919339"
        message_id_2="1596823919340"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "value": [
                    {
                        "chatMessageId": message_id_1,
                        "senderCommunicationIdentifier": {
                            "rawId": "string",
                            "communicationUser": {
                                "id": "string"
                            }
                        }
                    },
                    {
                        "chatMessageId": message_id_2,
                        "senderCommunicationIdentifier": {
                            "rawId": "string",
                            "communicationUser": {
                                "id": "string"
                            }
                        }
                    }
                ]})
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        read_receipts = None
        try:
            read_receipts = chat_thread_client.list_read_receipts(results_per_page=2)
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        for read_receipt_page in read_receipts.by_page():
            l = list(read_receipt_page)
            assert len(l) == 2

    def test_get_properties(self):
        thread_id = "19:bcaebfba0d314c2aa3e920d38fa3df08@thread.v2"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": thread_id,
                "topic": "Lunch Chat thread",
                "createdOn": "2020-10-30T10:50:50Z",
                "deletedOn": "2020-10-30T10:50:50Z",
                "createdByCommunicationIdentifier": {"rawId": "string", "communicationUser": {"id": "string"}}
                })
        chat_thread_client = ChatThreadClient("https://endpoint", TestChatThreadClient.credential, thread_id, transport=Mock(send=mock_send))

        get_thread_result = None
        try:
            get_thread_result = chat_thread_client.get_properties()
        except:
            raised = True

        self.assertFalse(raised, 'Expected is no excpetion raised')
        assert get_thread_result.id == thread_id


if __name__ == '__main__':
    unittest.main()
