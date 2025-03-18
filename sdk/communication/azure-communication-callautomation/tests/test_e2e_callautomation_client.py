# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
import time
import pytest

from azure.communication.callautomation._models import ChannelAffinity, ServerCallLocator
from devtools_testutils import recorded_by_proxy

from callautomation_test_case import CallAutomationRecordedTestCase
from azure.communication.callautomation._shared.models import CommunicationUserIdentifier, identifier_from_raw_id


class TestCallAutomationClientAutomatedLiveTest(CallAutomationRecordedTestCase):

    @recorded_by_proxy
    def test_create_VOIP_call_and_answer_then_hangup(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = self.check_for_event(
            "ParticipantsUpdated", call_connection._call_connection_id, timedelta(seconds=15)
        )

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_add_participant_then_cancel_request(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id(self.identity_client.create_user().raw_id)
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = self.check_for_event(
            "ParticipantsUpdated", call_connection._call_connection_id, timedelta(seconds=15)
        )

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        add_participant_result = call_connection.add_participant(participant_to_add)

        # ensure invitation is sent
        time.sleep(3)

        call_connection.cancel_add_participant_operation(add_participant_result.invitation_id)

        cancel_add_participant_succeeded_event = self.check_for_event(
            "CancelAddParticipantSucceeded", call_connection._call_connection_id, timedelta(seconds=15)
        )

        if cancel_add_participant_succeeded_event is None:
            raise ValueError("Caller CancelAddParticipantSucceeded event is None")

        self.terminate_call(unique_id)
        return
    
    @pytest.mark.skip(reason="""Playback fails for same event type triggered and test recording code
                       takes the event type has the dictionary it fails to recording call connected event for the connect api""")
    @recorded_by_proxy
    def test_create_VOIP_call_and_connect_call_then_hangup(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = self.establish_callconnection_voip_connect_call(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        call_connection_properties = call_connection.get_call_properties()
        server_call_id = call_connection_properties.server_call_id

        # connect call request.
        connect_call_connection = call_automation_client.connect_call(
            server_call_id=server_call_id,
            callback_url=callback_url,
            )

        # check returned call connected events
        connect_call_connected_event = self.check_for_event('CallConnected', connect_call_connection.call_connection_id, timedelta(seconds=20))
        if connect_call_connected_event is None:
            raise ValueError("Caller CallConnected event is None")

        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_create_VOIP_call_and_answer_custom_context(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip_answercall_withcustomcontext(caller, target)

        # check returned events
        connected_event = self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = self.check_for_event(
            "ParticipantsUpdated", call_connection._call_connection_id, timedelta(seconds=15)
        )

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_start_recording_with_call_connection_id(self):
     # try to establish the call
     caller = self.identity_client.create_user()
     target = self.identity_client.create_user()
     unique_id, call_connection, _, call_automation_client, callback_url = self.establish_callconnection_voip_connect_call(caller, target)

     # check returned events
     connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
     participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

     if connected_event is None:
         raise ValueError("Caller CallConnected event is None")
     if participant_updated_event is None:
         raise ValueError("Caller ParticipantsUpdated event is None")

     call_connection_properties = call_connection.get_call_properties()
     call_connection_id = call_connection_properties.call_connection_id
     target_participant = CommunicationUserIdentifier("testId")
     channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)
     
     # start recording request with call connection id.
     start_recording = call_automation_client.start_recording(call_connection_id=call_connection_id, recording_state_callback_url=callback_url, channel_affinity=[channel_affinity]
         )
     time.sleep(5)

     # check for RecordingStateChanged event
     recording_state_changed_event = self.check_for_event('RecordingStateChanged', call_connection_id, timedelta(seconds=30))
     if recording_state_changed_event is None:
         raise ValueError("RecordingStateChanged event is None")
     
     # stop recording request.
     call_automation_client.stop_recording(recording_id=start_recording.recording_id)
     time.sleep(3)
     
     self.terminate_call(unique_id)
     return

    @recorded_by_proxy
    def test_start_recording_with_server_call_id(self):
     # try to establish the call
     caller = self.identity_client.create_user()
     target = self.identity_client.create_user()
     unique_id, call_connection, _, call_automation_client, callback_url = self.establish_callconnection_voip_connect_call(caller, target)

     # check returned events
     connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
     participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

     if connected_event is None:
         raise ValueError("Caller CallConnected event is None")
     if participant_updated_event is None:
         raise ValueError("Caller ParticipantsUpdated event is None")

     call_connection_properties = call_connection.get_call_properties()
     call_connection_id = call_connection_properties.call_connection_id
     server_call_id = call_connection_properties.server_call_id
     target_participant = CommunicationUserIdentifier("testId")
     channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)

     # start recording request with call connection id.
     start_recording = call_automation_client.start_recording(server_call_id = server_call_id, recording_state_callback_url=callback_url, channel_affinity=[channel_affinity]
         )
     time.sleep(5)

     # check for RecordingStateChanged event
     recording_state_changed_event = self.check_for_event('RecordingStateChanged', call_connection_id, timedelta(seconds=30))
     if recording_state_changed_event is None:
         raise ValueError("RecordingStateChanged event is None")
     
     # stop recording request.
     call_automation_client.stop_recording(recording_id=start_recording.recording_id)
     time.sleep(3)
     
     self.terminate_call(unique_id)
     return
