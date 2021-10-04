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
    PlayAudioOptions,
    CommunicationUserIdentifier,
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

from azure.core.exceptions import HttpResponseError

class ServerCallTest(CommunicationTestCase):

    def setUp(self):
        super(ServerCallTest, self).setUp()

        self.from_user = CallingServerLiveTestUtils.get_new_user_id(self.connection_str)
        self.to_user = CallingServerLiveTestUtils.get_new_user_id(self.connection_str)

        if self.is_playback():
            self.from_phone_number = "+15551234567"
            self.to_phone_number = "+15551234567"
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "callbackUri"])])
        else:
            self.to_phone_number = os.getenv("AZURE_PHONE_NUMBER")
            self.from_phone_number = os.getenv("ALTERNATE_CALLERID")
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "callbackUri"]),
                ResponseReplacerProcessor(keys=[self._resource_name])])

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

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    def test_join_play_cancel_hangup_scenario(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_join_play_cancel_hangup_scenario")

        if self.is_live:
            self.recording_processors.extend([
            RequestReplacerProcessor(keys=group_id,
                replacement=CallingServerLiveTestUtils.get_playback_group_id("test_join_play_cancel_hangup_scenario"))])

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        # initialize a Server Call
        server_call = self.callingserver_client.initialize_server_call(group_id)

        try:
            # Play Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            options = PlayAudioOptions(
                loop = True,
                audio_file_id = str(uuid.uuid4()),
                callback_uri = CONST.AppCallbackUrl,
                operation_context = OperationContext
                )
            play_audio_result = server_call.play_audio(
                CONST.AudioFileUrl,
                options
                )
            CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

            # Cancel Prompt Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.cancel_all_media_operations_for_group_call(call_connections)
        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    def test_create_add_remove_hangup_scenario(self):
        # create GroupCalls
        group_id = CallingServerLiveTestUtils.get_group_id("test_create_add_remove_hangup_scenario")

        if self.is_live:
            self.recording_processors.extend([
            RequestReplacerProcessor(keys=group_id,
                replacement=CallingServerLiveTestUtils.get_playback_group_id("test_create_add_remove_hangup_scenario"))])

        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        # initialize a Server Call
        server_call = self.callingserver_client.initialize_server_call(group_id)

        try:
            # Add Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            add_participant_result = server_call.add_participant(
                participant=CommunicationUserIdentifier(CallingServerLiveTestUtils.get_fixed_user_id("0000000c-9f68-6fd6-e57b-254822002248")),
                callback_uri=None,
                alternate_caller_id=None,
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

            # Remove Participant
            participant_id=add_participant_result.participant_id
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            server_call.remove_participant(participant_id)
        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    def test_run_all_client_functions(self):
        group_id = CallingServerLiveTestUtils.get_group_id("test_run_all_client_functions")

        if self.is_live:
            self.recording_processors.extend([
            RequestReplacerProcessor(keys=group_id,
                replacement=CallingServerLiveTestUtils.get_playback_group_id("test_run_all_client_functions"))])
        
        call_connections = CallingServerLiveTestUtils.create_group_calls(
            self.callingserver_client,
            group_id,
            self.from_user,
            self.to_user,
            CONST.CALLBACK_URI
            )

        try:
            start_call_recording_result = self.callingserver_client.start_recording(ServerCallLocator(group_id), CONST.CALLBACK_URI)
            recording_id = start_call_recording_result.recording_id

            assert recording_id is not None
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            recording_state = self.callingserver_client.get_recording_properities(recording_id)
            assert recording_state.recording_state == "active"

            self.callingserver_client.pause_recording(recording_id)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            recording_state = self.callingserver_client.get_recording_properities(recording_id)
            assert recording_state.recording_state == "inactive"

            self.callingserver_client.resume_recording(recording_id)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            recording_state = self.callingserver_client.get_recording_properities(recording_id)
            assert recording_state.recording_state == "active"

            self.callingserver_client.stop_recording(recording_id)

        finally:
            # Clean up/Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            CallingServerLiveTestUtils.clean_up_connections(call_connections)

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    def test_start_recording_fails(self):
        invalid_server_call_id = "aHR0cHM6Ly9jb252LXVzd2UtMDkuY29udi5za3lwZS5jb20vY29udi9EZVF2WEJGVVlFV1NNZkFXYno2azN3P2k9MTEmZT02Mzc1NzIyMjk0Mjc0NTI4Nzk="

        with self.assertRaises(HttpResponseError):
            self.callingserver_client.start_recording(ServerCallLocator(invalid_server_call_id), CONST.CALLBACK_URI)
