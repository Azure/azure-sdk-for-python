import asyncio
import time
import os
from datetime import timedelta
from typing import Dict, Any, List, Optional

import pytest
from devtools_testutils import recorded_by_proxy

from azure.communication.callautomation.aio import (
    CallAutomationClient as AsyncCallAutomationClient,
    CallConnectionClient as AsyncCallConnectionClient,
)
from azure.communication.callautomation._shared.models import  identifier_from_raw_id

from callautomation_test_case_async import AsyncCallAutomationRecordedTestCase   

class TestCallAutomationClientAutomatedLiveTestAsync(AsyncCallAutomationRecordedTestCase):

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_create_VOIP_call_and_answer_then_hangup_async(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        call_connection_id, call_connection, _ = await self.establish_callconnection_voip_async(caller, target)

        connected_event = await self.check_for_event(
            "CallConnected", call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
            "ParticipantsUpdated", call_connection_id, timedelta(seconds=15)
        )

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        await self.terminate_call(call_connection_id)

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_add_participant_then_cancel_request_async(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id((await self.identity_client.create_user()).raw_id)
        call_connection_id, call_connection, _ = await self.establish_callconnection_voip_async(caller, target)

        connected_event = await self.check_for_event(
            "CallConnected", call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
            "ParticipantsUpdated", call_connection_id, timedelta(seconds=15)
        )

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        add_participant_result = await call_connection.add_participant(participant_to_add)
        await asyncio.sleep(3)
        await call_connection.cancel_add_participant_operation(add_participant_result.invitation_id)

        cancel_add_participant_succeeded_event = await self.check_for_event(
            "CancelAddParticipantSucceeded", call_connection_id, timedelta(seconds=15)
        )

        assert cancel_add_participant_succeeded_event is not None, "Caller CancelAddParticipantSucceeded event is None"

        await self.terminate_call(call_connection_id)

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_create_VOIP_call_and_connect_call_then_hangup_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = await self.establish_callconnection_voip_connect_call_async(caller, target)

        # check returned events
        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        call_connection_properties = await call_connection.get_call_properties()
        server_call_id = call_connection_properties.server_call_id

        # connect call request.
        connect_call_connection = await call_automation_client.connect_call(
            server_call_id=server_call_id,
            callback_url=callback_url,
        )

        # check returned call connected events
        connect_call_connected_event = await self.check_for_event('CallConnected', connect_call_connection.call_connection_id, timedelta(seconds=20))
        assert connect_call_connected_event is not None, "Caller CallConnected event is None"

        await self.terminate_call(unique_id)
        return
    
    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_create_VOIP_call_and_answer_custom_context_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip_answercall_withcustomcontext_async(caller, target)

        # check returned events
        connected_event = await self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
            "ParticipantsUpdated", call_connection._call_connection_id, timedelta(seconds=15)
        )

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_start_recording_with_call_connection_id_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = await self.establish_callconnection_voip_connect_call_async(caller, target)

        # check returned events
        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        call_connection_properties = await self.get_call_properties_async(call_connection)
        call_connection_id = call_connection_properties.call_connection_id

        # start recording request with call connection id
        start_recording = await self.start_recording_with_call_connection_id_async(
            call_automation_client,
            call_connection_id,
            callback_url
        )
        await asyncio.sleep(5)

        # check for RecordingStateChanged event
        recording_state_changed_event = await self.check_for_event('RecordingStateChanged', call_connection_id, timedelta(seconds=30))
        assert recording_state_changed_event is not None, "RecordingStateChanged event is None"

        # stop recording request
        await self.stop_recording_async(call_automation_client, start_recording.recording_id)
        await asyncio.sleep(3)

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_start_recording_with_server_call_id_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = await self.establish_callconnection_voip_connect_call_async(caller, target)

        # check returned events
        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        call_connection_properties = await self.get_call_properties_async(call_connection)
        call_connection_id = call_connection_properties.call_connection_id
        server_call_id = call_connection_properties.server_call_id

        # start recording request with server call id
        start_recording = await self.start_recording_with_server_call_id_async(
            call_automation_client,
            server_call_id,
            callback_url
        )
        await asyncio.sleep(5)

        # check for RecordingStateChanged event
        recording_state_changed_event = await self.check_for_event('RecordingStateChanged', call_connection_id, timedelta(seconds=30))
        assert recording_state_changed_event is not None, "RecordingStateChanged event is None"

        # stop recording request
        await self.stop_recording_async(call_automation_client, start_recording.recording_id)
        await asyncio.sleep(3)

        await self.terminate_call(unique_id)
        return
