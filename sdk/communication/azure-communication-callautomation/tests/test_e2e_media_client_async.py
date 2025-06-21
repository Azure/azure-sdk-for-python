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
    MediaStreamingTransportType,
    MediaStreamingAudioChannelType,
    TranscriptionOptions,
    TranscriptionTransportType,
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
from devtools_testutils import AzureRecordedTestCase, is_live, recorded_by_proxy
from devtools_testutils.helpers import get_test_id

from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.servicebus.aio import ServiceBusClient

# --- Async Base Test Case ---
import pytest
import asyncio
import os
from typing import Dict, Any
from azure.identity.aio import AzureCliCredential
from azure.communication.callautomation.aio import (
    CallAutomationClient as CallAutomationClientAsync,
    CallConnectionClient as CallConnectionClientAsync,
)
from azure.communication.identity.aio import CommunicationIdentityClient
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.servicebus.aio import ServiceBusClient
from devtools_testutils import AzureRecordedTestCase, is_live

class CallAutomationRecordedTestCaseAsync(AzureRecordedTestCase):
    @classmethod
    #@pytest.mark.asyncio
    def setup_class(cls):
        if is_live():
            cls.connection_str = os.environ.get('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING')
            cls.servicebus_str = os.environ.get('SERVICEBUS_STRING')
            cls.dispatcher_endpoint = os.environ.get('DISPATCHER_ENDPOINT')
            cls.file_source_url = os.environ.get('FILE_SOURCE_URL')
            cls.cognitive_service_endpoint = os.environ.get('COGNITIVE_SERVICE_ENDPOINT')
            cls.transport_url = os.environ.get('TRANSPORT_URL')
        else:
            cls.connection_str = "endpoint=https://someEndpoint/;accesskey=someAccessKeyw=="
            cls.servicebus_str = "redacted.servicebus.windows.net"
            cls.dispatcher_endpoint = "https://REDACTED.azurewebsites.net"
            cls.file_source_url = "https://REDACTED/prompt.wav"
            cls.cognitive_service_endpoint = "https://sanitized/"
            cls.transport_url = "wss://sanitized/ws"

        cls.credential = AzureCliCredential()
        cls.dispatcher_callback = cls.dispatcher_endpoint + "/api/servicebuscallback/events"
        cls.identity_client = CommunicationIdentityClient.from_connection_string(cls.connection_str)
        cls.phonenumber_client = PhoneNumbersClient.from_connection_string(cls.connection_str)
        cls.service_bus_client = ServiceBusClient(
            fully_qualified_namespace=cls.servicebus_str,
            credential=cls.credential
        )
        cls.call_automation_client = CallAutomationClientAsync.from_connection_string(cls.connection_str)
        cls.event_listener = AsyncEventListener()
        cls.wait_for_event_flags = []
        cls.event_store: Dict[str, Dict[str, Any]] = {}
        cls.event_to_save: Dict[str, Dict[str, Any]] = {}
        cls.open_call_connections: Dict[str, CallConnectionClientAsync] = {}

    # --- Async helper methods ---
    
    async def create_user(self):
        return await self.identity_client.create_user()

    async def establish_callconnection_voip(self, caller, target, cognitive_service_enabled=False):
        from azure.communication.callautomation import CreateCallOptions
        create_call_options = CreateCallOptions(
            source=caller,
            targets=[target],
            callback_url=self.dispatcher_callback
        )
        call_response = await self.call_automation_client.create_call(create_call_options)
        call_connection = call_response.call_connection
        unique_id = f"call-{int(asyncio.get_event_loop().time() * 1000)}"
        return unique_id, call_connection, None

    async def establish_callconnection_voip_with_streaming_options(self, caller, target, options, is_transcription):
        call_connection = await self.call_automation_client.create_call_connection(
            source=caller,
            targets=[target],
            callback_url=self.dispatcher_callback,
            media_streaming_options=options if not is_transcription else None,
            transcription_options=options if is_transcription else None
        )
        unique_id = f"call-{int(asyncio.get_event_loop().time() * 1000)}"
        return unique_id, call_connection, None

    async def check_for_event(self, event_type, call_connection_id, timeout):
        deadline = asyncio.get_event_loop().time() + timeout.total_seconds()
        while asyncio.get_event_loop().time() < deadline:
            event = await self.event_listener.get_event(event_type, call_connection_id)
            if event:
                return event
            await asyncio.sleep(1)
        return None

    async def terminate_call(self, unique_id):
        await self.call_automation_client.terminate_call(unique_id)

    def _unique_key_gen(self, caller, target):
        return f"{caller.raw_id}_{target.raw_id}_{int(asyncio.get_event_loop().time())}"

class AsyncEventListener:
    async def get_event(self, event_type, call_connection_id):
        await asyncio.sleep(0.1)
        return None  # Simulate no event
        
class TestMediaAutomatedLiveTestAsync(CallAutomationRecordedTestCaseAsync):

    @pytest.mark.asyncio
    #@recorded_by_proxy
    async def test_play_media_in_a_call(self):
        caller = await self.identity_client.create_user()
        print(f"Caller User ID: {caller.raw_id}")
        target = await self.identity_client.create_user()
        print(f"Target User ID: {target.raw_id}")
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)
        print(f"unique_id: {unique_id}")
        connected_event = await self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
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

        play_completed_event = await self.check_for_event(
            "PlayCompleted", call_connection._call_connection_id, timedelta(seconds=30)
        )
        if play_completed_event is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        # Do not return anything from this test method

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_add_and_mute_participant_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        new_user = await self.identity_client.create_user()  # Await here!
        participant_to_add = identifier_from_raw_id(new_user.raw_id)
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
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

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_add_and_hold_unhold_participant_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id((await self.identity_client.create_user()).raw_id)
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
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

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_start_stop_media_streaming_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()

        media_streaming_options = MediaStreamingOptions(
            transport_url=self.transport_url,
            transport_type=MediaStreamingTransportType.WEBSOCKET,
            content_type=MediaStreamingContentType.AUDIO,
            audio_channel_type=MediaStreamingAudioChannelType.MIXED,
            start_media_streaming=False
        )

        unique_id, call_connection, _ = await self.establish_callconnection_voip_with_streaming_options(
            caller, target, media_streaming_options, False
        )

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        await call_connection.start_media_streaming()

        media_streaming_started = await self.check_for_event('MediaStreamingStarted', call_connection._call_connection_id, timedelta(seconds=30))
        if media_streaming_started is None:
            raise ValueError("MediaStreamingStarted event is None")

        await asyncio.sleep(3)

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.media_streaming_subscription is None:
            raise ValueError("call_connection_properties.media_streaming_subscription is None")
        if call_connection_properties.media_streaming_subscription.state != 'active':
            raise ValueError("media streaming state is invalid for MediaStreamingStarted event")

        await call_connection.stop_media_streaming()

        media_streaming_stopped = await self.check_for_event('MediaStreamingStopped', call_connection._call_connection_id, timedelta(seconds=30))
        if media_streaming_stopped is None:
            raise ValueError("MediaStreamingStopped event is None")

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.media_streaming_subscription is None:
            raise ValueError("call_connection_properties.media_streaming_subscription is None")
        if call_connection_properties.media_streaming_subscription.state != 'inactive':
            raise ValueError("media streaming state is invalid for MediaStreamingStopped event")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_start_stop_transcription_in_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()

        transcription_options = TranscriptionOptions(
            transport_url=self.transport_url,
            transport_type=TranscriptionTransportType.WEBSOCKET,
            locale="en-US",
            start_transcription=False
        )

        unique_id, call_connection, _ = await self.establish_callconnection_voip_with_streaming_options(
            caller, target, transcription_options, True
        )

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        await call_connection.start_transcription(locale="en-ca")

        transcription_started = await self.check_for_event('TranscriptionStarted', call_connection._call_connection_id, timedelta(seconds=30))
        if transcription_started is None:
            raise ValueError("TranscriptionStarted event is None")

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.transcription_subscription is None:
            raise ValueError("call_connection_properties.transcription_subscription is None")
        if call_connection_properties.transcription_subscription.state != 'active':
            raise ValueError("transcription subscription state is invalid for TranscriptionStarted event")

        await asyncio.sleep(3)
        await call_connection.update_transcription(locale="en-gb")

        transcription_updated = await self.check_for_event('TranscriptionUpdated', call_connection._call_connection_id, timedelta(seconds=30))
        if transcription_updated is None:
            raise ValueError("TranscriptionUpdated event is None")

        await asyncio.sleep(3)

        await call_connection.stop_transcription()

        transcription_stopped = await self.check_for_event('TranscriptionStopped', call_connection._call_connection_id, timedelta(seconds=30))
        if transcription_stopped is None:
            raise ValueError("TranscriptionStopped event is None")

        call_connection_properties = await call_connection.get_call_properties()
        if call_connection_properties is None:
            raise ValueError("call_connection_properties is None")
        if call_connection_properties.transcription_subscription is None:
            raise ValueError("call_connection_properties.transcription_subscription is None")
        if call_connection_properties.transcription_subscription.state != 'inactive':
            raise ValueError("transcription subscription state is invalid for TranscriptionStopped event")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_multiple_file_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url)
        ]

        await call_connection.play_media_to_all(
            play_source=play_multiple_file_source
        )

        play_completed_event_file_source = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source is None:
            raise ValueError("Play media all PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_multiple_file_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url)
        ]

        await call_connection.play_media(
            play_source=play_multiple_file_source,
            play_to=[target]
        )

        play_completed_event_file_source_to_target = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source_to_target is None:
            raise ValueError("Play media PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_multiple_file_sources_with_operationcallbackurl_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url)
        ]

        random_unique_id = self._unique_key_gen(caller, target)

        await call_connection.play_media_to_all(
            play_source=play_multiple_file_source,
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id))
        )

        play_completed_event_file_source = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_multiple_file_sources_with_operationcallbackurl_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url)
        ]

        random_unique_id = self._unique_key_gen(caller, target)

        await call_connection.play_media(
            play_source=play_multiple_file_source,
            play_to=[target],
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id))
        )

        play_completed_event_file_source_to_target = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_multiple_text_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_text_source = [
            TextSource(text="this is test one", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test two", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test three", voice_name="en-US-NancyNeural")
        ]

        await call_connection.play_media(
            play_source=play_multiple_text_source,
            play_to=[target]
        )

        play_completed_event_text_source_to_target = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_text_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_multiple_text_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_text_source = [
            TextSource(text="this is test one", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test two", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test three", voice_name="en-US-NancyNeural")
        ]

        await call_connection.play_media_to_all(
            play_source=play_multiple_text_source
        )

        play_completed_event_text_source = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_text_source is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_combined_file_and_text_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_source = [
            FileSource(url=self.file_source_url),
            TextSource(text="this is test.", voice_name="en-US-NancyNeural"),
        ]

        await call_connection.play_media(
            play_source=play_multiple_source,
            play_to=[target]
        )

        play_completed_event_multiple_source_to_target = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_multiple_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_combined_file_and_text_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        play_multiple_source = [
            FileSource(url=self.file_source_url),
            TextSource(text="this is test.", voice_name="en-US-NancyNeural"),
        ]

        await call_connection.play_media_to_all(
            play_source=play_multiple_source
        )

        play_completed_event_multiple_source = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_multiple_source is None:
            raise ValueError("PlayCompleted event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_with_invalid_file_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        file_prompt = [FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection.play_media_to_all(
            play_source=file_prompt
        )

        play_failed_event = await self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        if play_failed_event is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_with_invalid_and_valid_file_sources_with_play_media_all(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        file_prompt = [FileSource(url=self.file_source_url), FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection.play_media_to_all(
            play_source=file_prompt
        )

        play_failed_event = await self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        if play_failed_event is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_with_invalid_file_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        file_prompt = [FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection._play_media(
            play_source=file_prompt,
            play_to=[target]
        )

        play_failed_event_to_target = await self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        if play_failed_event_to_target is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_with_invalid_and_valid_file_sources_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        file_prompt = [FileSource(url=self.file_source_url), FileSource(url="https://dummy.com/dummyurl.wav")]

        await call_connection._play_media(
            play_source=file_prompt,
            play_to=[target]
        )

        play_failed_event_to_target = await self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        print(play_failed_event_to_target)
        if play_failed_event_to_target is None:
            raise ValueError("PlayFailed event is None")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_interrupt_audio_and_announce_in_a_call(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event(
            "CallConnected", call_connection._call_connection_id, timedelta(seconds=15)
        )
        participant_updated_event = await self.check_for_event(
            "ParticipantsUpdated", call_connection._call_connection_id, timedelta(seconds=15)
        )

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        play_source = FileSource(url=self.file_source_url)

        await call_connection.hold(target_participant=target, play_source=play_source, operation_context="hold_add_target_participant")
        await asyncio.sleep(2)
        hold_audio_started_event = await self.check_for_event(
            "HoldAudioStarted", call_connection._call_connection_id, timedelta(seconds=15)
        )
        if hold_audio_started_event is None:
            raise ValueError("Caller HoldAudioStarted event is None")

        get_participant_result = await call_connection.get_participant(target)
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is False:
            raise ValueError("Failed to hold participant")
        play_multiple_file_source = [
            FileSource(url=self.file_source_url)
        ]
        await call_connection.interrupt_audio_and_announce(target_participant=target, play_sources=play_multiple_file_source)

        hold_audio_paused_event = await self.check_for_event(
            "HoldAudioPaused", call_connection._call_connection_id, timedelta(seconds=15)
        )
        if hold_audio_paused_event is None:
            raise ValueError("Caller HoldAudioPaused event is None")

        hold_audio_resumed_event = await self.check_for_event(
            "HoldAudioResumed", call_connection._call_connection_id, timedelta(seconds=15)
        )
        if hold_audio_resumed_event is None:
            raise ValueError("Caller HoldAudioResumed event is None")

        await call_connection.unhold(target, operation_context="unhold_add_target_participant")
        await asyncio.sleep(2)
        hold_audio_completed_event = await self.check_for_event(
            "HoldAudioCompleted", call_connection._call_connection_id, timedelta(seconds=15)
        )
        if hold_audio_completed_event is None:
            raise ValueError("Caller HoldAudioCompleted event is None")

        get_participant_result = await call_connection.get_participant(target)

        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is True:
            raise ValueError("Failed to unhold participant")

        await self.terminate_call(unique_id)
        return

    @pytest.mark.asyncio
    @recorded_by_proxy
    async def test_play_file_source_with_interrupt_hold_audio_with_play_media(self):
        caller = await self.identity_client.create_user()
        target = await self.identity_client.create_user()
        unique_id, call_connection, _ = await self.establish_callconnection_voip(caller, target)

        connected_event = await self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = await self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        random_unique_id = self._unique_key_gen(caller, target)

        play_hold_source = FileSource(url=self.file_source_url)

        await call_connection.hold(target, play_source=play_hold_source,
                                  operation_context="hold_add_target_participant",
                                  operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id)))

        await asyncio.sleep(2)
        hold_audio_event = await self.check_for_event('HoldAudioStarted', call_connection._call_connection_id, timedelta(seconds=30))
        if hold_audio_event is None:
            raise ValueError("HoldAudioStarted event is None")

        get_participant_result = await call_connection.get_participant(target)
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is False:
            raise ValueError("Failed to hold participant")

        play_file_source = FileSource(url=self.file_source_url)

        await call_connection.play_media(
            play_source=play_file_source,
            play_to=[target],
            interrupt_hold_audio=True,
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id))
        )

        hold_audio_paused_event = await self.check_for_event('HoldAudioPaused', call_connection._call_connection_id, timedelta(seconds=30))
        if hold_audio_paused_event is None:
            raise ValueError("HoldAudioPaused event is None")

        play_started_event = await self.check_for_event('PlayStarted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_started_event is None:
            raise ValueError("PlayStarted event is None")

        play_completed_event_file_source_to_target = await self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source_to_target is None:
            raise ValueError("PlayCompleted event is None")

        hold_audio_resume_event = await self.check_for_event('HoldAudioResumed', call_connection._call_connection_id, timedelta(seconds=30))
        if hold_audio_resume_event is None:
            raise ValueError("HoldAudioResumed event is None")

        await call_connection.unhold(target, operation_context="unhold_add_target_participant")

        await asyncio.sleep(2)
        hold_audio_completed_event = await self.check_for_event('HoldAudioCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if hold_audio_completed_event is None:
            raise ValueError("HoldAudioCompleted event is None")

        get_participant_result = await call_connection.get_participant(target)

        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is True:
            raise ValueError("Failed to unhold participant")

        await self.terminate_call(unique_id)
        return