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

from datetime import datetime, timedelta
from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms import (
    ParticipantRole,
    RoomsClient,
    RoomParticipant
)

sys.path.append("..")

class RoomsSample(object):

    def setUp(self):
        self.connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")

        self.rooms_client = RoomsClient.from_connection_string(self.connection_string)
        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_string)
        self.rooms = []
        self.participant_1 = RoomParticipant(
            communication_identifier=self.identity_client.create_user(),
            role=ParticipantRole.PRESENTER)
        self.participant_2 = RoomParticipant(
            communication_identifier=self.identity_client.create_user(),
            role=ParticipantRole.CONSUMER)

    def tearDown(self):
        self.delete_room_all_rooms()

    def create_single_room(self):

        valid_from =  datetime.now()
        valid_until = valid_from + timedelta(weeks=4)
        participants = [self.participant_1]

        try:
            create_room_response = self.rooms_client.create_room(
                valid_from=valid_from,
                valid_until=valid_until,
                participants=participants)
            self.printRoom(response=create_room_response)

            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)

    def create_single_room_with_default_attributes(self):
        try:
            create_room_response = self.rooms_client.create_room()
            self.printRoom(response=create_room_response)
            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)

    # Starting in 1.1.0b1 release,create_room function also takes pstn_dial_out_enabled as parameter
    def create_room_with_pstn_attribute(self):

        valid_from =  datetime.now()
        valid_until = valid_from + timedelta(weeks=4)
        participants = [self.participant_1]
        pstn_dial_out_enabled = True

        try:
            create_room_response = self.rooms_client.create_room(
                valid_from=valid_from,
                valid_until=valid_until,
                participants=participants,
                pstn_dial_out_enabled=pstn_dial_out_enabled)
            self.printRoom(response=create_room_response)

            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)

    def update_single_room(self, room_id):
        # set attributes you want to change
        valid_from =  datetime.now()
        valid_until = valid_from + timedelta(weeks=7)

        try:
            update_room_response = self.rooms_client.update_room(room_id=room_id, valid_from=valid_from, valid_until=valid_until)
            self.printRoom(response=update_room_response)
        except HttpResponseError as ex:
            print(ex)

    # Starting in 1.1.0b1 release,update_room function also takes pstn_dial_out_enabled as parameter
    def update_room_with_pstn_attribute(self, room_id):
        # set attributes you want to change
        valid_from =  datetime.now()
        valid_until = valid_from + timedelta(weeks=7)
        pstn_dial_out_enabled = True

        try:
            update_room_response = self.rooms_client.update_room(
                room_id=room_id,
                valid_from=valid_from,
                valid_until=valid_until,
                pstn_dial_out_enabled=pstn_dial_out_enabled)
            self.printRoom(response=update_room_response)
        except HttpResponseError as ex:
            print(ex)

    def add_or_update_participants(self, room_id):
        self.participant_1.role = ParticipantRole.ATTENDEE
        participants = [
            self.participant_1, # Update participant_1 role from Presenter to Attendee
            self.participant_2  # Add participant_2 to room
            ]

        try:
            self.rooms_client.add_or_update_participants(room_id=room_id, participants=participants)
        except HttpResponseError as ex:
            print(ex)

    def list_participants(self, room_id):
        try:
            get_participants_response = self.rooms_client.list_participants(room_id=room_id)
            print("participants: \n", self.convert_participant_list_to_string(get_participants_response))
        except HttpResponseError as ex:
            print(ex)

    def remove_participants(self, room_id):
        participants = [self.participant_1.communication_identifier]

        try:
            self.rooms_client.remove_participants(room_id=room_id, participants=participants)
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
        print("created_at: ", response.created_at)
        print("valid_from: ", response.valid_from)
        print("valid_until: ", response.valid_until)

    def convert_participant_list_to_string(self, participants):
        result = ''
        for p in participants:
            result += "id: {}\n role: {}\n".format(
                p.communication_identifier.properties["id"], p.role)
        return result

if __name__ == '__main__':
    sample = RoomsSample()
    sample.setUp()
    sample.create_single_room()
    sample.create_single_room_with_default_attributes()
    if len(sample.rooms) > 0:
        sample.get_room(room_id=sample.rooms[0] )
        sample.update_single_room(room_id=sample.rooms[0])
        sample.add_or_update_participants(room_id=sample.rooms[0])
        sample.list_participants(room_id=sample.rooms[0])
        sample.remove_participants(room_id=sample.rooms[0])
        sample.get_room(room_id=sample.rooms[0])
    sample.tearDown()