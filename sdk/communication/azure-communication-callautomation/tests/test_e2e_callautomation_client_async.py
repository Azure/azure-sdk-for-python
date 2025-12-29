# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
import time
import pytest
import asyncio

from azure.communication.callautomation._models import ChannelAffinity, ServerCallLocator
from azure.communication.callautomation._shared.models import CommunicationUserIdentifier, identifier_from_raw_id
from devtools_testutils.aio import recorded_by_proxy_async

from callautomation_test_case_async import CallAutomationRecordedTestCaseAsync


class TestCallAutomationClientAutomatedLiveTestAsync(CallAutomationRecordedTestCaseAsync):

    @recorded_by_proxy_async
    async def test_create_VOIP_call_and_answer_then_hangup(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_add_participant_then_cancel_request_async(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id((await self.identity_client.create_user()).raw_id)
        call_connection_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = self.check_for_event("CallConnected", call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event(
            "ParticipantsUpdated", call_connection_id, timedelta(seconds=15)
        )

        assert connected_event is not None, "Caller CallConnected event is None"
        assert participant_updated_event is not None, "Caller ParticipantsUpdated event is None"

        add_participant_result = await call_connection.add_participant(participant_to_add)
        await asyncio.sleep(3)
        await call_connection.cancel_add_participant_operation(add_participant_result.invitation_id)

        cancel_add_participant_succeeded_event = self.check_for_event(
            "CancelAddParticipantSucceeded", call_connection_id, timedelta(seconds=15)
        )

        assert cancel_add_participant_succeeded_event is not None, "Caller CancelAddParticipantSucceeded event is None"

        await self.terminate_call(call_connection_id)

    @pytest.mark.skip(
        reason="""Playback fails for same event type triggered and test recording code
                       takes the event type has the dictionary it fails to recording call connected event for the connect api"""
    )
    @recorded_by_proxy_async
    async def test_create_VOIP_call_connect_call_hangup_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = (
            await self.establish_callconnection_voip_connect_call(caller, target)
        )

        # check returned events
        connected_event = self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = self.check_for_event(
            "ParticipantsUpdated", call_connection._call_connection_id, timedelta(seconds=15)
        )

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
        connect_call_connected_event = self.check_for_event(
            "CallConnected", connect_call_connection.call_connection_id, timedelta(seconds=20)
        )
        assert connect_call_connected_event is not None, "Caller CallConnected event is None"

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_start_rec_with_call_connection_id_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = (
            await self.establish_callconnection_voip_connect_call(caller, target)
        )

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

        call_connection_properties = await call_connection.get_call_properties()
        call_connection_id = call_connection_properties.call_connection_id

        target_participant = CommunicationUserIdentifier("testId")
        channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)

        # start recording request with call connection id.
        start_recording = await call_automation_client.start_recording(
            call_connection_id=call_connection_id,
            recording_state_callback_url=callback_url,
            channel_affinity=[channel_affinity],
        )
        await asyncio.sleep(5)

        # check for RecordingStateChanged event
        recording_state_changed_event = self.check_for_event(
            "RecordingStateChanged", call_connection_id, timedelta(seconds=30)
        )
        if recording_state_changed_event is None:
            raise ValueError("RecordingStateChanged event is None")

        # stop recording request
        await call_automation_client.stop_recording(recording_id=start_recording.recording_id)
        await asyncio.sleep(3)

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_start_recording_with_server_call_id_async(self):
        # try to establish the call
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _, call_automation_client, callback_url = (
            await self.establish_callconnection_voip_connect_call(caller, target)
        )

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

        call_connection_properties = await call_connection.get_call_properties()
        call_connection_id = call_connection_properties.call_connection_id
        server_call_id = call_connection_properties.server_call_id

        target_participant = CommunicationUserIdentifier("testId")
        channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)

        # start recording request with call connection id.
        start_recording = await call_automation_client.start_recording(
            server_call_id=server_call_id,
            recording_state_callback_url=callback_url,
            channel_affinity=[channel_affinity],
        )
        await asyncio.sleep(5)

        # check for RecordingStateChanged event
        recording_state_changed_event = self.check_for_event(
            "RecordingStateChanged", call_connection_id, timedelta(seconds=30)
        )
        if recording_state_changed_event is None:
            raise ValueError("RecordingStateChanged event is None")

        # stop recording request
        await call_automation_client.stop_recording(recording_id=start_recording.recording_id)
        await asyncio.sleep(3)

        await self.terminate_call(unique_id)
        return
