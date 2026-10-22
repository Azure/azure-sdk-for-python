# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
import pytest
import asyncio
import os
from typing import Dict, Any
from azure.identity.aio import AzureCliCredential
from azure.communication.callautomation import (
    FileSource,
    MediaStreamingOptions,
    MediaStreamingContentType,
    StreamingTransportType,
    MediaStreamingAudioChannelType,
    TranscriptionOptions,
    TextSource,
)
from azure.communication.callautomation._shared.models import identifier_from_raw_id
from azure.communication.callautomation.aio import (
    CallAutomationClient as CallAutomationClientAsync,
    CallConnectionClient as CallConnectionClientAsync,
)
from azure.communication.callautomation._shared.models import CommunicationUserIdentifier, identifier_from_raw_id
from azure.communication.callautomation._models import ChannelAffinity
from azure.communication.identity import CommunicationIdentityClient
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.helpers import get_test_id

from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.servicebus.aio import ServiceBusClient

from callautomation_test_case_async import CallAutomationRecordedTestCaseAsync


class TestMediaAutomatedLiveTestAsync(CallAutomationRecordedTestCaseAsync):

    @recorded_by_proxy_async
    async def test_play_media_in_a_call(self):
        caller = await self.identity_client.create_user()
        print(f"Caller User ID: {caller.raw_id}")
        target = await self.identity_client.create_user()
        print(f"Target User ID: {target.raw_id}")
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)
        print(f"unique_id: {unique_id}")
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

        file_source = FileSource(url=self.file_source_url)
        await call_connection.play_media_to_all(
            play_source=file_source,
        )

        play_completed_event = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        # Do not return anything from this test method

    @pytest.mark.skip(
        reason="Known issues - Bug 3949487: [GA4] [Python] [SDK] [Async] Get Participant fails with authentication error HMAC-SHA256, Bug 4182867: [SDK] Hmac Validation with ':' (GetParticipant) mismatch"
    )
    @recorded_by_proxy_async
    async def test_add_and_mute_participant_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        new_user = await self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id(new_user.raw_id)
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        add_participant_result = await call_connection.add_participant(participant_to_add)
        if add_participant_result is None:
            raise ValueError("Invalid add_participant_result")

        await asyncio.sleep(3)

        mute_participant_result = await call_connection.mute_participant(
            target, operation_context="muting_add_target_participant"
        )
        if mute_participant_result is None:
            raise ValueError("Invalid mute_participant_result")

        await asyncio.sleep(2)
        get_participant_result = await call_connection.get_participant(target)
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_muted is False:
            raise ValueError("Failed to mute participant")

        await self.terminate_call(unique_id)

    @pytest.mark.skip(
        reason="Known issues - Bug 3949487: [GA4] [Python] [SDK] [Async] Get Participant fails with authentication error HMAC-SHA256, Bug 4182867: [SDK] Hmac Validation with ':' (GetParticipant) mismatch"
    )
    @recorded_by_proxy_async
    async def test_add_and_hold_unhold_participant_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id((await self.identity_client.create_user()).raw_id)
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        add_participant_result = await call_connection.add_participant(participant_to_add)
        if add_participant_result is None:
            raise ValueError("Invalid add_participant_result")

        await asyncio.sleep(3)

        await call_connection.hold(target, operation_context="hold_add_target_participant")

        await asyncio.sleep(2)
        get_participant_result = await call_connection.get_participant(target)
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is False:
            raise ValueError("Failed to hold participant")

        await call_connection.unhold(target, operation_context="unhold_add_target_participant")

        await asyncio.sleep(2)
        get_participant_result = await call_connection.get_participant(target)

        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is True:
            raise ValueError("Failed to unhold participant")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_start_stop_media_streaming_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()

        media_streaming_options = MediaStreamingOptions(
            transport_url=self.transport_url,
            transport_type=StreamingTransportType.WEBSOCKET,
            content_type=MediaStreamingContentType.AUDIO,
            audio_channel_type=MediaStreamingAudioChannelType.MIXED,
            start_media_streaming=False,
        )

        unique_id, call_connection, _ = await self.establish_callconnection_voip_with_streaming_options(
            caller, target, media_streaming_options, False
        )

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

        await call_connection.start_media_streaming()

        media_streaming_started = self.check_for_event(
            "MediaStreamingStarted", call_connection._call_connection_id, timedelta(seconds=30)
        )

        if media_streaming_started is None:
            raise ValueError("MediaStreamingStarted event is None")

        await asyncio.sleep(3)

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.media_streaming_subscription is None:
            raise ValueError("call_connection_properties.media_streaming_subscription is None")
        if call_connection_properties.media_streaming_subscription.state != "active":
            raise ValueError("media streaming state is invalid for MediaStreamingStarted event")

        await call_connection.stop_media_streaming()

        media_streaming_stopped = self.check_for_event(
            "MediaStreamingStopped", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if media_streaming_stopped is None:
            raise ValueError("MediaStreamingStopped event is None")

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.media_streaming_subscription is None:
            raise ValueError("call_connection_properties.media_streaming_subscription is None")
        if call_connection_properties.media_streaming_subscription.state != "inactive":
            raise ValueError("media streaming state is invalid for MediaStreamingStopped event")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_start_stop_transcription_in_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()

        transcription_options = TranscriptionOptions(
            transport_url=self.transport_url,
            transport_type=StreamingTransportType.WEBSOCKET,
            locale="en-US",
            start_transcription=False,
        )

        unique_id, call_connection, _ = await self.establish_callconnection_voip_with_streaming_options(
            caller, target, transcription_options, True
        )

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

        await call_connection.start_transcription(locale="en-ca")

        transcription_started = self.check_for_event(
            "TranscriptionStarted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if transcription_started is None:
            raise ValueError("TranscriptionStarted event is None")

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.transcription_subscription is None:
            raise ValueError("call_connection_properties.transcription_subscription is None")
        if call_connection_properties.transcription_subscription.state != "active":
            raise ValueError("transcription subscription state is invalid for TranscriptionStarted event")

        await asyncio.sleep(3)
        await call_connection.update_transcription(locale="en-gb")

        transcription_updated = self.check_for_event(
            "TranscriptionUpdated", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if transcription_updated is None:
            raise ValueError("TranscriptionUpdated event is None")

        await asyncio.sleep(3)

        await call_connection.stop_transcription()

        transcription_stopped = self.check_for_event(
            "TranscriptionStopped", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if transcription_stopped is None:
            raise ValueError("TranscriptionStopped event is None")

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.transcription_subscription is None:
            raise ValueError("call_connection_properties.transcription_subscription is None")
        if call_connection_properties.transcription_subscription.state != "inactive":
            raise ValueError("transcription subscription state is invalid for TranscriptionStopped event")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_multiple_file_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
        ]

        await call_connection.play_media_to_all(play_source=play_multiple_file_source)

        play_completed_event_file_source = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_file_source is None:
            raise ValueError("Play media all PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_multiple_file_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
        ]

        await call_connection.play_media(play_source=play_multiple_file_source, play_to=[target])

        play_completed_event_file_source_to_target = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_file_source_to_target is None:
            raise ValueError("Play media PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_multiple_file_sources_with_opcallbackurl_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
        ]

        random_unique_id = self._unique_key_gen(caller, target)

        await call_connection.play_media_to_all(
            play_source=play_multiple_file_source,
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id)),
        )

        play_completed_event_file_source = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_file_source is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_multiple_file_sources_with_operationcallbackurl_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
        ]

        random_unique_id = self._unique_key_gen(caller, target)

        await call_connection.play_media(
            play_source=play_multiple_file_source,
            play_to=[target],
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id)),
        )

        play_completed_event_file_source_to_target = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_file_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_multiple_text_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(
            caller, target, cognitive_service_enabled=True
        )

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

        play_multiple_text_source = [
            TextSource(text="this is test one", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test two", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test three", voice_name="en-US-NancyNeural"),
        ]

        await call_connection.play_media(play_source=play_multiple_text_source, play_to=[target])

        play_completed_event_text_source_to_target = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_text_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_multiple_text_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(
            caller, target, cognitive_service_enabled=True
        )

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

        play_multiple_text_source = [
            TextSource(text="this is test one", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test two", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test three", voice_name="en-US-NancyNeural"),
        ]

        await call_connection.play_media_to_all(play_source=play_multiple_text_source)

        play_completed_event_text_source = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_text_source is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_combined_file_and_text_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(
            caller, target, cognitive_service_enabled=True
        )

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

        play_multiple_source = [
            FileSource(url=self.file_source_url),
            TextSource(text="this is test.", voice_name="en-US-NancyNeural"),
        ]

        await call_connection.play_media(play_source=play_multiple_source, play_to=[target])

        play_completed_event_multiple_source_to_target = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_multiple_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_combined_file_and_text_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(
            caller, target, cognitive_service_enabled=True
        )

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

        play_multiple_source = [
            FileSource(url=self.file_source_url),
            TextSource(text="this is test.", voice_name="en-US-NancyNeural"),
        ]

        await call_connection.play_media_to_all(play_source=play_multiple_source)

        play_completed_event_multiple_source = self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event_multiple_source is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_with_invalid_file_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        file_prompt = [FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection.play_media_to_all(play_source=file_prompt)

        play_failed_event = self.check_for_event(
            "PlayFailed", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_failed_event is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_with_invalid_and_valid_file_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        file_prompt = [FileSource(url=self.file_source_url), FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection.play_media_to_all(play_source=file_prompt)

        play_failed_event = self.check_for_event(
            "PlayFailed", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_failed_event is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_with_invalid_file_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        file_prompt = [FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection._play_media(play_source=file_prompt, play_to=[target])

        play_failed_event_to_target = self.check_for_event(
            "PlayFailed", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_failed_event_to_target is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @recorded_by_proxy_async
    async def test_play_with_invalid_and_valid_file_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

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

        file_prompt = [FileSource(url=self.file_source_url), FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection._play_media(play_source=file_prompt, play_to=[target])

        play_failed_event_to_target = self.check_for_event(
            "PlayFailed", call_connection._call_connection_id, timedelta(seconds=30)
        )
        print(play_failed_event_to_target)
        if play_failed_event_to_target is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return
