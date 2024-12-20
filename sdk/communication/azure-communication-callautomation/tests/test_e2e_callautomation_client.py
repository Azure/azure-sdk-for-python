# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
import time
import pytest

from devtools_testutils import recorded_by_proxy

from callautomation_test_case import CallAutomationRecordedTestCase
from azure.communication.callautomation._shared.models import identifier_from_raw_id


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
