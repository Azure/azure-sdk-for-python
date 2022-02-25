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
import datetime
import sys
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import RoomsClient, RoomRequest, RoomParticipant
from azure.communication.rooms._shared.models import(
    CommunicationUserIdentifier
)

sys.path.append("..")

class CreateRoomSample(object):
    connection_string = "endpoint=https://rooms-ppe-us.ppe.communication.azure.net/;accesskey=J9gcDYLfopqKzHIKg7BI7+Qt/ZKTg0jeO/xvUF1JWxr8sHeA9Wq3DT+bjEIo3kRfjuj84CNm3s7B/zDrqkeLnA=="#os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    #connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    
    def create_single_room(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)

        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 22)
        valid_until = datetime.datetime(2022, 2, 25, 4, 34, 22)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        try:
            create_room_response = rooms_client.create_room(room_request=room_request)
            print(create_room_response)
            # delete created room
            rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)
    
    def create_single_room_with_participants(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)

        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 22)
        valid_until = datetime.datetime(2022, 2, 25, 4, 34, 22)
        participants = {}
        
        # participant can be added by directly providing them while creating a room request
        participants["8:acs:db75ed0c-e801-41a3-99a4-66a0a119a06c_be3a83c1-f5d9-49ee-a427-0e9b917c062c"] = RoomParticipant()
        
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until, participants=participants)
        user = CommunicationUserIdentifier("8:acs:db75ed0c-e801-41a3-99a4-66a0a119a06c_be3a83c1-f5d9-49ee-a427-0e9b917c062e")
        
        # participant can also be added using add_participant in RoomRequest obj
        room_request.add_participant(user)
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        try:
            create_room_response = rooms_client.create_room(room_request=room_request)
            print(create_room_response)
            # delete created room
            rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)
    
    def create_single_room_with_default_attributes(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)
        room_request = RoomRequest()
        
        try:
            create_room_response = rooms_client.create_room(room_request=None)
            print(create_room_response)
            # delete created room
            rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)

if __name__ == '__main__':
    sample = CreateRoomSample()
    sample.create_single_room()
    sample.create_single_room_with_participants()
    sample.create_single_room_with_default_attributes()