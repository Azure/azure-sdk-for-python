# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from turtle import update
import pytest
from datetime import datetime, timezone, tzinfo
from dateutil.relativedelta import relativedelta

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms.aio import RoomsClient
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import (
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from azure.communication.rooms._models import (
    RoomRequest
)

from _shared.utils import get_http_logging_policy

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class RoomsClientTestAsync(AsyncCommunicationTestCase):
    def __init__(self, method_name):
        super(RoomsClientTestAsync, self).__init__(method_name)

    def setUp(self):
        super(RoomsClientTestAsync, self).setUp()
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
        super(RoomsClientTestAsync, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            for user in self.users.values():
                self.identity_client.delete_user(user)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_no_attributes_async(self):
        room_request = RoomRequest()
        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)     
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_only_validFrom_async(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        room_request = RoomRequest(valid_from=valid_from)
        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)     
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
        
            # verify room is valid for 180 days
            valid_until = datetime.now() + relativedelta(days=+180)
            self.assertEqual(valid_until.date(), response.valid_until.date())

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_only_validUntil_async(self):
        # room attributes
        valid_until =  datetime.now() + relativedelta(months=+3)
        room_request = RoomRequest(valid_until=valid_until)
        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)     
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response, valid_until=valid_until)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_only_participants_async(self):
        # room with no attributes
        room_request = RoomRequest()
        
        # add john and chris to room
        room_request.add_participant(self.users["john"])
        room_request.add_participant(self.users["chris"])
        
        participants = {
            self.users["john"].properties["id"] : {},
            self.users["chris"].properties["id"] : {}
        }
        
        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)
            
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response, participants=participants)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_validUntil_7Months_async(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+7)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(room_request=room_request)     
                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_validFrom_7Months_async(self):
        # room attributes
        valid_from = datetime.now() + relativedelta(months=+7)
        room_request = RoomRequest(valid_from=valid_from)
        
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(room_request=room_request)     
                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_correct_timerange_async(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+4)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)

        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)     
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until)
   
    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_none_participant_async(self):
        # room attributes
        room_request = RoomRequest()
        
        # add john and chris to room
        room_request.add_participant(self.users["john"])
        room_request.remove_participant(self.users["chris"])
        participants = {
            self.users["john"].properties["id"] : {},
            self.users["chris"].properties["id"] : {}
        }
        
        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)
            
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)    
            self.verify_successful_room_response(response=response, participants=participants)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_incorretMri_async(self):
        # room attributes
        participants = {
            "wrong_mir" : {},
            self.users["john"].properties["id"] : {}
        }
        room_request = RoomRequest(participants=participants)
        
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(room_request=room_request)     

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_all_attributes_async(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+4)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        # add john to room
        room_request.add_participant(self.users["john"])
        participants = {
            self.users["john"].properties["id"] : {}
        }
        
        async with self.rooms_client:
            response = await self.rooms_client.create_room(room_request=room_request)
            
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(
            response=response, valid_from=valid_from, valid_until=valid_until, participants=participants)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_room_async(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+2)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        
        # add john to room
        room_request.add_participant(self.users["john"])
        
        participants = {
            self.users["john"].properties["id"] : {}
        }
        async with self.rooms_client:
            # create a room first
            create_response = await self.rooms_client.create_room(room_request=room_request)

            get_response = await self.rooms_client.get_room(room_id=create_response.id)
            
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=get_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id, participants=participants)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_get_invalid_room_async(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.get_room(room_id="89469124725336262")

                # Resource not found    
                assert str(ex.value.status_code) == "404"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_invalid_room_async(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.delete_room(room_id="78469124725336262")

                # Resource not found    
                assert str(ex.value.status_code) == "404"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_only_ValidFrom_async(self):
        # room with no attributes
        create_request = RoomRequest()  
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
        
            # update room attributes
            valid_from =  datetime.now() + relativedelta(months=+2)
            update_request = RoomRequest(valid_from=valid_from)
            
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
                
                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_only_ValidUntil_async(self):
        # room with no attributes
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
        
            # update room attributes
            valid_until =  datetime.now() + relativedelta(months=+2)
            update_request = RoomRequest(valid_until=valid_until)
            
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
                
                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_ValidFrom_7Months_async(self):
        # room with no attributes
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
        
            # update room attributes
            valid_from =  datetime.now() + relativedelta(months=+7)
            update_request = RoomRequest(valid_from=valid_from)
            
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
                
                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_ValidUntil_7Months_async(self):
        # room with no attributes
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
            
            # update room attributes
            valid_until =  datetime.now() + relativedelta(months=+7)
            update_request = RoomRequest(valid_until=valid_until)
            
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
                
                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_incorrect_timerange_async(self):
        # room with no attributes
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)

            # update room attributes
            valid_from =  datetime.now() + relativedelta(days=+3)
            valid_until =  datetime.now() + relativedelta(months=+7)
            update_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
            
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
                
                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_correct_timerange_async(self):
        # room with no attributes
        create_request = RoomRequest()        
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
            
            # update room attributes
            valid_from =  datetime.now() + relativedelta(days=+3)
            valid_until =  datetime.now() + relativedelta(months=+4)
            update_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
            
            update_response = await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
            
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=update_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_add_participant_async(self):
        # room with no attributes
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
            
            # update room attributes
            update_request = RoomRequest()
            update_request.add_participant(self.users["john"])

            update_response = await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
            participants = {
                self.users["john"].properties["id"] : {}
            }
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=update_response,
                valid_from=create_response.valid_from,
                valid_until=create_response.valid_until,
                room_id=create_response.id,
                participants=participants)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_remove_participant_async(self):
        # room with participant
        create_request = RoomRequest()

        # add john and chris to room
        create_request.add_participant(self.users["john"])
        create_request.add_participant(self.users["chris"])
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)

            # update room attributes                
            update_request = RoomRequest()
            update_request.remove_participant(self.users["chris"])

            update_response = await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
            participants = {
                self.users["john"].properties["id"] : {}
            }
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=update_response,
                valid_from=create_response.valid_from,
                valid_until=create_response.valid_until,
                room_id=create_response.id,
                participants=participants)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_add_remove_participant_async(self):
        create_request = RoomRequest()
        # add chris to the room
        create_request.add_participant(self.users["chris"])
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
            
            # add john to room and remove chris
            update_request = RoomRequest()
            update_request.add_participant(self.users["john"])
            update_request.remove_participant(self.users["chris"])

            update_response = await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
            participants = {
                self.users["john"].properties["id"] : {}
            }
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=update_response,
                valid_from=create_response.valid_from,
                valid_until=create_response.valid_until,
                room_id=create_response.id,
                participants=participants)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_incorretMri_async(self):
        # room with no attributes
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)

            participants = {
                "wrong_mir" : {},
                self.users["john"].properties["id"] : {}
            }
            
            # update room attributes
            update_request = RoomRequest(participants=participants)
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id,room_request=update_request)     

            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_clear_participant_dict_async(self):
        create_request = RoomRequest()
        # add john and chris to the room
        create_request.add_participant(self.users["chris"])
        create_request.add_participant(self.users["john"])
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
            
            # clear participants
            update_request = RoomRequest(participants={})
            update_response = await self.rooms_client.update_room(room_id=create_response.id, room_request=update_request)
            
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=update_response,
                valid_from=create_response.valid_from,
                valid_until=create_response.valid_until,
                room_id=create_response.id,
                participants={})

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_incorrect_roomId_async(self):
        # try to update room with random room_id
        update_request = RoomRequest()
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.update_room(room_id=78469124725336262,room_request=update_request)     

                #  assert error is Resource not found
                assert str(ex.value.status_code) == "404"
                assert ex.value.message is not None
    
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_deleted_room_async(self):
        # create a room -> delete it -> try to update it
        self.rooms_client = RoomsClient.from_connection_string(
            self.connection_str, 
            http_logging_policy=get_http_logging_policy()
        )
        # create default room
        create_request = RoomRequest()
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(room_request=create_request)
            
            # delete the room
            await self.rooms_client.delete_room(room_id=create_response.id)
            
            update_request = RoomRequest()
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id,room_request=update_request)     

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