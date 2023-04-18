# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# cSpell:ignore aiounittest
import aiounittest
import datetime

from azure.core.credentials import AzureKeyCredential
from azure.communication.rooms.aio import RoomsClient
from azure.communication.rooms import (
    ParticipantRole,
    RoomParticipant,
    UpsertParticipantsResult,
    RemoveParticipantsResult
)
from azure.communication.rooms._shared.models import CommunicationUserIdentifier, UnknownIdentifier
from unittest_helpers import mock_response

from unittest.mock import Mock

class TestRoomsClient(aiounittest.AsyncTestCase):
    room_id = "999126454"
    valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
    valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
    raw_id = "8:acs:abcd"
    room_participant = RoomParticipant(
        communication_identifier=CommunicationUserIdentifier(
            id=raw_id
        ),
        role=ParticipantRole.ATTENDEE
    )
    json_participant = {
        "rawId": raw_id,
        "role": "Attendee"
    }

    async def test_create_room(self):
        raised = False

        async def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                "id": self.room_id,
                "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = await rooms_client.create_room(valid_from=self.valid_from, valid_until=self.valid_until, participants=[self.room_participant])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)

    async def test_update_room(self):
        raised = False

        async def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = await rooms_client.update_room(
                room_id=self.room_id,
                valid_from=self.valid_from,
                valid_until=self.valid_until)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)

    async def test_list_rooms(self):
        raised = False

        async def mock_send(*_, **__):
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
        async for page in rooms.by_page():
             async for room in page:
                items.append(room)
        assert len(items) > 0
        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, items[0].id)
        self.assertEqual(self.valid_from, items[0].valid_from)
        self.assertEqual(self.valid_until, items[0].valid_until)

    async def test_delete_room_raises_error(self):
        raised = False
        async def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            await rooms_client.delete_room(room_id=self.room_id)
        except:
            raised = True
        assert raised == True

    async def test_get_room(self):
        raised = False

        async def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": self.room_id,
                "createdAt": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = await rooms_client.get_room(room_id=self.room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)

    async def test_get_room_raises_error(self):
        raised = False
        async def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            await rooms_client.get_room(room_id=self.room_id)
        except:
            raised = True
        assert raised == True

    async def test_upsert_participants(self):
        raised = False
        updated_participant = RoomParticipant(
            communication_identifier=CommunicationUserIdentifier(
                id=self.raw_id
            ),
            role=""
        )

        async def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "participants": [self.json_participant]
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = await rooms_client.upsert_participants(room_id=self.room_id, participants=[updated_participant])
        except:
            raised = True
            raise
        self.assertFalse(raised, 'Expected is no exception raised')
        assert isinstance(response, UpsertParticipantsResult)

    async def test_remove_participants(self):
        raised = False
        user_to_remove = CommunicationUserIdentifier(self.raw_id)

        async def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))

        response = None
        try:
            response = await rooms_client.remove_participants(room_id=self.room_id, communication_identifiers=[user_to_remove])
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no exception raised')
        assert isinstance(response, RemoveParticipantsResult)

    async def test_list_participants(self):
        raised = False

        async def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={"value": [self.json_participant]})

        rooms_client = RoomsClient("https://endpoint", AzureKeyCredential("fakeCredential=="), transport=Mock(send=mock_send))
        try:
            participants = rooms_client.list_participants(room_id=self.room_id)
        except:
            raised = True
            raise
        items = []
        async for page in participants.by_page():
             async for participant in page:
                items.append(participant)
        assert len(items) > 0
        self.assertEqual(self.room_participant.communication_identifier, items[0].communication_identifier)
        self.assertEqual(self.room_participant.communication_identifier.raw_id, items[0].communication_identifier.raw_id)
        self.assertEqual(self.room_participant.role, items[0].role)
        self.assertFalse(raised, 'Expected is no exception raised')
