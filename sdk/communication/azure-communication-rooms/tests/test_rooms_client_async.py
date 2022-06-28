# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import aiounittest
import datetime

from azure.core.credentials import AccessToken
from azure.communication.rooms.aio import RoomsClient
from azure.communication.rooms import (
    RoomParticipant,
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel
)
from unittest_helpers import mock_response

from unittest.mock import Mock, patch

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    async def get_token(self, *args):
        return self.token

class TestRoomsClient(aiounittest.AsyncTestCase):
    room_id = "999126454"
    valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
    valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
    raw_id = "8:acs:abcd"
    room_participants = [RoomParticipant(
        communication_identifier=CommunicationIdentifierModel(
            raw_id=raw_id,
            communication_user=CommunicationUserIdentifierModel(id=raw_id)
        ),
        role='Attendee'
    )]
    json_participant = {
        "communicationIdentifier": {
            "rawId": raw_id,
            "communicationUser": {"id": raw_id}
        },
        "role": "Attendee"
    }

    async def test_create_room(self):
        raised = False

        async def mock_send(*_, **__):
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
            response = await rooms_client.create_room(valid_from=self.valid_from, valid_until=self.valid_until, participants=self.room_participants)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(self.room_participants, response.participants)

    async def test_update_room(self):
        raised = False

        async def mock_send(*_, **__):
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
            response = await rooms_client.update_room(
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

    async def test_delete_room_raises_error(self):
        raised = False
        async def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))
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
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": self.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": self.valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": []
            })

        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = await rooms_client.get_room(room_id=self.room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(self.room_id, response.id)
        self.assertEqual(self.valid_from, response.valid_from)
        self.assertEqual(self.valid_until, response.valid_until)
        self.assertListEqual(response.participants, [])

    async def test_get_room_raises_error(self):
        raised = False
        async def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))
        try:
            await rooms_client.get_room(room_id=self.room_id)
        except:
            raised = True
        assert raised == True