# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import uuid
import os
import pytest
import urllib.parse
from azure.communication.callingserver.aio import CallingServerClient, CallConnection
from azure.communication.callingserver import PlayAudioOptions, PhoneNumberIdentifier, CreateCallOptions, MediaType, EventSubscriptionType
from azure.communication.callingserver._shared.utils import parse_connection_str
from azure.communication.identity.aio import CommunicationIdentityClient
from live_test_utils._test_utils_async import CallingServerLiveTestUtils
from azure.identity.aio import DefaultAzureCredential
from _shared.asynctestcase  import AsyncCommunicationTestCase
from _shared.testcase import (
    BodyReplacerProcessor, ResponseReplacerProcessor
)
from devtools_testutils import is_live
from _shared.utils import get_http_logging_policy

SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS = is_live and os.getenv("SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS", "false") == "true"
CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON = "SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS skips certain callingserver tests that required human interaction"

IncomingRequestSecret = "helloworld"
AppBaseUrl = "https://dummy.ngrok.io"
AppCallbackUrl = f"{AppBaseUrl}/api/incident/callback?SecretKey={urllib.parse.quote(IncomingRequestSecret)}"
AudioFileName = "sample-message.wav"
AudioFileUrl = f"{AppBaseUrl}/audio/{AudioFileName}"

@pytest.mark.skipif(SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS, reason=CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON)
class CallingServerClientTestAsync(AsyncCommunicationTestCase):

    def setUp(self):
        super(CallingServerClientTestAsync, self).setUp()
    
        if self.is_playback():
            self.from_phone_number = "+15551234567"
            self.to_phone_number = "+15551234567"
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "communicationUser", "callConnectionId", "callbackUri"])])
        else:
            self.to_phone_number = os.getenv("AZURE_PHONE_NUMBER")
            self.from_phone_number = os.getenv("ALTERNATE_CALLERID")
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "communicationUser", "callConnectionId", "callbackUri"]),
                ResponseReplacerProcessor(keys=[self._resource_name])])
        
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_create_play_cancel_hangup_scenario_async(self):

        # Establish a call
        # create identity client
        self.identity_client = CommunicationIdentityClient.from_connection_string(self.connection_str)

        # create source
        self.from_user = await self.identity_client.create_user()

        # create target
        self.to_user = PhoneNumberIdentifier(self.to_phone_number)
        
        # create option
        self.options = CreateCallOptions(
            callback_uri=AppCallbackUrl,
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED, EventSubscriptionType.DTMF_RECEIVED]
        )
        self.options.alternate_Caller_Id = PhoneNumberIdentifier(self.from_phone_number)

        # create CallingServerClient
        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint
    
        self.callingserver_client = CallingServerClient(
            self.endpoint, 
            DefaultAzureCredential(), 
            http_logging_policy=get_http_logging_policy()
        )

        async with self.callingserver_client:
            self.call_connection_async = await self.callingserver_client.create_call_connection(
                        source=self.from_user,
                        targets=[self.to_user],
                        options=self.options,
                        )
            
            CallingServerLiveTestUtils.validate_callconnection_Async(self.call_connection_async)
            time.sleep(10)

            async with self.call_connection_async:
                # Play Audio
                OperationContext = str(uuid.uuid4())
                AudioFileId = str(uuid.uuid4())
                options = PlayAudioOptions(
                    loop = True,
                    audio_file_id = AudioFileId,
                    callback_uri = AppCallbackUrl,
                    operation_context = OperationContext
                    )

                play_audio_result = await self.call_connection_async.play_audio(
                    AudioFileUrl,
                    options
                    )

                CallingServerLiveTestUtils.validate_play_audio_result_Async(play_audio_result)

                # Cancel All Media Operations
                CancelMediaOperationContext = str(uuid.uuid4())
                cancel_all_media_operations_result = await self.call_connection_async.cancel_all_media_operations(
                    CancelMediaOperationContext
                    )   

                CallingServerLiveTestUtils.validate_cancel_all_media_operations_Async(cancel_all_media_operations_result)
                time.sleep(5)

                # Hang up
                await self.call_connection_async.hang_up()

