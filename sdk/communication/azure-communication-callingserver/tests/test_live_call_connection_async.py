# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
import os
import pytest
import utils._test_constants as CONST

from azure.communication.callingserver.aio import CallingServerClient
from azure.communication.callingserver import (
    PlayAudioOptions,
    PhoneNumberIdentifier,
    CreateCallOptions,
    CallMediaType,
    CallingEventSubscriptionType,
    CommunicationUserIdentifier
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
from utils._live_test_utils import CallingServerLiveTestUtils
from utils._test_mock_utils_async import FakeTokenCredential_Async

class CallConnectionTestAsync(AsyncCommunicationTestCase):

    def setUp(self):
        super(CallConnectionTestAsync, self).setUp()

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
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )

    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_play_cancel_hangup_scenario_async(self):
        # create call option
        options = CreateCallOptions(
            callback_uri=CONST.AppCallbackUrl,
            requested_media_types=[CallMediaType.AUDIO],
            requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED, CallingEventSubscriptionType.TONE_RECEIVED]
        )
        options.alternate_Caller_Id = PhoneNumberIdentifier(self.from_phone_number)

        # Establish a call
        async with self.callingserver_client:
            call_connection_async = await self.callingserver_client.create_call_connection(
                        source=CommunicationUserIdentifier(self.from_user),
                        targets=[PhoneNumberIdentifier(self.to_phone_number)],
                        options=options
                        )
            CallingServerLiveTestUtilsAsync.validate_callconnection_Async(call_connection_async)

            async with call_connection_async:
                try:
                    # Play Audio
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    OperationContext = str(uuid.uuid4())
                    AudioFileId = str(uuid.uuid4())
                    options = PlayAudioOptions(
                        loop = True,
                        audio_file_id = AudioFileId,
                        callback_uri = CONST.AppCallbackUrl,
                        operation_context = OperationContext
                        )
                    play_audio_result = await call_connection_async.play_audio(
                        CONST.AudioFileUrl,
                        options
                        )
                    CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

                    # Cancel All Media Operations
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    CancelMediaOperationContext = str(uuid.uuid4())
                    cancel_all_media_operations_result = await call_connection_async.cancel_all_media_operations(
                        CancelMediaOperationContext
                        )
                    CallingServerLiveTestUtils.validate_cancel_all_media_operations(cancel_all_media_operations_result)
                finally:
                    # Hang up
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await call_connection_async.hang_up()

    @pytest.mark.skip(reason="Skip because the server side bits not ready")
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_add_remove_hangup_scenario_async(self):
        # create call option
        options = CreateCallOptions(
            callback_uri=CONST.AppCallbackUrl,
            requested_media_types=[CallMediaType.AUDIO],
            requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED, CallingEventSubscriptionType.TONE_RECEIVED]
        )
        options.alternate_Caller_Id = PhoneNumberIdentifier(self.from_phone_number)

        # Establish a call
        async with self.callingserver_client:
            call_connection_async = await self.callingserver_client.create_call_connection(
                        source=CommunicationUserIdentifier(self.from_user),
                        targets=[PhoneNumberIdentifier(self.to_phone_number)],
                        options=options
                        )
            CallingServerLiveTestUtils.validate_callconnection(call_connection_async)

            async with call_connection_async:
                try:
                    # Add Participant
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    OperationContext = str(uuid.uuid4())
                    add_participant_result = await call_connection_async.add_participant(
                        participant=CommunicationUserIdentifier(CallingServerLiveTestUtils.get_fixed_user_id("0000000c-9f68-6fd6-e57b-254822002248")),
                        alternate_caller_id=None,
                        operation_context=OperationContext
                        )
                    CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

                    # Remove Participant
                    participant_id=add_participant_result.participant_id
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await call_connection_async.remove_participant(participant_id)
                finally:
                    # Hang up
                    CallingServerLiveTestUtils.sleep_if_in_live_mode()
                    await call_connection_async.hang_up()
