# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from functools import partial
import os
from turtle import update
import pytest
from datetime import datetime, timezone, tzinfo
from dateutil.relativedelta import relativedelta

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.rooms import RoomsClient
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)

from azure.communication.rooms import (
    RoomsClient,
    RoomParticipant
)

from _shared.utils import get_http_logging_policy
from azure.communication.rooms._shared.models import CommunicationUserIdentifier


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class RoomsClientTest(CommunicationTestCase):
    def __init__(self, method_name):
        super(RoomsClientTest, self).__init__(method_name)

    def setUp(self):
        super(RoomsClientTest, self).setUp()
        if self.is_playback():
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["participants","invalid_participants"])])
        else:
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["participants", "invalid_participants"]),
                ResponseReplacerProcessor(keys=[self._resource_name])])
        # create multiple users users
        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)
        self.users = {
            "john" : RoomParticipant(identifier=self.identity_client.create_user().properties["id"], role_name='Presenter'),
            "fred" : RoomParticipant(identifier=self.identity_client.create_user().properties["id"], role_name='Organizer'),
            "chris" : RoomParticipant(identifier=self.identity_client.create_user().properties["id"], role_name='Attendee')
        }
        self.rooms_client = RoomsClient.from_connection_string(
            self.connection_str,
            http_logging_policy=get_http_logging_policy()
        )

    def tearDown(self):
        super(RoomsClientTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            for user in self.users.values():
                self.identity_client.delete_user(CommunicationUserIdentifier(id=user.identifier))

    def test_create_room_no_attributes(self):
        response = self.rooms_client.create_room()
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    @pytest.mark.live_test_only
    def test_create_room_only_validFrom(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        response = self.rooms_client.create_room(valid_from=valid_from)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        # verify room is valid for 180 days
        valid_until = datetime.utcnow() + relativedelta(days=+180)
        self.assertEqual(valid_until.date(), response.valid_until.date())

    @pytest.mark.live_test_only
    def test_create_room_only_validUntil(self):
        # room attributes
        valid_until =  datetime.now() + relativedelta(months=+3)
        response = self.rooms_client.create_room(valid_until=valid_until)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)
        self.verify_successful_room_response(response=response, valid_until=valid_until)

    @pytest.mark.live_test_only
    def test_create_room_only_participants(self):
        # add john and chris to room
        participants = [
            self.users["john"],
            self.users["chris"]
        ]

        response = self.rooms_client.create_room(participants=participants)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        self.verify_successful_room_response(response=response, participants=participants)

    def test_create_room_validUntil_7Months(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+7)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)
        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_create_room_validFrom_7Months(self):
        # room attributes
        valid_from = datetime.now() + relativedelta(months=+7)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(valid_from=valid_from)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_create_room_correct_timerange(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+4)

        response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until)
        self.verify_successful_room_response(response=response, valid_from=valid_from, valid_until=valid_until)
        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

    def test_create_room_incorretMri(self):
        # room attributes
        participants = [
            RoomParticipant(identifier="wrong_mir", role_name='Attendee'),
            self.users["john"]
        ]

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.create_room(participants=participants)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_create_room_all_attributes(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+4)
        participants = [
            self.users["john"]
        ]

        response = self.rooms_client.create_room(valid_from=valid_from, valid_until=valid_until, participants=participants)

        # delete created room
        self.rooms_client.delete_room(room_id=response.id)

        self.verify_successful_room_response(
            response=response, valid_from=valid_from, valid_until=valid_until, participants=participants)

    @pytest.mark.live_test_only
    def test_get_room(self):
        # room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until = valid_from + relativedelta(months=+2)
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
            response=get_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id, participants=participants)

    def test_get_invalid_room(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.get_room(room_id="89469124725336262")

        # Resource not found
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    def test_delete_invalid_room(self):
        # random room id
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.delete_room(room_id="78469124725336262")

        # Resource not found
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    def test_update_room_only_ValidFrom(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_from =  datetime.now() + relativedelta(months=+2)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_only_ValidUntil(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_until =  datetime.now() + relativedelta(months=+2)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, valid_until=valid_until)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_ValidFrom_7Months(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_from =  datetime.now() + relativedelta(months=+7)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_ValidUntil_7Months(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_until =  datetime.now() + relativedelta(months=+7)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, valid_until=valid_until)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_incorrect_timerange(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until =  datetime.now() + relativedelta(months=+7)

        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_update_room_correct_timerange(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        valid_from =  datetime.now() + relativedelta(days=+3)
        valid_until =  datetime.now() + relativedelta(months=+4)

        update_response = self.rooms_client.update_room(room_id=create_response.id, valid_from=valid_from, valid_until=valid_until)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response, valid_from=valid_from, valid_until=valid_until, room_id=create_response.id)

    @pytest.mark.live_test_only
    def test_update_room_add_participant(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        # update room attributes
        participants = [
            self.users["john"]
        ]
        update_response = self.rooms_client.add_participants(room_id=create_response.id, participants=participants)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=participants)

    @pytest.mark.live_test_only
    def test_update_room_update_participant(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        create_response = self.rooms_client.create_room(participants=create_participants)

        # participants to be updated
        self.users["john"].role_name = "Consumer"
        self.users["chris"].role_name = "Consumer"

        update_participants = [
            self.users["john"],
            self.users["chris"]
        ]

        update_response = self.rooms_client.update_participants(room_id=create_response.id, participants=update_participants)
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)

        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=update_participants)

    @pytest.mark.live_test_only
    def test_update_room_remove_participant(self):
        # add john and chris to room
        create_participants = [
            self.users["john"],
            self.users["chris"]
        ]
        create_response = self.rooms_client.create_room(participants=create_participants)

        # participants to be removed
        removed_participants = [
            self.users["john"],
        ]

        update_response = self.rooms_client.remove_participants(room_id=create_response.id, participants=removed_participants)
        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        participants = [
            self.users["chris"]
        ]

        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=participants)

    def test_update_room_incorretMri(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        participants = [
            RoomParticipant(identifier="wrong_mir", role_name='Attendee'),
            self.users["john"]
        ]

        # update room attributes
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.add_participants(room_id=create_response.id, participants=participants)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    def test_update_room_wrongRoleName(self):
        # room with no attributes
        create_response = self.rooms_client.create_room()

        participants = [
            RoomParticipant(identifier=self.users["john"].identifier, role_name='Kafka'),
        ]

        # update room attributes
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.add_participants(room_id=create_response.id, participants=participants)

        assert str(ex.value.status_code) == "400"
        assert ex.value.message is not None

    @pytest.mark.live_test_only
    def test_update_room_clear_participant_dict(self):
        # add john and chris to the room
        participants = [
            self.users["john"],
            self.users["chris"]
        ]
        create_response = self.rooms_client.create_room(participants=participants)

        # clear participants
        update_response = self.rooms_client.remove_all_participants(room_id=create_response.id)

        # delete created room
        self.rooms_client.delete_room(room_id=create_response.id)
        self.verify_successful_room_response(
            response=update_response,
            valid_from=create_response.valid_from,
            valid_until=create_response.valid_until,
            room_id=create_response.id,
            participants=[])

    def test_update_room_incorrect_roomId(self):
        # try to update room with random room_id
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=78469124725336262)

        #  assert error is Resource not found
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    def test_update_room_deleted_room(self):
        # create a room -> delete it -> try to update it
        create_response = self.rooms_client.create_room()

        # delete the room
        self.rooms_client.delete_room(room_id=create_response.id)
        with pytest.raises(HttpResponseError) as ex:
            self.rooms_client.update_room(room_id=create_response.id)

        #  assert error is Resource not found
        assert str(ex.value.status_code) == "404"
        assert ex.value.message is not None

    def verify_successful_room_response(self, response, valid_from=None, valid_until=None, room_id=None, participants=None):
        if room_id is not None:
            self.assertEqual(room_id, response.id)
        if valid_from is not None:
            self.assertEqual(valid_from.replace(tzinfo=None), response.valid_from.replace(tzinfo=None))
        if valid_until is not None:
            self.assertEqual(valid_until.replace(tzinfo=None), response.valid_until.replace(tzinfo=None))
        if participants is not None:
            self.assertListEqual(participants, response.participants)