# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os, uuid, pytest
from time import sleep
import utils._test_constants as CONST
from azure.communication.callingserver import (
    CallingServerClient,
    CommunicationUserIdentifier,
    GroupCallLocator,
    ServerCallLocator
    )
from azure.communication.callingserver._shared.utils import parse_connection_str
from azure.identity import DefaultAzureCredential
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from devtools_testutils import is_live
from _shared.utils import get_http_logging_policy
from utils._live_test_utils import CallingServerLiveTestUtils, RequestReplacerProcessor
from utils._test_mock_utils import FakeTokenCredential

from azure.core.exceptions import (
    HttpResponseError
)

class ServerCallTest(CommunicationTestCase):

    def setUp(self):
        super(ServerCallTest, self).setUp()

        if self.is_playback():
            self.from_phone_number = "+15551234567"
            self.to_phone_number = "+15551234567"
            self.invalid_server_call_id = "aHR0cHM6Ly9XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "callbackUri", "identity", "communicationUser", "rawId", "callConnectionId", "phoneNumber", "groupCallId", "recordingId", "serverCallId"])])
        else:
            self.to_phone_number = os.getenv("AZURE_PHONE_NUMBER")
            self.from_phone_number = os.getenv("ALTERNATE_CALLERID")
            self.invalid_server_call_id = os.getenv("INVALID_SERVER_CALL_ID")
            self.participant_guid = os.getenv("PARTICIPANT_GUID")
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "callbackUri", "identity", "communicationUser", "rawId", "callConnectionId", "phoneNumber", "groupCallId", "recordingId", "serverCallId"]),
                BodyReplacerProcessor(keys=["audioFileUri"], replacement = "https://dummy.ngrok.io/audio/sample-message.wav"),
                ResponseReplacerProcessor(keys=[self._resource_name]),
                RequestReplacerProcessor()])

        # create CallingServerClient
        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()

        self.callingserver_client = CallingServerClient(
            self.endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )

        self.from_user = CallingServerLiveTestUtils.get_new_user_id(self.connection_str)
        self.to_user = CallingServerLiveTestUtils.get_new_user_id(self.connection_str)

    def test_join_play_cancel_hangup_scenario(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_join_play_cancel_hangup_scenario")

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        CallingServerLiveTestUtils.validate_group_call_connection(call_connections)

        try:
            # Play Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            play_audio_result = self.callingserver_client.play_audio(
                GroupCallLocator(group_id),
                CONST.AUDIO_FILE_URL,
                is_looped = True,
                audio_file_id = str(uuid.uuid4()),
                callback_uri = CONST.AppCallbackUrl,
                operation_context = OperationContext
                )

            CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

            # Cancel Prompt Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.cancel_all_media_operations_for_group_call(call_connections)
        except Exception as ex:
            print(str(ex))
        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    def test_create_add_remove_hangup_scenario(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_create_add_remove_hangup_scenario")

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        CallingServerLiveTestUtils.validate_group_call_connection(call_connections)

        try:
            # Add Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            added_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.participant_guid)
            add_participant_result = self.callingserver_client.add_participant(
                call_locator=GroupCallLocator(group_id),
                participant=CommunicationUserIdentifier(added_participant),
                callback_uri=CONST.AppCallbackUrl,
                alternate_caller_id=None,
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

            # Play Audio To Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            play_audio_to_participant_result = self.callingserver_client.play_audio_to_participant(
                call_locator=GroupCallLocator(group_id),
                participant=CommunicationUserIdentifier(added_participant), 
                audio_url = CONST.AUDIO_FILE_URL,
                is_looped=True,
                audio_file_id=str(uuid.uuid4()),
                callback_uri=CONST.AppCallbackUrl)

            assert play_audio_to_participant_result.operation_id is not None

            # Cancel Participant Media Operation 
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            self.callingserver_client.cancel_participant_media_operation(
                call_locator=GroupCallLocator(group_id),
                participant=CommunicationUserIdentifier(added_participant),
                media_operation_id=play_audio_to_participant_result.operation_id
            )

            # Remove Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            self.callingserver_client.remove_participant(
                GroupCallLocator(group_id),
                CommunicationUserIdentifier(added_participant)
                )

        except Exception as ex:
            print(str(ex))
        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    def test_create_add_get_remove_participant_hangup_scenario(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_create_add_get_remove_participant_hangup_scenario")

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        CallingServerLiveTestUtils.validate_group_call_connection(call_connections)

        try:
            # Get Call Connection
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            get_call_connection = self.callingserver_client.get_call_connection(call_connections[0].call_connection_id)
            assert get_call_connection.call_connection_id is not None
            
            # Add Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            added_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.participant_guid)
            add_participant_result = self.callingserver_client.add_participant(
                call_locator=GroupCallLocator(group_id),
                participant=CommunicationUserIdentifier(added_participant),
                callback_uri=CONST.AppCallbackUrl,
                alternate_caller_id=None,
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

            # Get Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            get_participant_result = self.callingserver_client.get_participant(GroupCallLocator(group_id), CommunicationUserIdentifier(added_participant))
            assert get_participant_result.participant_id is not None

            # Get all Participants
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            get_all_participants = self.callingserver_client.list_participants(GroupCallLocator(group_id))  
            assert len(get_all_participants)  > 2
       
            # Remove Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            self.callingserver_client.remove_participant(
                GroupCallLocator(group_id),
                CommunicationUserIdentifier(added_participant)
                )
        except Exception as ex:
            print(str(ex))
        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    def test_run_all_client_functions(self):
        group_id = CallingServerLiveTestUtils.get_group_id("test_run_all_client_functions")

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        try:
            start_call_recording_result = self.callingserver_client.start_recording(GroupCallLocator(group_id), CONST.CALLBACK_URI)
            recording_id = start_call_recording_result.recording_id

            assert recording_id is not None
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            recording_state = self.callingserver_client.get_recording_properties(recording_id)
            assert recording_state.recording_state == "active"

            self.callingserver_client.pause_recording(recording_id)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            recording_state = self.callingserver_client.get_recording_properties(recording_id)
            assert recording_state.recording_state == "inactive"

            self.callingserver_client.resume_recording(recording_id)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            recording_state = self.callingserver_client.get_recording_properties(recording_id)
            assert recording_state.recording_state == "active"

            self.callingserver_client.stop_recording(recording_id)

        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    def test_start_recording_fails(self):
        with self.assertRaises(HttpResponseError):
            self.callingserver_client.start_recording(ServerCallLocator(self.invalid_server_call_id), CONST.CALLBACK_URI)

    def test_start_recording_relative_uri_fails(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_start_recording_relative_uri_fails")

        try:
            with self.assertRaises(HttpResponseError):
                self.callingserver_client.start_recording(GroupCallLocator(group_id), "/not/absolute/uri")
        except Exception as ex:
            print(str(ex))

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_delete_success(self):
        delete_url = CallingServerLiveTestUtils.get_delete_url()
        self.callingserver_client.delete_recording(delete_url)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_delete_content_not_exists(self):
        delete_url = CallingServerLiveTestUtils.get_invalid_delete_url()
        with self.assertRaises(HttpResponseError):
            self.callingserver_client.delete_recording(delete_url)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    def test_delete_content_unauthorized(self):
        delete_url = CallingServerLiveTestUtils.get_delete_url()
        unauthorized_client = CallingServerClient.from_connection_string("endpoint=https://test.communication.azure.com/;accesskey=1234")
        with self.assertRaises(HttpResponseError):
            unauthorized_client.delete_recording(delete_url)

    def test_join_play_cancel_media_hangup_scenario(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_join_play_cancel_media_hangup_scenario")

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        CallingServerLiveTestUtils.validate_group_call_connection(call_connections)

        try:
            # Play Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            play_audio_result = self.callingserver_client.play_audio(
                GroupCallLocator(group_id),
                CONST.AUDIO_FILE_URL,
                is_looped = True,
                audio_file_id = str(uuid.uuid4()),
                callback_uri = CONST.AppCallbackUrl,
                operation_context = OperationContext
                )

            CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

            # Cancel Prompt Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            self.callingserver_client.cancel_media_operation(
                call_locator=GroupCallLocator(group_id), 
                media_operation_id=play_audio_result.operation_id )
        except Exception as ex:
            print(str(ex))
        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)
