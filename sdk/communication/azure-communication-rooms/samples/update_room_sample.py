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
from asyncio.windows_events import NULL
import os
import datetime
import sys
from azure.core.exceptions import HttpResponseError
from azure.communication.rooms import RoomsClient, RoomRequest, RoomParticipant
from azure.communication.rooms._shared.models import(
    CommunicationUserIdentifier
)
sys.path.append("..")

class UpdateRoomSample(object):

    connection_string = "endpoint=https://rooms-ppe-us.ppe.communication.azure.net/;accesskey=J9gcDYLfopqKzHIKg7BI7+Qt/ZKTg0jeO/xvUF1JWxr8sHeA9Wq3DT+bjEIo3kRfjuj84CNm3s7B/zDrqkeLnA=="#os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    roomsClient = None
    def create_single_room(self):
        self.rooms_client = RoomsClient.from_connection_string(self.connection_string)

        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 22)
        valid_until = datetime.datetime(2022, 4, 25, 4, 34, 22)
        participants = {}
        user = CommunicationUserIdentifier("8:acs:db75ed0c-e801-41a3-99a4-66a0a119a06c_be3a83c1-f5d9-49ee-a427-0e9b917c062e")
        participants["8:acs:db75ed0c-e801-41a3-99a4-66a0a119a06c_be3a83c1-f5d9-49ee-a427-0e9b917c062c"] = RoomParticipant()
        
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until, participants=participants)
        room_request.add_participant(user)
        try:
            create_room_response = self.rooms_client.create_room(room_request=room_request)
            print(create_room_response)
            return create_room_response.id
        except HttpResponseError as ex:
            print(ex)

    def update_single_room(self, room_id):
        
        valid_from = datetime.datetime(2022, 4, 25, 4, 34, 22)
        valid_until = datetime.datetime(2022, 6, 25, 4, 34, 22)
        participants = {}
        user = CommunicationUserIdentifier("8:acs:db75ed0c-e801-41a3-99a4-66a0a119a06c_be3a83c1-f5d9-49ee-a427-0e9b917c062e")
        participants["8:acs:db75ed0c-e801-41a3-99a4-66a0a119a06c_be3a83c1-f5d9-49ee-a427-0e9b917c062d"] = RoomParticipant()
        
        room_request = RoomRequest(valid_from=valid_from, valid_until=valid_until, participants=participants)
        room_request.remove_participant(user)
        try:
            update_room_response = self.rooms_client.update_room(room_id=room_id, room_request=room_request)
            print(update_room_response)
        except HttpResponseError as ex:
            print(ex)

    def delete_room(self, room_id):
        self.rooms_client.delete_room(room_id=room_id)

if __name__ == '__main__':
    sample = UpdateRoomSample()
    room_id = sample.create_single_room()
    sample.update_single_room(room_id=room_id)
    sample.delete_room(room_id=room_id)