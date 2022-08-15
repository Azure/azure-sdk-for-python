# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms._shared.models import CommunicationUserIdentifier
from azure.communication.rooms.aio import RoomsClient
from azure.communication.rooms import (
    RoomParticipant,
    RoomJoinPolicy,
    RoleType
)
from _shared.asynctestcase import AsyncCommunicationTestCase
from _shared.testcase import (
    ResponseReplacerProcessor
)

from _shared.utils import get_http_logging_policy
from helper import URIIdentityReplacer, RequestBodyIdentityReplacer

class RoomsClientTestAsync(AsyncCommunicationTestCase):
    def __init__(self, method_name):
        super(RoomsClientTestAsync, self).__init__(method_name)

    def setUp(self):
        super(RoomsClientTestAsync, self).setUp()
        if not self.is_playback():
            self.recording_processors.extend([
                ResponseReplacerProcessor(keys=[self._resource_name, "8:acs:[A-Za-z0-9-_]+"]),
                URIIdentityReplacer(),
                RequestBodyIdentityReplacer()])
        # create multiple users users
        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)

        self.users = {
            "john" : RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(
                    self.identity_client.create_user().properties["id"]
                ),
                role=RoleType.PRESENTER
            ),
            "fred" : RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(
                    self.identity_client.create_user().properties["id"]
                ),
                role=RoleType.CONSUMER
            ),
            "chris" : RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(
                    self.identity_client.create_user().properties["id"]
                ),
                role=RoleType.ATTENDEE
            )
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
                self.identity_client.delete_user(user.communication_identifier)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_no_attributes_async(self):
        async with self.rooms_client:
            response = await self.rooms_client.create_room()
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_only_validFrom_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        async with self.rooms_client:
            response = await self.rooms_client.create_room(valid_from=valid_from)
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)

            # verify room is valid for 180 days
            valid_until = datetime.now() + timedelta(days=180)
            self.assertEqual(valid_until.date(), response.valid_until.date())

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_only_validUntil_async(self):
        # room attributes
        valid_until =  datetime.now() + timedelta(weeks=3)
        async with self.rooms_client:
            response = await self.rooms_client.create_room(valid_until=valid_until)
            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response, valid_until=valid_until)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
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
            self.verify_successful_room_response(response=response, participants=participants)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_validUntil_7Months_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=29)

        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)
                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_validFrom_7Months_async(self):
        # room attributes
        valid_from = datetime.now() + timedelta(weeks=29)

        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(valid_from=valid_from)
                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_correct_timerange_async(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)

        async with self.rooms_client:
            response = await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)

            # delete created room
            await self.rooms_client.delete_room(room_id=response.id)
            self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_incorrectMri_async(self):
        # room attributes
        participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                role=RoleType.ATTENDEE
            ),
            self.users["john"]
        ]

        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.create_room(participants=participants)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_room_open_room(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)
        room_join_policy = RoomJoinPolicy.COMMUNICATION_SERVICE_USERS

        response = await self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, room_join_policy=room_join_policy)
        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until, room_join_policy=room_join_policy)
        # delete created room
        await self.rooms_client.delete_room(room_id=response.id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
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
            response=response, valid_from=valid_from, valid_until=valid_until, participants=participants)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
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
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            valid_from =  datetime.now() + timedelta(weeks=2)

            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from)

                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_only_ValidUntil_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # update room attributes
            valid_until =  datetime.now() + timedelta(weeks=2)

            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, valid_until=valid_until)

                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_ValidFrom_7Months_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # update room attributes
            valid_from =  datetime.now() + timedelta(weeks=29)

            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from)

                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_ValidUntil_7Months_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # update room attributes
            valid_until =  datetime.now() + timedelta(weeks=29)

            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id, valid_until=valid_until)

                # delete created room
                await self.rooms_client.delete_room(room_id=create_response.id)

                assert str(ex.value.status_code) == "400"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_incorrect_timerange_async(self):
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
    @AsyncCommunicationTestCase.await_prepared_test
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

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_change_open_room_in_past(self):
        # room with no attributes
        create_response = await self.rooms_client.create_room()

        # room attributes
        valid_from =  datetime.now() - timedelta(days=1)
        valid_until = valid_from + timedelta(weeks=4)
        room_join_policy = RoomJoinPolicy.COMMUNICATION_SERVICE_USERS

        with pytest.raises(HttpResponseError) as ex:
            await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until, room_join_policy=room_join_policy)

        # delete created room
        await self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_change_open_room_in_future(self):
        # room with no attributes
        create_response = await self.rooms_client.create_room()

        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)
        room_join_policy = RoomJoinPolicy.COMMUNICATION_SERVICE_USERS

        response = await self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until, room_join_policy=room_join_policy)
        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until, room_join_policy=room_join_policy)
        # delete created room
        await self.rooms_client.delete_room(room_id=create_response.id)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_participant_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # update room attributes
            participants = [
                self.users["john"]
            ]
            await self.rooms_client.add_participants(room_id=create_response.id, participants=participants)
            updated_participants = await self.rooms_client.get_participants(room_id=create_response.id)
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.assertListEqual(participants, updated_participants.participants)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_participant_async(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        self.users["john"].role = RoleType.CONSUMER
        self.users["chris"].role = RoleType.CONSUMER

        update_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(participants=create_participants)
            await self.rooms_client.update_participants(room_id=create_response.id, participants=update_participants)
            update_response = await self.rooms_client.get_participants(room_id=create_response.id)
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            self.assertListEqual(update_participants, update_response.participants)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_remove_participant_async(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        remove_participants = [
            self.users["john"].communication_identifier
        ]
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room(participants=create_participants)

            await self.rooms_client.remove_participants(room_id=create_response.id, communication_identifiers=remove_participants)
            update_response = await self.rooms_client.get_participants(room_id=create_response.id)
            # delete created room
            await self.rooms_client.delete_room(room_id=create_response.id)
            participants = [self.users["chris"]]
            self.assertListEqual(participants, update_response.participants)

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_participants_incorrectMri_async(self):
        # room with no attributes
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            participants = [
                RoomParticipant(
                    communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                    role=RoleType.ATTENDEE),
                self.users["john"]
            ]

            # update room attributes
            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.add_participants(room_id=create_response.id, participants=participants)

            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
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
                await self.rooms_client.add_participants(room_id=create_response.id, participants=participants)

            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_incorrect_roomId_async(self):
        # try to update room with random room_id
        with pytest.raises(HttpResponseError) as ex:
            async with self.rooms_client:
                await self.rooms_client.update_room(room_id=78469124725336262)

                #  assert error is Resource not found
                assert str(ex.value.status_code) == "404"
                assert ex.value.message is not None

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_update_room_deleted_room_async(self):
        # create a room -> delete it -> try to update it
        async with self.rooms_client:
            create_response = await self.rooms_client.create_room()

            # delete the room
            await self.rooms_client.delete_room(room_id=create_response.id)

            with pytest.raises(HttpResponseError) as ex:
                await self.rooms_client.update_room(room_id=create_response.id)

            #  assert error is Resource not found
            assert str(ex.value.status_code) == "404"
            assert ex.value.message is not None

    def verify_successful_room_response(self, response, valid_from=None, valid_until=None, room_id=None, participants=None, room_join_policy=None):

        if room_id is not None:
            self.assertEqual(room_id, response.id)
        if valid_from is not None:
            self.assertEqual(valid_from.replace(tzinfo=None), response.valid_from.replace(tzinfo=None))
        if valid_until is not None:
            self.assertEqual(valid_until.replace(tzinfo=None), response.valid_until.replace(tzinfo=None))
        if participants is not None:
            self.assertListEqual(participants, response.participants)
        if room_join_policy is not None:
            self.assertEqual(room_join_policy, response.room_join_policy)