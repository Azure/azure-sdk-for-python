# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import uuid
import os
import pytest
import utils._test_constants as CONST

from azure.communication.callingserver import (
    CallingServerClient,
    PlayAudioOptions,
    PhoneNumberIdentifier,
    CreateCallOptions,
    MediaType,
    EventSubscriptionType,
    CommunicationUserIdentifier
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
from utils._live_test_utils import CallingServerLiveTestUtils
from utils._test_mock_utils import FakeTokenCredential
from utils._test_utils import TestUtils

SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS = is_live and os.getenv("SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS", "false") == "true"
CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON = "SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS skips certain callingserver tests that required human interaction"

@pytest.mark.skipif(SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
class CallConnectionTest(CommunicationTestCase):

    def setUp(self):
        super(CallConnectionTest, self).setUp()

        self.from_user = TestUtils.get_new_user_id(self.connection_str)
        self.to_user = TestUtils.get_new_user_id(self.connection_str)

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
        endpoint = endpoint

        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()

        self.callingserver_client = CallingServerClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )

    def test_create_play_cancel_hangup_scenario(self):
        # create option
        options = CreateCallOptions(
            callback_uri=CONST.AppCallbackUrl,
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED, EventSubscriptionType.DTMF_RECEIVED]
        )
        options.alternate_Caller_Id = PhoneNumberIdentifier(self.from_phone_number)

        # Establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    options=options,
                    )

        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        if is_live():
            time.sleep(10)

        # Play Audio
        OperationContext = str(uuid.uuid4())
        AudioFileId = str(uuid.uuid4())
        options = PlayAudioOptions(
            loop = True,
            audio_file_id = AudioFileId,
            callback_uri = CONST.AppCallbackUrl,
            operation_context = OperationContext
            )

        play_audio_result = call_connection.play_audio(
            CONST.AudioFileUrl,
            options
            )

        CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

        # Cancel All Media Operations
        CancelMediaOperationContext = str(uuid.uuid4())
        cancel_all_media_operations_result = call_connection.cancel_all_media_operations(
            CancelMediaOperationContext
            )

        CallingServerLiveTestUtils.validate_cancel_all_media_operations(cancel_all_media_operations_result)
        if is_live():
            time.sleep(5)

        # Hang up
        call_connection.hang_up()

    def test_create_add_remove_hangup_scenario(self):
        # create option
        options = CreateCallOptions(
            callback_uri=CONST.AppCallbackUrl,
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED, EventSubscriptionType.DTMF_RECEIVED]
        )
        options.alternate_Caller_Id = PhoneNumberIdentifier(self.from_phone_number)

        # Establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    options=options,
                    )

        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        if is_live():
            time.sleep(10)

        # Add Participant
        OperationContext = str(uuid.uuid4())
        add_participant_result = call_connection.add_participant(
            participant=CommunicationUserIdentifier(self.to_user),
            alternate_caller_id=None,
            operation_context=OperationContext
            )

        CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

        participant_id=add_participant_result.participant_id

        # Remove Participant
        call_connection.remove_participant(participant_id)

        if is_live():
            time.sleep(5)

        # Hang up
        call_connection.hang_up()
