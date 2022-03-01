# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from turtle import update
import pytest
from datetime import datetime, timezone, tzinfo
from dateutil.relativedelta import relativedelta

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms import RoomsClient
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)

from azure.communication.rooms import (
    RoomsClient,
    RoomRequest
)

from _shared.utils import get_http_logging_policy


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class RoomsClientTest(CommunicationTestCase):
    def __init__(self, method_name):
        super(RoomsClientTest, self).__init__(method_name)

    def setUp(self):
        super(RoomsClientTest, self).setUp()
        if self.is_playback():
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["participants","invalid_participants"])])
        else:
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["participants", "invalid_participants"]),
                ResponseReplacerProcessor(keys=[self._resource_name])])
        # create multiple users users
        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)
        self.users = {
            "john" : self.identity_client.create_user(),
            "fred" : self.identity_client.create_user(),
            "chris" : self.identity_client.create_user()
        }
        self.rooms_client = RoomsClient.from_connection_string(
            self.connection_str, 
            http_logging_policy=get_http_logging_policy()
        )
    
    def tearDown(self):
        super(RoomsClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            for user in self.users.values():
                self.identity_client.delete_user(user)

    def test_create_room_no_attributes(self):
        room_request = RoomRequest()
        
        response = self.rooms_client.create_room(room_request=room_request)     
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
    
    @pytest.mark.live_test_only
    def test_create_room_only_validFrom(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        room_request = RoomRequest(valid_from=valid_from)
        response = self.rooms_client.create_room(room_request=room_request)     
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
        
        # verify room is valid for 180 days
        valid_until = datetime.utcnow() + relativedelta(days=+180)
        self.assertEqual(valid_until.date(), response.valid_until.date())

    @pytest.mark.live_test_only
    def test_create_room_only_validUntil(self):
        # room attributes
        valid_until =  datetime.now() + relativedelta(months=+3)
        room_request = RoomRequest(valid_until=valid_until)
        
        response = self.rooms_client.create_room(room_request=room_request)     
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
        self.verify_successful_room_response(response=response, valid_until=valid_until)

    @pytest.mark.live_test_only
    def test_create_room_only_participants(self):
        # room with no attributes
        room_request = RoomRequest()
        
        # add john and chris to room
        room_request.add_participant(self.users["john"])
        room_request.add_participant(self.users["chris"])
        
        response = self.rooms_client.create_room(room_request=room_request)
        participants = {
            self.users["john"].properties["id"] : {},
            self.users["chris"].properties["id"] : {}
        }
        
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
        
        self.verify_successful_room_response(response=response, participants=participants)

    def test_create_room_validUntil_7Months(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+7)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(room_request=room_request)     
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_create_room_validFrom_7Months(self):
        # room attributes
        valid_from = datetime.now() + relativedelta(months=+7)
        room_request = RoomRequest(valid_from=valid_from)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(room_request=room_request)     

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_create_room_correct_timerange(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+4)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        response = self.rooms_client.create_room(room_request=room_request)     
        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    @pytest.mark.live_test_only
    def test_create_room_none_participant(self):
        # room attributes
        room_request = RoomRequest()
        
        # add john and chris to room
        room_request.add_participant(self.users["john"])
        room_request.remove_participant(self.users["chris"])
        
        response = self.rooms_client.create_room(room_request=room_request)
        participants = {
            self.users["john"].properties["id"] : {},
            self.users["chris"].properties["id"] : {}
        }
        
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
        
        self.verify_successful_room_response(response=response, participants=participants)

    def test_create_room_incorretMri(self):
        # room attributes
        participants = {
            "wrong_mir" : {},
            self.users["john"].properties["id"] : {}
        }
        room_request = RoomRequest(participants=participants)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(room_request=room_request)     

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_create_room_all_attributes(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+4)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        # add john to room
        room_request.add_participant(self.users["john"])
        
        response = self.rooms_client.create_room(room_request=room_request)
        participants = {
            self.users["john"].properties["id"] : {}
        }
        
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
        
        self.verify_successful_room_response(
            response=response, valid_from=valid_from, valid_until=valid_until, participants=participants)

    @pytest.mark.live_test_only
    def test_get_room(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+2)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        # add john to room
        room_request.add_participant(self.users["john"])
        
        # create a room first
        create_response = self.rooms_client.create_room(room_request=room_request)
        participants = {
            self.users["john"].properties["id"] : {}
        }

        get_response = self.rooms_client.get_room(room_id=create_response.id)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=get_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id, participants=participants)

    def test_get_invalid_room(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.get_room(room_id="89469124725336262")

        # Resource not found    
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    def test_delete_invalid_room(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.delete_room(room_id="78469124725336262")

        # Resource not found    
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    def test_update_room_only_ValidFrom(self):
        # room with no attributes
        create_request = RoomRequest()  
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # update room attributes
        valid_from =  datetime.now() + relativedelta(months=+2)
        update_request = RoomRequest(valid_from=valid_from)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_only_ValidUntil(self):
        # room with no attributes
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # update room attributes
        valid_until =  datetime.now() + relativedelta(months=+2)
        update_request = RoomRequest(valid_until=valid_until)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
            
    def test_update_room_ValidFrom_7Months(self):
        # room with no attributes
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # update room attributes
        valid_from =  datetime.now() + relativedelta(months=+7)
        update_request = RoomRequest(valid_from=valid_from)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_ValidUntil_7Months(self):
        # room with no attributes
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # update room attributes
        valid_until =  datetime.now() + relativedelta(months=+7)
        update_request = RoomRequest(valid_until=valid_until)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_incorrect_timerange(self):
        # room with no attributes
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)

        # update room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until =  datetime.now() + relativedelta(months=+7)
        update_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_update_room_correct_timerange(self):
        # room with no attributes
        create_request = RoomRequest()        
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # update room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until =  datetime.now() + relativedelta(months=+4)
        update_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        update_response = self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @pytest.mark.live_test_only
    def test_update_room_add_participant(self):
        # room with no attributes
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # update room attributes
        update_request = RoomRequest()
        update_request.add_participant(self.users["john"])

        update_response = self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        participants = {
            self.users["john"].properties["id"] : {}
        }
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=participants)

    @pytest.mark.live_test_only
    def test_update_room_remove_participant(self):
        # room with participant
        create_request = RoomRequest()

        # add john and chris to room
        create_request.add_participant(self.users["john"])
        create_request.add_participant(self.users["chris"])
        create_response = self.rooms_client.create_room(room_request=create_request)

        # update room attributes                
        update_request = RoomRequest()
        update_request.remove_participant(self.users["chris"])

        update_response = self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        participants = {
            self.users["john"].properties["id"] : {}
        }
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=participants)

    @pytest.mark.live_test_only
    def test_update_room_add_remove_participant(self):
        create_request = RoomRequest()
        # add chris to the room
        create_request.add_participant(self.users["chris"])
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # add john to room and remove chris
        update_request = RoomRequest()
        update_request.add_participant(self.users["john"])
        update_request.remove_participant(self.users["chris"])

        update_response = self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        participants = {
            self.users["john"].properties["id"] : {}
        }
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=participants)

    def test_update_room_incorretMri(self):
        # room with no attributes
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)

        participants = {
            "wrong_mir" : {},
            self.users["john"].properties["id"] : {}
        }
        
        # update room attributes
        update_request = RoomRequest(participants=participants)
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id,room_request=update_request)     

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_update_room_clear_participant_dict(self):
        create_request = RoomRequest()
        # add john and chris to the room
        create_request.add_participant(self.users["chris"])
        create_request.add_participant(self.users["john"])
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # clear participants
        update_request = RoomRequest(participants={})
        update_response = self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
        
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants={})

    def test_update_room_incorrect_roomId(self):
        # try to update room with random room_id
        update_request = RoomRequest()
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=78469124725336262,room_request=update_request)     

        #  assert error is Resource not found
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None
    
    def test_update_room_deleted_room(self):
        # create a room -> delete it -> try to update it
        self.rooms_client = RoomsClient.from_connection_string(
            self.connection_str, 
            http_logging_policy=get_http_logging_policy()
        )
        # create default room
        create_request = RoomRequest()
        create_response = self.rooms_client.create_room(room_request=create_request)
        
        # delete the room
        self.rooms_client.delete_room(room_id=create_response.id)
        
        update_request = RoomRequest()
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id,room_request=update_request)     

        #  assert error is Resource not found
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None
    
    def verify_successful_room_response(self, response, valid_from=None, valid_until=None, room_id=None, participants=None):
        if room_id is not None:
            self.assertEqual(room_id, response.id)
        if valid_from is not None:
            self.assertEqual(valid_from.replace(tzinfo=None), response.valid_from.replace(tzinfo=None))
        if valid_until is not None:
            self.assertEqual(valid_until.replace(tzinfo=None), response.valid_until.replace(tzinfo=None))
        if participants is not None:
            self.assertDictEqual(participants, response.participants)