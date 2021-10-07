# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os, uuid, pytest
from time import sleep

import utils._test_constants as CONST
from azure.communication.callingserver.aio import CallingServerClient
from azure.communication.callingserver import (
    PlayAudioOptions,
    CommunicationUserIdentifier,
    ServerCallLocator
    )

from azure.communication.callingserver._shared.utils import parse_connection_str
from azure.identity.aio import DefaultAzureCredential
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.testcase import (
    BodyReplacerProcessor, ResponseReplacerProcessor
)
from devtools_testutils import is_live
from _shared.utils import get_http_logging_policy
from utils._live_test_utils_async import CallingServerLiveTestUtilsAsync
from utils._live_test_utils import CallingServerLiveTestUtils, RequestReplacerProcessor
from utils._test_mock_utils_async import FakeTokenCredential_Async

from azure.core.exceptions import HttpResponseError

class ServerCallTestAsync(AsyncCommunicationTestCase):

    def setUp(self):
        super(ServerCallTestAsync, self).setUp()

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
            credential = FakeTokenCredential_Async()
        else:
            credential = DefaultAzureCredential()

        self.callingserver_client = CallingServerClient(
            self.endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_join_play_cancel_hangup_scenario_async(self):
        async with self.callingserver_client:
            # create GroupCalls
            group_id = CallingServerLiveTestUtils.get_group_id("test_join_play_cancel_hangup_scenario_async")

            if self.is_live:
                self.recording_processors.extend([
                RequestReplacerProcessor(keys=group_id,
                    replacement=CallingServerLiveTestUtils.get_playback_group_id("test_join_play_cancel_hangup_scenario_async"))])

            call_connections = await CallingServerLiveTestUtilsAsync.create_group_calls_async(
                self.callingserver_client,
                group_id,
                self.from_user,
                self.to_user,
                CONST.CALLBACK_URI
                )

            # initialize a Server Call
            server_call_async = self.callingserver_client.initialize_server_call(group_id)

            async with server_call_async:
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
                    play_audio_result = await server_call_async.play_audio(
                        CONST.AudioFileUrl,
                        options
                        )
                    CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

                    # Cancel Prompt Audio
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await CallingServerLiveTestUtilsAsync.cancel_all_media_operations_for_group_call_async(call_connections)
                finally:
                    # Clean up/Hang up
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await CallingServerLiveTestUtilsAsync.clean_up_connections_async(call_connections)

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_add_remove_hangup_scenario_async(self):
        async with self.callingserver_client:
            # create GroupCalls
            group_id = CallingServerLiveTestUtils.get_group_id("test_create_add_remove_hangup_scenario_async")

            if self.is_live:
                self.recording_processors.extend([
                RequestReplacerProcessor(keys=group_id,
                    replacement=CallingServerLiveTestUtils.get_playback_group_id("test_create_add_remove_hangup_scenario_async"))])

            call_connections = await CallingServerLiveTestUtilsAsync.create_group_calls_async(
                self.callingserver_client,
                group_id,
                self.from_user,
                self.to_user,
                CONST.CALLBACK_URI
                )

            # initialize a Server Call
            server_call_async = self.callingserver_client.initialize_server_call(group_id)

            async with server_call_async:
                try:
                    # Add Participant
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    OperationContext = str(uuid.uuid4())
                    add_participant_result = await server_call_async.add_participant(
                        participant=CommunicationUserIdentifier(CallingServerLiveTestUtils.get_fixed_user_id("0000000c-9f68-6fd6-e57b-254822002248")),
                        callback_uri=None,
                        alternate_caller_id=None,
                        operation_context=OperationContext
                        )
                    CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

                    # Remove Participant
                    participant_id=add_participant_result.participant_id
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await server_call_async.remove_participant(participant_id)
                finally:
                    # Clean up/Hang up
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await CallingServerLiveTestUtilsAsync.clean_up_connections_async(call_connections)
    
    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_run_all_client_functions(self):
        async with self.callingserver_client:
            # create GroupCalls
            group_id = CallingServerLiveTestUtils.get_group_id("test_run_all_client_functions")

            if self.is_live:
                self.recording_processors.extend([
                RequestReplacerProcessor(keys=group_id,
                    replacement=CallingServerLiveTestUtils.get_playback_group_id("test_run_all_client_functions"))])

            call_connections = await CallingServerLiveTestUtilsAsync.create_group_calls_async(
                self.callingserver_client,
                group_id,
                self.from_user,
                self.to_user,
                CONST.CALLBACK_URI
                )

            call_locator = ServerCallLocator(group_id)

            async with self.callingserver_client:
                try:
                    start_call_recording_result = await self.callingserver_client.start_recording(call_locator, CONST.CALLBACK_URI)
                    recording_id = start_call_recording_result.recording_id

                    assert recording_id is not None
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()

                    recording_state = await self.callingserver_client.get_recording_properities(recording_id)
                    assert recording_state.recording_state == "active"

                    await self.callingserver_client.pause_recording(recording_id)
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    recording_state = await self.callingserver_client.get_recording_properities(recording_id)
                    assert recording_state.recording_state == "inactive"

                    await self.callingserver_client.resume_recording(recording_id)
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    recording_state = await self.callingserver_client.get_recording_properities(recording_id)
                    assert recording_state.recording_state == "active"

                    await self.callingserver_client.stop_recording(recording_id)
                finally:
                    # Clean up/Hang up
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await CallingServerLiveTestUtilsAsync.clean_up_connections_async(call_connections)

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_start_recording_fails(self):
        invalid_server_call_id = "aHR0cHM6Ly9jb252LXVzd2UtMDkuY29udi5za3lwZS5jb20vY29udi9EZVF2WEJGVVlFV1NNZkFXYno2azN3P2k9MTEmZT02Mzc1NzIyMjk0Mjc0NTI4Nzk="

        with self.assertRaises(HttpResponseError):
            await self.callingserver_client.start_recording(ServerCallLocator(invalid_server_call_id), CONST.CALLBACK_URI)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_success(self):
        delete_url = CallingServerLiveTestUtilsAsync.get_delete_url()       
        async with self.callingserver_client:
            delete_response = await self.callingserver_client.delete_recording(delete_url)
            assert delete_response is not None
            assert delete_response.status_code == 200

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_content_not_exists(self):
        delete_url = CallingServerLiveTestUtilsAsync.get_invalid_delete_url()
        async with self.callingserver_client:
            with self.assertRaises(HttpResponseError):
                await self.callingserver_client.delete_recording(delete_url)

    @pytest.mark.skipif(CONST.SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CONST.CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_delete_content_unauthorized(self):       
        delete_url = CallingServerLiveTestUtilsAsync.get_delete_url()       
        unauthorized_client = CallingServerClient.from_connection_string("endpoint=https://test.communication.azure.com/;accesskey=1234")
        async with unauthorized_client:
            with self.assertRaises(HttpResponseError):
                await unauthorized_client.delete_recording(delete_url)