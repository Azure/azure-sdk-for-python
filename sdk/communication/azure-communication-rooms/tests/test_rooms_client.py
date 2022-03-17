# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import datetime

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import RoomsClient, RoomParticipant
from unittest_helpers import mock_response

from unittest.mock import Mock, patch

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class TestRoomsClient(unittest.TestCase):
    def test_create_room(self):
        room_id = "999126454"
        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
        valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
        raised = False
        participants = {}
        participants["8:acs:abcd"] = {}
        

        def mock_send(*_, **__):
            return mock_response(status_code=201, json_payload={
                "room": {
                    "id": room_id,
                    "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                    "validFrom": valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "validUntil": valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "participants": participants
                }
            })
            
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, participants=participants)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(room_id, response.id)
        self.assertEqual(valid_from, response.valid_from)
        self.assertEqual(valid_until, response.valid_until)
        self.assertDictEqual(participants, response.participants)
    
    def test_update_room(self):
        room_id = "999126454"
        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
        valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "room": {
                    "id": room_id,
                    "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                    "validFrom": valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "validUntil": valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "participants": {}
                }
            })
            
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))
        response = None
        try:
            response = rooms_client.update_room(room_id=room_id, valid_from=valid_from, valid_until=valid_until) 
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(room_id, response.id)
        self.assertEqual(valid_from, response.valid_from)
        self.assertEqual(valid_until, response.valid_until)
        self.assertDictEqual(response.participants, {})
    
    def test_delete_room_raises_error(self):
        room_id = "999126454"
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        self.assertRaises(HttpResponseError, rooms_client.delete_room, room_id=room_id)
    
    def test_get_room(self):
        room_id = "999126454"
        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 0)
        valid_until = datetime.datetime(2022, 4, 25, 4, 34, 0)
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=200, json_payload={
                "id": room_id,
                "createdDateTime": "2022-08-28T01:38:19.0359921+00:00",
                "validFrom": valid_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "validUntil": valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "participants": {}
            })
            
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        response = None
        try:
            response = rooms_client.get_room(room_id=room_id)
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(room_id, response.id)
        self.assertEqual(valid_from, response.valid_from)
        self.assertEqual(valid_until, response.valid_until)
        self.assertDictEqual(response.participants, {})

    def test_get_room_raises_error(self):
        room_id = "999126454"
        def mock_send(*_, **__):
            return mock_response(status_code=404, json_payload={"msg": "some error"})
        rooms_client = RoomsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        self.assertRaises(HttpResponseError, rooms_client.get_room, room_id=room_id)