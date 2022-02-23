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
from azure.communication.rooms import RoomsClient, RoomRequest

sys.path.append("..")

class CreateRoomSample(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    
    def create_single_room(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)

        valid_from = datetime.datetime(2022, 2, 25, 4, 34, 22)
        valid_until = datetime.datetime(2022, 2, 25, 4, 34, 22)
        roomRequest = RoomRequest(valid_from=valid_from, valid_until=valid_until)
        try:
            create_room_response = rooms_client.create_room(roomRequest=roomRequest)
            print(create_room_response)
            # delete created room
            rooms_client.delete_room(room_id=create_room_response.id)
        except HttpResponseError as ex:
            print(ex)
        
if __name__ == '__main__':
    sample = CreateRoomSample()
    sample.create_single_room()