# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import sys

from datetime import datetime
from dateutil.relativedelta import relativedelta
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import RoomsClient, RoomRequest, RoomParticipant
from azure.communication.rooms._shared.models import(
    CommunicationUserIdentifier
)

from azure.communication.identity import CommunicationIdentityClient

sys.path.append("..")

class CreateRoomSample(object):
    
    def setUp(self):
        self.connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    
        self.rooms_client = RoomsClient.from_connection_string(self.connection_string)
        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_string)
        self.user1 = self.identity_client.create_user()
        self.user2 = self.identity_client.create_user()
    
    def tearDown(self):
        self.identity_client.delete_user(self.user1)
        self.identity_client.delete_user(self.user2)
    
    def create_single_room(self):
        valid_from =  datetime.utcnow()
        valid_until = valid_from + relativedelta(months=+4)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        try:
            create_room_response = self.rooms_client.create_room(room_request=room_request)
            print(create_room_response)
            # delete created room
            self.rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)
    
    def create_single_room_with_participants(self):
        
        valid_from =  datetime.utcnow()
        valid_until = valid_from + relativedelta(months=+4)
        participants = {}
        
        # participant can be added by directly providing them while creating a room request
        participants[self.user1.properties["id"]] = RoomParticipant()
        
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until, participants=participants)
        
        # participant can also be added using add_participant in RoomRequest obj
        room_request.add_participant(self.user2)
        try:
            create_room_response = self.rooms_client.create_room(room_request=room_request)
            print(create_room_response)
            # delete created room
            self.rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)
    
    def create_single_room_with_default_attributes(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)

        try:
            create_room_response = rooms_client.create_room(room_request=None)
            print(create_room_response)
            # delete created room
            rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)

if __name__ == '__main__':
    sample = CreateRoomSample()
    sample.setUp()
    sample.create_single_room()
    sample.create_single_room_with_participants()
    sample.create_single_room_with_default_attributes()
    sample.tearDown()