# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import datetime

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import (
    RoomsClient,
    RoomParticipant,
    RoleType
)
from azure.communication.rooms._shared.models import CommunicationUserIdentifier, UnknownIdentifier
from unittest_helpers import mock_response

from unittest.mock import Mock

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class TestRoomsClient(unittest.TestCase):
    room_id = "999126454"
    valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
    valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
    raw_id = "8:acs:abcd"
    room_participant = RoomParticipant(
        communication_identifier=CommunicationUserIdentifier(
            id=raw_id
        ),
        role=RoleType.PRESENTER
    )
    json_participant = {
        "communicationIdentifier": {
            "rawId": raw_id,
            "communicationUser": {"id": raw_id}
        },
        "role": "Presenter"
    }

    def test_create_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": [self.json_participant]
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.create_room(
                valid_from=self.valid_from,
                valid_until=self.valid_until,
                participants=[self.room_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual([self.room_participant], response.participants)

    def test_update_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.update_room(
                room_id=self.room_id,
                valid_from=self.valid_from,
                valid_until=self.valid_until)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(response.participants, [])

    def test_delete_room_raises_error(self):
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        self.assertRaises(HttpResponseError, rooms_client.delete_room, room_id=self.room_id)

    def test_get_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.get_room(room_id=self.room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(response.participants, [])

    def test_get_room_raises_error(self):
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        self.assertRaises(HttpResponseError, rooms_client.get_room, room_id=self.room_id)

    def test_add_participants(self):
        raised = False
        additional_id = "8:acs:abcde"
        additional_participant_json = {
            "communicationIdentifier": {
                "rawId": additional_id
            },
            "role": ""
        }
        additional_participant = RoomParticipant(
            communication_identifier=UnknownIdentifier(additional_id),
            role=''
        )

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": [self.json_participant, additional_participant_json]
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.add_participants(room_id=self.room_id, participants=[additional_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(response.participants, [self.room_participant, additional_participant])

    def test_update_participants(self):
        raised = False
        updated_participant_json = {
            "communicationIdentifier": {
                "rawId": self.raw_id,
                "communicationUser": {"id": self.raw_id}
            },
            "role": ""
        }
        updated_participant = RoomParticipant(
            communication_identifier=CommunicationUserIdentifier(
                id=self.raw_id
            ),
            role=''
        )

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": [updated_participant_json]
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.update_participants(room_id=self.room_id, participants=[updated_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(response.participants, [updated_participant])

    def test_remove_participants(self):
        raised = False
        user_to_remove = CommunicationUserIdentifier(self.raw_id)

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.remove_all_participants(room_id=self.room_id, participants=[user_to_remove])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(response.participants, [])

    def test_get_participants(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "participants": [self.json_participant]
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.get_participants(room_id=self.room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertListEqual(response.participants, [self.room_participant])
