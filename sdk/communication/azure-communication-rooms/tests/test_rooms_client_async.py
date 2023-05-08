# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from datetime import datetime, timedelta
import unittest
from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms._shared.models import CommunicationUserIdentifier
from azure.communication.rooms.aio import RoomsClient
from azure.communication.rooms import (
    ParticipantRole,
    RoomParticipant
)
from acs_rooms_test_case import ACSRoomsTestCase
from _shared.utils import get_http_logging_policy
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import is_live, add_general_regex_sanitizer


@pytest.mark.asyncio
class TestRoomsClientAsync(ACSRoomsTestCase):
    def setup_method(self):
        super().setUp()
        sanitizedId1 = "8:acs:sanitized1"
        sanitizedId2 = "8:acs:sanitized2"
        sanitizedId3 = "8:acs:sanitized3"
        sanitizedId4 = "8:acs:sanitized4"
        if is_live():
            self.identity_client = CommunicationIdentityClient.from_connection_string(
                self.connection_str)


            self.id1 = self.identity_client.create_user().properties["id"]
            self.id2 = self.identity_client.create_user().properties["id"]
            self.id3 = self.identity_client.create_user().properties["id"]
            self.id4 = self.identity_client.create_user().properties["id"]
            add_general_regex_sanitizer(regex=self.id1, value=sanitizedId1)
            add_general_regex_sanitizer(regex=self.id2, value=sanitizedId2)
            add_general_regex_sanitizer(regex=self.id3, value=sanitizedId3)
            add_general_regex_sanitizer(regex=self.id4, value=sanitizedId4)
        else:
            self.id1 = sanitizedId1
            self.id2 = sanitizedId2
            self.id3 = sanitizedId3
            self.id4 = sanitizedId4

        self.rooms_client = RoomsClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )
        self.users = {
                "john" : RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id1),
                    role=ParticipantRole.PRESENTER
                ),
                "fred" : RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id2),
                    role=ParticipantRole.CONSUMER
                ),
                "chris" : RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id3),
                    role=ParticipantRole.ATTENDEE
                )
            }

    @recorded_by_proxy_async
    async def test_create_room_no_attributes_async(self):
        async with self.rooms_client:
            response = await self.rooms_client.create_room()
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)

    @recorded_by_proxy_async
    async def test_create_room_only_participants_async(self):
        # add john and chris to room
        participants = [
            self.users["john"],
            self.users["chris"]
        ]

        async with self.rooms_client:
            response = await self.rooms_client.create_room(participants=participants)

            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response)

    @recorded_by_proxy_async
    async def test_create_room_validUntil_7Months_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=29)

        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)
                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_create_room_validFrom_7Months_async(self):
        # room attributes
        valid_from = datetime.now() + timedelta(weeks=29)

        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(valid_from=valid_from)
                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy_async
    async def test_create_room_correct_timerange_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)

        async with self.rooms_client:
            response = await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)

            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until)

    @recorded_by_proxy_async
    async def test_create_room_incorrectMri_async(self):
        # room attributes
        participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                role=ParticipantRole.ATTENDEE
            ),
            self.users["john"]
        ]

        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(participants=participants)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy_async
    async def test_create_room_all_attributes_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)
        # add john to room
        participants = [
            self.users["john"]
        ]

        async with self.rooms_client:
            response = await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, participants=participants)

            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(
            response=response, valid_from=valid_from, valid_until=valid_until)

    @pytest.mark.live_test_only
    @recorded_by_proxy_async
    async def test_get_room_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=2)

        # add john to room
        participants = [
            self.users["john"]
        ]
        async with self.rooms_client:
            # create a room first
            create_response = await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, participants=participants)

            get_response = await self.rooms_client.get_room(room_id=create_response.id)

            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=get_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @recorded_by_proxy_async
    async def test_get_invalid_room_async(self):
        # random room id
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            with pytest.raises(HttpResponseError) as ex:

                await self.rooms_client.get_room(room_id=create_response.id)
                # Resource not found
            assert str(ex.value.status_code) == "404"
            assert ex.value.message is not None
            await self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy_async
    async def test_update_room_exceed_max_timerange_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # update room attributes
            valid_from =  datetime.now() + timedelta(days=3)
            valid_until =  datetime.now() + timedelta(weeks=29)

            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy_async
    async def test_update_room_correct_timerange_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # update room attributes
            valid_from =  datetime.now() + timedelta(days=3)
            valid_until =  datetime.now() + timedelta(weeks=4)

            update_response = await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.verify_successful_room_response(
                response=update_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @recorded_by_proxy_async
    async def test_add_or_update_participant_async(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        # update join to consumer and add fred to room
        self.users["john"].role = ParticipantRole.CONSUMER
        update_participants = [
            self.users["john"],
            self.users["fred"]
        ]
        expected_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id1),
                role=ParticipantRole.CONSUMER
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id2),
                role=ParticipantRole.CONSUMER
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.ATTENDEE
            )
        ]
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(participants=create_participants)
            await self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=update_participants)
            update_response = self.rooms_client.list_participants(room_id=create_response.id)
            participants = []
            async for participant in update_response:
                participants.append(participant)
            assert len(participants) == 3
            case = unittest.TestCase()
            case.assertCountEqual(expected_participants, participants)
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy_async
    async def test_add_or_update_participant_with_null_roles_async(self):
        create_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id1),
                role=None
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id2)
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.PRESENTER
            )
        ]

        expected_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id1),
                role=ParticipantRole.ATTENDEE
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id2),
                role=ParticipantRole.ATTENDEE
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.PRESENTER
            )
        ]
        async with self.rooms_client:
            # Check participants with null roles were added in created room
            create_response = await self.rooms_client.create_room(participants=create_participants)
            list_participants_response = self.rooms_client.list_participants(room_id=create_response.id)
            participants = []
            async for participant in list_participants_response:
                participants.append(participant)
            assert len(participants) == 3
            case = unittest.TestCase()
            case.assertCountEqual(expected_participants, participants)

            # Check participants were added or updated properly
            add_or_update_participants = [
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id1),
                    role=None
                ),
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id2),
                    role=ParticipantRole.CONSUMER
                ),
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id3)
                ),
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id4)
                )]

            expected_participants = [
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id1),
                    role=ParticipantRole.ATTENDEE
                ),
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id2),
                    role=ParticipantRole.CONSUMER
                ),
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id3),
                    role=ParticipantRole.ATTENDEE
                ),
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier(self.id4),
                    role=ParticipantRole.ATTENDEE
                )
            ]
            await self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=add_or_update_participants)
            update_response = self.rooms_client.list_participants(room_id=create_response.id)
            updated_participants = []
            async for participant in update_response:
                updated_participants.append(participant)
            assert len(updated_participants) == 4
            case = unittest.TestCase()
            case.assertCountEqual(expected_participants, updated_participants)
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy_async
    async def test_remove_participant_async(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        remove_participants = [
            self.users["john"].communication_identifier
        ]
        expected_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.ATTENDEE
            )
        ]
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(participants=create_participants)
            await self.rooms_client.remove_participants(room_id=create_response.id, participants=remove_participants)
            update_response = self.rooms_client.list_participants(room_id=create_response.id)
            participants = []
            async for participant in update_response:
                participants.append(participant)
            assert len(participants) == 1
            case = unittest.TestCase()
            case.assertCountEqual(expected_participants, participants)
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy_async
    async def test_add_or_update_participants_incorrectMri_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            participants = [
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                    role=ParticipantRole.ATTENDEE),
                self.users["john"]
            ]

            # update room attributes
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=participants)

            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_add_participants_wrongRoleName_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            participants = [
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier("chris"),
                    role='kafka'),
                self.users["john"]
            ]

            # update room attributes
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=participants)

            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_update_room_incorrect_roomId_async(self):
        # try to update room with random room_id
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                valid_from =  datetime.now() + timedelta(days=3)
                valid_until = valid_from + timedelta(days=4)
                await self.rooms_client.update_room(room_id=78469124725336262, valid_from=valid_from, valid_until=valid_until)

                #  assert error is Resource not found
                assert str(ex.value.status_code) == "404"
                assert ex.value.message is not None

    @recorded_by_proxy_async
    async def test_update_room_deleted_room_async(self):
        # create a room -> delete it -> try to update it
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # delete the room
            await self.rooms_client.delete_room(room_id=create_response.id)

            with pytest.raises(HttpResponseError) as ex:
                valid_from =  datetime.now() + timedelta(days=3)
                valid_until = valid_from + timedelta(days=4)
                await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

            #  assert error is Resource not found
            assert str(ex.value.status_code) == "404"
            assert ex.value.message is not None

    def verify_successful_room_response(self, response, valid_from=None, valid_until=None, room_id=None):
        if room_id is not None:
            assert room_id == response.id
        if valid_from is not None:
            assert valid_from.replace(tzinfo=None) == datetime.strptime(
                response.valid_from, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        if valid_until is not None:
            assert valid_until.replace(tzinfo=None) == datetime.strptime(
                response.valid_until, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        assert response.created_at is not None
