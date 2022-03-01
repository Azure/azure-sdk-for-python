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
import re
import sys

from datetime import datetime
from webbrowser import get
from dateutil.relativedelta import relativedelta
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import (
    RoomsClient,
    RoomRequest,
    RoomParticipant
)
from azure.communication.rooms._shared.models import(
    CommunicationUserIdentifier
)

sys.path.append("..")

class CreateRoomSample(object):
    
    def setUp(self):
        self.connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    
        self.rooms_client = RoomsClient.from_connection_string(self.connection_string)
        self.rooms = []
  
    def tearDown(self):
        self.delete_room_all_rooms()
    
    def create_single_room(self):
        
        valid_from =  datetime.now()
        valid_until = valid_from + relativedelta(months=+4)
        participants = {}
        
        # participant can be added by directly providing them while creating a room request
        participants["PARTICIPANT MRI"] = RoomParticipant()
        
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until, participants=participants)
        
        # participant can also be added using add_participant in RoomRequest obj
        user = CommunicationUserIdentifier("PARTICIPANT_MRI")
        room_request.add_participant(user)
        try:
            create_room_response = self.rooms_client.create_room(room_request=room_request)
            self.printRoom(response=create_room_response)

            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)
    
    def create_single_room_with_default_attributes(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)

        try:
            create_room_response = rooms_client.create_room(room_request=None)
            self.printRoom(response=create_room_response)
            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)
    
    def update_single_room(self, room_id):
        # set attributes you want to change
        valid_from =  datetime.now()
        valid_until = valid_from + relativedelta(months=+1,days=+20)
        participants = {}
        participants["PARTICIPANT_MRI1"] = RoomParticipant()
        participants["PARTICIPANT_MRI2"] = RoomParticipant()
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until, participants=participants)
        # to remove a participant
        #   a) user = CommunicationUserIdentifier("PARTICIPANT_MRI")
        #      room_request.remove_participant(user) or,
        #   b) participants["PARTICIPANT_MRI"] = None
        
        try:
            update_room_response = self.rooms_client.update_room(room_id=room_id, room_request=room_request)
            self.printRoom(response=update_room_response)
        except HttpResponseError as ex:
            print(ex)

    def clear_all_participants(self, room_id):
        room_request = RoomRequest()
        room_request.remove_all_participants()

        try:
            update_room_response = self.rooms_client.update_room(room_id=room_id, room_request=room_request)
            self.printRoom(response=update_room_response)
        except HttpResponseError as ex:
            print(ex)

    def delete_room_all_rooms(self):
        for room in self.rooms:
            print("deleting: ", room)
            self.rooms_client.delete_room(room_id=room)
    
    def get_room(self, room_id):
        
        try:
            get_room_response = self.rooms_client.get_room(room_id=room_id)
            self.printRoom(response=get_room_response)

        except HttpResponseError as ex:
            print(ex)
    
    def printRoom(self, response):
        print("room_id: ", response.id)
        print("created_date_time: ", response.created_date_time)
        print("valid_from: ", response.valid_from)
        print("valid_until: ", response.valid_until)
        print("participants: ", response.participants)

if __name__ == '__main__':
    sample = CreateRoomSample()
    sample.setUp()
    sample.create_single_room()
    sample.create_single_room_with_default_attributes()
    if len(sample.rooms) > 0:
        sample.get_room(room_id=sample.rooms[0] )
        sample.update_single_room(room_id=sample.rooms[0])
        sample.clear_all_participants(room_id=sample.rooms[0])
        sample.get_room(room_id=sample.rooms[0] )
    sample.tearDown()