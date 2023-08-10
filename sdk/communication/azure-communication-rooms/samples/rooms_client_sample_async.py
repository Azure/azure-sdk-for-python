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
import asyncio

from datetime import datetime, timedelta
from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms.aio import RoomsClient
from azure.communication.rooms import (
    RoomParticipant,
    ParticipantRole
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

    async def tearDown(self):
        await self.delete_room_all_rooms()

    async def create_single_room(self):

        valid_from =  datetime.now()
        valid_until = valid_from + timedelta(weeks=4)
        participants = [self.participant_1]

        try:
            create_room_response = await self.rooms_client.create_room(
                valid_from=valid_from,
                valid_until=valid_until,
                participants=participants)
            self.printRoom(response=create_room_response)

            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)

    async def create_single_room_with_default_attributes(self):
        rooms_client = RoomsClient.from_connection_string(self.connection_string)

        try:
            create_room_response = await rooms_client.create_room()
            self.printRoom(response=create_room_response)
            # all created room to a list
            self.rooms.append(create_room_response.id)

        except HttpResponseError as ex:
            print(ex)

    async def update_single_room(self, room_id):
        # set attributes you want to change
        valid_from =  datetime.now()
        valid_until = valid_from + timedelta(weeks=7)

        try:
            update_room_response = await self.rooms_client.update_room(room_id=room_id, valid_from=valid_from, valid_until=valid_until)
            self.printRoom(response=update_room_response)
        except HttpResponseError as ex:
            print(ex)

    async def add_or_update_participants(self, room_id):
        self.participant_1.role = ParticipantRole.ATTENDEE
        participants = [
            self.participant_1, # Update participant_1 role from Presenter to Attendee
            self.participant_2  # Add participant_2 to room
            ]

        try:
            await self.rooms_client.add_or_update_participants(room_id=room_id, participants=participants)
        except HttpResponseError as ex:
            print(ex)

    async def list_participants(self, room_id):
        try:
            list_participants_response = self.rooms_client.list_participants(room_id=room_id)
            print("participants: \n", self.convert_participant_list_to_string(list_participants_response))
        except HttpResponseError as ex:
            print(ex)

    async def remove_participants(self, room_id):
        participants = [self.participant_1.communication_identifier]

        try:
            await self.rooms_client.remove_participants(room_id=room_id, participants=participants)
        except HttpResponseError as ex:
            print(ex)

    async def delete_room_all_rooms(self):
        for room in self.rooms:
            print("deleting: ", room)
            await self.rooms_client.delete_room(room_id=room)

    async def get_room(self, room_id):

        try:
            get_room_response = await self.rooms_client.get_room(room_id=room_id)
            self.printRoom(response=get_room_response)

        except HttpResponseError as ex:
            print(ex)

    def printRoom(self, response):
        print("room_id: ", response.id)
        print("created_at: ", response.created_at)
        print("valid_from: ", response.valid_from)
        print("valid_until: ", response.valid_until)

    async def convert_participant_list_to_string(self, participants):
        result = ''
        async for p in participants:
            result += "id: {}\n role: {}\n".format(
                p.communication_identifier.properties["id"], p.role)
        return result

async def main():
    sample = RoomsSample()
    sample.setUp()
    await sample.create_single_room()
    await sample.create_single_room_with_default_attributes()
    if len(sample.rooms) > 0:
        await sample.get_room(room_id=sample.rooms[0] )
        await sample.update_single_room(room_id=sample.rooms[0])
        await sample.add_or_update_participants(room_id=sample.rooms[0])
        await sample.list_participants(room_id=sample.rooms[0])
        await sample.remove_participants(room_id=sample.rooms[0])
        await sample.get_room(room_id=sample.rooms[0])
    await sample.tearDown()

if __name__ == '__main__':
    asyncio.run(main())
