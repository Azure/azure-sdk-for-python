# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
import time
from datetime import datetime
from devtools_testutils import AzureTestCase
from msrest.serialization import TZ_UTC
from uuid import UUID, uuid4

from azure.communication.identity import CommunicationIdentityClient
from azure.communication.callingserver import (
    CallingServerClient,
    CreateCallOptions
)

from azure.communication.callingserver._models import (
    EventSubscriptionType,
    MediaType
)

from azure.communication.callingserver._shared.models import (
    CommunicationUserIdentifier,
    PhoneNumberIdentifier
)

from azure_devtools.scenario_tests import RecordingProcessor
from helper import URIIdentityReplacer
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)

from typing import (
    cast,
    Tuple,
)

from _shared.utils import get_http_logging_policy

class CallConnectionLiveTest(CommunicationTestCase):
    def setUp(self):
        super(CallConnectionLiveTest, self).setUp()

        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)

        # create user and issue token
        self.user = self.identity_client.create_user()
        # tokenresponse = self.identity_client.get_token(self.user, scopes=["chat"])
        # self.token = tokenresponse.token

        # create CallingServerClient
        self.calling_server_client = CallingServerClient.from_connection_string(self.connection_str,
            http_logging_policy=get_http_logging_policy())
        # TODO: Check for the logging policy to match Java's

    def tearDown(self):
        super(CallConnectionLiveTest, self).tearDown()

        # delete created users and chat threads
        if not self.is_playback():
            self.identity_client.delete_user(self.user)

    # @pytest.mark.live_test_only
    def test_create_play_cancel_hangup_scenario(self):
        # Establish call
        call_options = CreateCallOptions(callback_uri="", requested_media_types=MediaType.AUDIO,
            requested_call_events=EventSubscriptionType.PARTICIPANTS_UPDATED)
        call_options.alternate_Caller_Id = PhoneNumberIdentifier("")

        call_connection = self.calling_server_client.create_call_connection(
            CommunicationUserIdentifier(""),
            [PhoneNumberIdentifier("")],
            call_options
            )
        
        assert call_connection is not None
        assert call_connection.call_connection_id is not None
        assert call_connection.call_connection_id

        # Play Audio
        play_audio_operation_context = str(uuid4())
        play_audio_result = call_connection.play_audio(
            audio_file_uri="",
            audio_File_id="",
            callback_uri=None,
            operation_context=play_audio_operation_context,
            loop=False
        )

        assert play_audio_result is not None
        assert play_audio_result.operation_id is not None
        assert play_audio_result.operation_id
        assert play_audio_result.status is not None
        assert play_audio_result.status == "Running"

        # Cancel all media operations
        cancel_media_operation_context = str(uuid4())
        cancel_media_operation_result = call_connection.cancel_all_media_operations(
            cancel_media_operation_context
        )

        assert cancel_media_operation_result is not None
        assert cancel_media_operation_result.operation_id is not None
        assert cancel_media_operation_result.operation_id
        assert cancel_media_operation_result.status is not None
        assert cancel_media_operation_result.status == "Completed"

        # Hangup
        call_connection.hang_up()

