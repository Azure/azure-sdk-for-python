# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import unittest
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms import (
    ParticipantRole,
    RoomParticipant,
    RoomsClient
)
from azure.communication.rooms._shared.models import CommunicationUserIdentifier
from _shared.utils import get_http_logging_policy
from acs_rooms_test_case import ACSRoomsTestCase
from devtools_testutils import is_live, add_general_regex_sanitizer, recorded_by_proxy

class TestRoomsClient(ACSRoomsTestCase):
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
        self.rooms_client = RoomsClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )

    @recorded_by_proxy
    def test_create_room_no_attributes(self):
        response = self.rooms_client.create_room()
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    @recorded_by_proxy
    def test_create_room_only_participants(self):
        # add john and chris to room
        participants = [
            self.users["john"],
            self.users["chris"]
        ]

        response = self.rooms_client.create_room(participants=participants)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        self.verify_successful_room_response(response=response)

    @recorded_by_proxy
    def test_create_room_validUntil_seven_months(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=29)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @recorded_by_proxy
    def test_create_room_valid_until_in_past(self):
        # room attributes
        valid_until = datetime.now() - timedelta(weeks=1)
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(valid_until=valid_until)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_create_room_correct_timerange(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)

        response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)
        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    @recorded_by_proxy
    def test_create_room_incorrectMri(self):
        # room attributes
        participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                role='Attendee'),
            self.users["john"]
        ]

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(participants=participants)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_create_room_all_attributes(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)
        participants = [
            self.users["john"]
        ]

        response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, participants=participants)

        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        self.verify_successful_room_response(
            response=response, valid_from=valid_from, valid_until=valid_until)

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_get_room(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=2)
        # add john to room
        participants = [
            self.users["john"]
        ]

        # create a room first
        create_response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, participants=participants)

        get_response = self.rooms_client.get_room(room_id=create_response.id)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=get_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @recorded_by_proxy
    def test_get_invalid_format_roomId(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.get_room(room_id="invalid_id")

            # Bad request
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_update_room_correct_timerange(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until =  datetime.now() + timedelta(weeks=4)

        update_response = self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_update_room_PstnDialOutEnabled(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        update_response = self.rooms_client.update_room(room_id=create_response.id, pstn_dial_out_enabled=True)

        self.verify_successful_room_response(
            response=update_response, pstn_dial_out_enabled=True, room_id=create_response.id)

        update_response = self.rooms_client.update_room(room_id=create_response.id, pstn_dial_out_enabled=False)

        self.verify_successful_room_response(
            response=update_response, pstn_dial_out_enabled=False, room_id=create_response.id)
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_update_room_PstnDialOutRemainsUnchanged(self):
        # room with no attributes
        create_response = self.rooms_client.create_room(pstn_dial_out_enabled=True)

        # update room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until =  datetime.now() + timedelta(weeks=4)
        # update room attributes
        update_response = self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

        self.verify_successful_room_response(
            response=update_response, valid_from=valid_from, valid_until=valid_until, pstn_dial_out_enabled=True, room_id=create_response.id)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_update_room_invalid_format_roomId(self):
        # try to update room with random room_id
        with pytest.raises(HttpResponseError) as ex:
            valid_from =  datetime.now() + timedelta(days=3)
            valid_until = valid_from + timedelta(days=4)
            self.rooms_client.update_room(room_id="invalid_id", valid_from=valid_from, valid_until=valid_until)
            #  assert error is bad request
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @recorded_by_proxy
    def test_update_room_valid_until_in_past(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        with pytest.raises(HttpResponseError) as ex:
            # update room attributes
            valid_from =  datetime.now() - timedelta(days=3)
            valid_until =  datetime.now() - timedelta(weeks=1)
            self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)
            # delete created room
            self.rooms_client.delete_room(room_id=create_response.id)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @recorded_by_proxy
    def test_update_room_deleted_room(self):
        # create a room -> delete it -> try to update it
        create_response = self.rooms_client.create_room()

        # delete the room
        self.rooms_client.delete_room(room_id=create_response.id)
        with pytest.raises(HttpResponseError) as ex:
            valid_from =  datetime.now() + timedelta(days=3)
            valid_until = valid_from + timedelta(days=4)
            self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

            #  assert error is Resource not found
            assert str(ex.value.status_code) == "404"
            assert ex.value.message is not None

    @recorded_by_proxy
    def test_update_room_exceed_max_timerange(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until =  datetime.now() + timedelta(weeks=29)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

         # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_add_or_update_participants(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        create_response = self.rooms_client.create_room(participants=create_participants)

        # update join to consumer and add fred to room
        self.users["john"].role = ParticipantRole.CONSUMER
        add_or_update_participants = [
            self.users["john"],
            self.users["fred"]
        ]

        expected_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id1),
                role=ParticipantRole.CONSUMER
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.ATTENDEE
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id2),
                role=ParticipantRole.CONSUMER
            )
        ]

        self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=add_or_update_participants)
        update_response = self.rooms_client.list_participants(room_id=create_response.id)
        participants = []
        for participant in update_response:
            participants.append(participant)
        assert len(participants) == 3
        case = unittest.TestCase()
        case.assertCountEqual(expected_participants, participants)
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_add_or_update_participants_with_null_role(self):
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

        # Check participants with null roles were added in created room
        create_response = self.rooms_client.create_room(participants=create_participants)
        list_participants_response = self.rooms_client.list_participants(room_id=create_response.id)
        participants = []
        for participant in list_participants_response:
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
        self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=add_or_update_participants)
        update_response = self.rooms_client.list_participants(room_id=create_response.id)
        updated_participants = []
        for participant in update_response:
            updated_participants.append(participant)
        assert len(updated_participants) == 4
        case = unittest.TestCase()
        case.assertCountEqual(expected_participants, updated_participants)
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_add_or_update_participants_incorrectMri(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                role=ParticipantRole.ATTENDEE),
            self.users["john"]
        ]

        # update room attributes
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=participants)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_add_or_update_room_wrongRoleName(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        participants = [
            RoomParticipant(
                communication_identifier=self.users["john"].communication_identifier,
                role='Kafka'),
        ]

        # update room attributes
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.add_or_update_participants(room_id=create_response.id, participants=participants)
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_remove_participants(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        create_response = self.rooms_client.create_room(participants=create_participants)

        # participants to be removed
        removed_participants = [
            self.users["john"].communication_identifier
        ]

        expected_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.ATTENDEE
            )
        ]
        self.rooms_client.remove_participants(room_id=create_response.id, participants=removed_participants)
        update_response = self.rooms_client.list_participants(room_id=create_response.id)
        participants = []
        for participant in update_response:
            participants.append(participant)
        assert len(participants) == 1
        case = unittest.TestCase()
        case.assertCountEqual(expected_participants, participants)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_remove_participant_who_do_not_exist(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        remove_participants = [
            self.users["fred"].communication_identifier
        ]
        expected_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id1),
                role=ParticipantRole.PRESENTER
            ),
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier(self.id3),
                role=ParticipantRole.ATTENDEE
            )
        ]
        create_response = self.rooms_client.create_room(participants=create_participants)
        self.rooms_client.remove_participants(room_id=create_response.id, participants=remove_participants)
        update_response = self.rooms_client.list_participants(room_id=create_response.id)
        participants = []
        for participant in update_response:
            participants.append(participant)
        assert len(participants) == 2
        case = unittest.TestCase()
        case.assertCountEqual(expected_participants, participants)
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_remove_participant_wrong_mri(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        remove_participants = [
            RoomParticipant(
                communication_identifier=CommunicationUserIdentifier("wrong_mri"),
                role=ParticipantRole.ATTENDEE),
        ]
        create_response = self.rooms_client.create_room(participants=create_participants)
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.remove_participants(room_id=create_response.id, participants=remove_participants)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_list_rooms_first_room_is_not_null_success(self):
        # create a room -> list all rooms -> delete room
        create_response = self.rooms_client.create_room()

        all_rooms = self.rooms_client.list_rooms()
        first_room = None
        count = 0
        for room in all_rooms:
            if count == 1:
                break
            first_room = room
            count += 1

        assert first_room is not None
        self.verify_successful_room_response(first_room)

        # delete the room
        self.rooms_client.delete_room(room_id=create_response.id)

    @recorded_by_proxy
    def test_delete_room_success(self):
        # create a room -> delete the room -> cannot get the room
        create_response = self.rooms_client.create_room()
        # delete the room
        self.rooms_client.delete_room(room_id=create_response.id)
        # get the deleted room
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.get_room(create_response.id)
            assert str(ex.value.status_code) == "404"
            assert ex.value.message is not None

    @recorded_by_proxy
    def test_delete_room_invalid_id(self):
        # room with no attributes
        with pytest.raises(HttpResponseError) as ex:
            # delete created room with invalid id
            self.rooms_client.delete_room(room_id="123")
            assert str(ex.value.status_code) == "400"
            assert ex.value.message is not None

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_create_room_pstn_dial_out_enabled(self):
        # room attributes

        response = self.rooms_client.create_room(pstn_dial_out_enabled=True)

        self.verify_successful_room_response(response=response, pstn_dial_out_enabled=True)

        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        response = self.rooms_client.create_room(pstn_dial_out_enabled=False)

        self.verify_successful_room_response(response=response, pstn_dial_out_enabled=False)

        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_create_room_timerange_pstn_dial_out_enabled(self):
        # room attributes
        valid_from =  datetime.now() + timedelta(days=3)
        valid_until = valid_from + timedelta(weeks=4)

        response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, pstn_dial_out_enabled=True)

        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until, pstn_dial_out_enabled=True)

        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, pstn_dial_out_enabled=False)

        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until, pstn_dial_out_enabled=False)

        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    def verify_successful_room_response(self, response, valid_from=None, valid_until=None, room_id=None, pstn_dial_out_enabled=None):
        if room_id is not None:
            assert room_id == response.id
        if valid_from is not None:
            assert valid_from.replace(tzinfo=None) == datetime.strptime(
                response.valid_from, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        if valid_until is not None:
            assert valid_until.replace(tzinfo=None) == datetime.strptime(
                response.valid_until, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        assert response.created_at is not None
        if pstn_dial_out_enabled is not None:
            assert pstn_dial_out_enabled == response.pstn_dial_out_enabled
