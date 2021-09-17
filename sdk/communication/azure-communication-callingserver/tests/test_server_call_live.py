# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
from time import sleep
from datetime import datetime
from uuid import UUID, uuid4

from azure.communication.identity import CommunicationIdentityClient
from azure.communication.callingserver import (
    CallingServerClient,
    CreateCallOptions
)

from azure.communication.callingserver._models import (
    EventSubscriptionType,
    JoinCallOptions,
    MediaType
)

from azure.communication.callingserver._shared.models import (
    CommunicationUserIdentifier,
    PhoneNumberIdentifier
)

from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor
)

from typing import (
    cast,
    Tuple,
)
from azure.core.exceptions import HttpResponseError

from helper import URIIdentityReplacer, CallingServerURIReplacer
from _shared.utils import get_http_logging_policy

class CallConnectionLiveTest(CommunicationTestCase):
    def setUp(self):
        super().setUp()

        self.identity_client = CommunicationIdentityClient.from_connection_string(
            self.connection_str)

        # if self.is_live:
        #     self.identity_client = CommunicationIdentityClient.from_connection_string(
        #     self.connection_str)
        #     self.user = self.identity_client.create_user()
        # else:
        #     self.user = "8:acs:" + self.variables_map["AZURE_TENANT_ID"] + "_" + str(uuid4())

        # create CallingServerClient
        self.calling_server_client = CallingServerClient.from_connection_string(self.connection_str,
        http_logging_policy=get_http_logging_policy())
        # TODO: Check for the logging policy to match Java's

        self.recording_processors.extend([
            BodyReplacerProcessor(keys=["recordingId"]),
            URIIdentityReplacer(),
            CallingServerURIReplacer()])

    def tearDown(self):
        super().tearDown()

        # delete created users and chat threads
        # if not self.is_playback():
        #     self.identity_client.delete_user(self.user)

    # @pytest.mark.live_test_only
    def test_run_all_client_functions(self):
        if self.is_playback():
            group_id = "sanitized"
        else:
            group_id = str(uuid4())

        from_user = "8:acs:" + self.variables_map["AZURE_TENANT_ID"] + "_" + str(uuid4())
        to_user = "8:acs:" + self.variables_map["AZURE_TENANT_ID"] + "_" + str(uuid4())
        from_participant = CommunicationUserIdentifier(from_user)
        to_participant = CommunicationUserIdentifier(to_user)

        call_options = JoinCallOptions(
            callback_uri=self.variables_map["CALLBACK_URI"],
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED]
        )

        from_call_connection = self.calling_server_client.join_call(group_id, from_participant,
            call_options)
        sleep(1)
        assert from_call_connection is not None
        assert from_call_connection.call_connection_id is not None
        assert from_call_connection.call_connection_id

        to_call_connection = self.calling_server_client.join_call(group_id, to_participant,
            call_options)
        sleep(1)
        assert to_call_connection is not None
        assert to_call_connection.call_connection_id is not None
        assert to_call_connection.call_connection_id

        server_call = self.calling_server_client.initialize_server_call(group_id)
        start_call_recording_result = server_call.start_recording(self.variables_map["CALLBACK_URI"])
        recording_id = start_call_recording_result.recording_id

        assert server_call is not None
        assert server_call.server_call_id is not None
        assert recording_id is not None
        sleep(7)

        recording_state = server_call.get_recording_properities(recording_id)
        assert recording_state.recording_state == "active"

        server_call.pause_recording(recording_id)
        sleep(7)
        recording_state = server_call.get_recording_properities(recording_id)
        assert recording_state.recording_state == "inactive"

        server_call.resume_recording(recording_id)
        sleep(7)
        recording_state = server_call.get_recording_properities(recording_id)
        assert recording_state.recording_state == "active"

        server_call.stop_recording(recording_id)

        from_call_connection.hang_up()
        to_call_connection.hang_up()

    def test_start_recording_fails(self):
        invalid_server_call_id = "aHR0cHM6Ly9jb252LXVzd2UtMDkuY29udi5za3lwZS5jb20vY29udi9EZVF2WEJGVVlFV1NNZkFXYno2azN3P2k9MTEmZT02Mzc1NzIyMjk0Mjc0NTI4Nzk="
        server_call = self.calling_server_client.initialize_server_call(invalid_server_call_id)

        with self.assertRaises(HttpResponseError):
            server_call.start_recording(self.variables_map["CALLBACK_URI"])