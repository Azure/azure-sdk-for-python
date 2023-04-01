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
    ParticipantRole,
    InvitedRoomParticipant,
    RemoveParticipantsResult,
    UpsertParticipantsResult
)
from azure.communication.rooms._shared.models import CommunicationUserIdentifier, UnknownIdentifier
from unittest_helpers import mock_response

from unittest.mock import Mock

class TestRoomsClient(unittest.TestCase):
    room_id = "999126454"
    valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
    valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
    raw_id = "8:acs:abcd"
    room_participant = InvitedRoomParticipant(
        communication_identifier=CommunicationUserIdentifier(
            id=raw_id
        ),
        role=ParticipantRole.PRESENTER
    )
    json_participant = {
        "rawId": raw_id,
        "role": "Presenter"
    }

    def test_create_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                "id": self.room_id,
                "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")
            })
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.create_room(
                valid_from=self.valid_from,
                valid_until=self.valid_until,
                participants=[self.room_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)

    def test_update_room(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.update_room(
                room_id=self.room_id,
                valid_from=self.valid_from,
                valid_until=self.valid_until
            )
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)

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
                "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.get_room(room_id=self.room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)

    def test_get_room_raises_error(self):
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        self.assertRaises(HttpResponseError, rooms_client.get_room, room_id=self.room_id)

    def test_list_rooms(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "value": [{
                    "id": self.room_id,
                    "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                    "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")
                }]
            })


        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        rooms = None
        try:
            rooms = rooms_client.list_rooms()
        except:
            raised = True
            raise
        items = []
        for page in rooms.by_page():
            for room in page:
                items.append(room)
        assert len(items) > 0
        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, items[0].id)
        self.assertEqual(self.valid_from, items[0].valid_from)
        self.assertEqual(self.valid_until, items[0].valid_until)

    def test_upsert_participants(self):
        raised = False
        updated_participant = InvitedRoomParticipant(
            communication_identifier=CommunicationUserIdentifier(
                id=self.raw_id
            ),
            role=''
        )

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={})

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        response = None

        try:
            response = rooms_client.upsert_participants(room_id=self.room_id, participants=[updated_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        assert isinstance(response, UpsertParticipantsResult)

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

        self.assertFalse(raised, 'Expected is no exception raised')
        assert isinstance(response, RemoveParticipantsResult)

    def test_list_participants(self):
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "value": [self.json_participant]
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        participants = None
        try:
            participants = rooms_client.list_participants(room_id=self.room_id)
        except:
            raised = True
            raise

        items = []
        for page in participants.by_page():
            for participant in page:
                items.append(participant)
        assert len(items) > 0
        self.assertFalse(raised, 'Expected is no exception raised')