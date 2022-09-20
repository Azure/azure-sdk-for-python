# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import datetime

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import (
    RoomsClient,
    RoomParticipant,
    RoomJoinPolicy,
    RoleType
)
from azure.communication.rooms._shared.models import CommunicationUserIdentifier, UnknownIdentifier
from unittest_helpers import mock_response

from unittest.mock import Mock

class TestRoomsClient(unittest.TestCase):
    room_id = "999126454"
    valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
    valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
    raw_id = "8:acs:abcd"
    room_join_policy = RoomJoinPolicy.INVITE_ONLY
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
                "roomJoinPolicy": self.room_join_policy,
                "participants": [self.json_participant]
            })
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.create_room(
                valid_from=self.valid_from,
                valid_until=self.valid_until,
                room_join_policy=self.room_join_policy,
                participants=[self.room_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertEqual(self.room_join_policy, response.room_join_policy)
        self.assertListEqual([self.room_participant], response.participants)

    def test_update_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "roomJoinPolicy": self.room_join_policy,
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.update_room(
                room_id=self.room_id,
                valid_from=self.valid_from,
                valid_until=self.valid_until,
                room_join_policy=self.room_join_policy)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertEqual(self.room_join_policy, response.room_join_policy)
        self.assertListEqual(response.participants, [])

    def test_delete_room_raises_error(self):
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        self.assertRaises(HttpResponseError, rooms_client.delete_room, room_id=self.room_id)

    def test_get_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "roomJoinPolicy": self.room_join_policy,
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

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
        self.assertEqual(self.room_join_policy, response.room_join_policy)
        self.assertListEqual(response.participants, [])

    def test_get_room_raises_error(self):
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

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
                "participants": [self.json_participant, additional_participant_json]
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.add_participants(room_id=self.room_id, participants=[additional_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(None, response)

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
                "participants": [updated_participant_json]
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None

        try:
            response = rooms_client.update_participants(room_id=self.room_id, participants=[updated_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(None, response)

    def test_remove_participants(self):
        raised = False
        user_to_remove = CommunicationUserIdentifier(self.raw_id)

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.remove_participants(room_id=self.room_id, communication_identifiers=[user_to_remove])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(None, response)

    def test_get_participants(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "participants": [self.json_participant]
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.get_participants(room_id=self.room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertListEqual(response.participants, [self.room_participant])

    def test_invalid_datetime_raises_valueError(self):
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=None)

        # verify value error on create room call
        self.assertRaises(ValueError, rooms_client.create_room, valid_from="dummy", valid_until=self.valid_until)
        self.assertRaises(ValueError, rooms_client.create_room, valid_from=self.valid_from, valid_until="dummy")
        self.assertRaises(ValueError, rooms_client.create_room, valid_from="dummy", valid_until="dummy")

        # verify ValueError on update_room calls
        self.assertRaises(ValueError, rooms_client.update_room, room_id=self.room_id, valid_from="dummy", valid_until=self.valid_until)
        self.assertRaises(ValueError, rooms_client.update_room, room_id=self.room_id, valid_from=self.valid_from, valid_until="dummy")
        self.assertRaises(ValueError, rooms_client.update_room, room_id=self.room_id, valid_from="dummy", valid_until="dummy")
