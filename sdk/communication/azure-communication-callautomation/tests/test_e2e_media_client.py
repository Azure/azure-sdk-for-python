# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
import pytest
import time
import unittest

from devtools_testutils import recorded_by_proxy
from azure.communication.callautomation import (
    FileSource,
    DtmfTone,
    PhoneNumberIdentifier,
    TextSource,
    RecognizeInputType,
    RecognitionChoice
)
from callautomation_test_case import CallAutomationRecordedTestCase
from azure.communication.callautomation._shared.models import identifier_from_raw_id

class TestMediaAutomatedLiveTest(CallAutomationRecordedTestCase):

    @recorded_by_proxy
    def test_play_media_in_a_call(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        # play media to all participants
        file_source = FileSource(url=self.file_source_url)
        call_connection.play_media_to_all(
            play_source=file_source,
        )

        # check for PlayCompleted event
        play_completed_event = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event is None:
            raise ValueError("PlayCompleted event is None")

        self.terminate_call(unique_id)
        return

    # NOTE: Commented out by ericasp in March 2024.  This test is incompatible with version updates to phone number client versions
    # @recorded_by_proxy
    # def test_dtmf_actions_in_a_call(self):
    #     # try to establish the call
    #     purchased_numbers = list(self.phonenumber_client.list_purchased_phone_numbers())
    #     if len(purchased_numbers) >= 2:
    #         caller = PhoneNumberIdentifier(purchased_numbers[0].phone_number)
    #         target = PhoneNumberIdentifier(purchased_numbers[1].phone_number)
    #     else:
    #         raise ValueError("Invalid PSTN setup, test needs at least 2 phone numbers")

    #     unique_id, call_connection, _ = self.establish_callconnection_pstn(caller, target)

    #     # check returned events
    #     connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
    #     participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

    #     if connected_event is None:
    #         raise ValueError("Caller CallConnected event is None")
    #     if participant_updated_event is None:
    #         raise ValueError("Caller ParticipantsUpdated event is None")

    #     call_connection.start_continuous_dtmf_recognition(target_participant=target)

    #     # send DTMF tones
    #     call_connection.send_dtmf_tones(tones=[DtmfTone.POUND], target_participant=target)
    #     send_dtmf_completed_event = self.check_for_event('SendDtmfTonesCompleted', call_connection._call_connection_id, timedelta(seconds=15),)
    #     if send_dtmf_completed_event is None:
    #         raise ValueError("SendDtmfTonesCompleted event is None")

    #     # stop continuous DTMF recognition
    #     call_connection.stop_continuous_dtmf_recognition(target_participant=target)
    #     continuous_dtmf_recognition_stopped_event = self.check_for_event('ContinuousDtmfRecognitionStopped', call_connection._call_connection_id, timedelta(seconds=15))
    #     if continuous_dtmf_recognition_stopped_event is None:
    #         raise ValueError("ContinuousDtmfRecognitionStopped event is None")

    #     self.terminate_call(unique_id)
    #     return

    @recorded_by_proxy    
    def test_add_and_mute_participant_in_a_call(self):

        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id(self.identity_client.create_user().raw_id)
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        #Add dummy participant
        add_participant_result = call_connection.add_participant(participant_to_add)
        if add_participant_result is None:
            raise ValueError("Invalid add_participant_result")

        time.sleep(3)

        # Mute participant
        mute_participant_result = call_connection.mute_participant(target, operation_context="muting_add_target_participant")
        if mute_participant_result is None:
            raise ValueError("Invalid mute_participant_result")

        time.sleep(2)
        get_participant_result = call_connection.get_participant(target)
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_muted is False:
            raise ValueError("Failed to mute participant")

        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy    
    def test_add_and_hold_unhold_participant_in_a_call(self):

        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        participant_to_add = identifier_from_raw_id(self.identity_client.create_user().raw_id)
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        #Add dummy participant
        add_participant_result = call_connection.add_participant(participant_to_add)
        if add_participant_result is None:
            raise ValueError("Invalid add_participant_result")

        time.sleep(3)

        # Hold participant
        call_connection.hold(target, operation_context="hold_add_target_participant")

        time.sleep(2)
        get_participant_result = call_connection.get_participant(target)
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is False:
            raise ValueError("Failed to hold participant")

        # Unhold participant
        call_connection.unhold(target, operation_context="unhold_add_target_participant")

        time.sleep(2)
        get_participant_result = call_connection.get_participant(target)
        
        if get_participant_result is None:
            raise ValueError("Invalid get_participant_result")

        if get_participant_result.is_on_hold is True:
            raise ValueError("Failed to unhold participant")
        
        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_play_multiple_file_sources_with_play_media_all(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url)
        ]

        # play media to all 
        call_connection.play_media_to_all(
            play_source=play_multiple_file_source
        )

        # check for PlayCompleted event
        play_completed_event_file_source = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source is None:
            raise ValueError("Play media all PlayCompleted event is None")

        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_play_multiple_file_sources_with_play_media(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        play_multiple_file_source = [
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url),
            FileSource(url=self.file_source_url)
        ]

        # play media
        call_connection.play_media(
            play_source=play_multiple_file_source,
            play_to=[target]
        )

        # check for PlayCompleted event
        play_completed_event_file_source_to_target = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source_to_target is None:
            raise ValueError("Play media PlayCompleted event is None")
        
        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_multiple_file_sources_with_operationcallbackurl_with_play_media_all(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

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

        # play media to all 
        call_connection.play_media_to_all(
            play_source=play_multiple_file_source,
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id))
        )

        # check for PlayCompleted event
        play_completed_event_file_source = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source is None:
            raise ValueError("PlayCompleted event is None")
        
        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_multiple_file_sources_with_operationcallbackurl_with_play_media(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

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

        # play media
        call_connection.play_media(
            play_source=play_multiple_file_source,
            play_to=[target],
            operation_callback_url=(self.dispatcher_callback + "?q={}".format(random_unique_id))
        )

        # check for PlayCompleted event
        play_completed_event_file_source_to_target = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_file_source_to_target is None:
            raise ValueError("PlayCompleted event is None")
        
        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_play_multiple_text_sources_with_play_media(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        play_multiple_text_source = [
            TextSource(text="this is test one", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test two", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test three", voice_name="en-US-NancyNeural")
        ]

        call_connection.play_media(
            play_source=play_multiple_text_source,
            play_to=[target]
        )

        # check for PlayCompleted event
        play_completed_event_text_source_to_target = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_text_source_to_target is None:
            raise ValueError("PlayCompleted event is None")
        
        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_multiple_text_sources_with_play_media_all(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        play_multiple_text_source = [
            TextSource(text="this is test one", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test two", voice_name="en-US-NancyNeural"),
            TextSource(text="this is test three", voice_name="en-US-NancyNeural")
        ]

        call_connection.play_media_to_all(
            play_source=play_multiple_text_source
        )

        # check for PlayCompleted event
        play_completed_event_text_source = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_text_source is None:
            raise ValueError("PlayCompleted event is None")
        
        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_combined_file_and_text_sources_with_play_media(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        play_multiple_source = [
            FileSource(url=self.file_source_url),
            TextSource(text="this is test.", voice_name="en-US-NancyNeural"),
        ]

        call_connection.play_media(
            play_source=play_multiple_source,
            play_to=[target]
        )

         # check for PlayCompleted event
        play_completed_event_multiple_source_to_target = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_multiple_source_to_target is None:
            raise ValueError("PlayCompleted event is None")
        
        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_combined_file_and_text_sources_with_play_media_all(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target, cognitive_service_enabled=True)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        play_multiple_source = [
            FileSource(url=self.file_source_url),
            TextSource(text="this is test.", voice_name="en-US-NancyNeural"),
        ]

        call_connection.play_media_to_all(
            play_source=play_multiple_source
        )

        # check for PlayCompleted event
        play_completed_event_multiple_source = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event_multiple_source is None:
            raise ValueError("PlayCompleted event is None")

        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_with_invalid_file_sources_with_play_media_all(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        file_prompt = [FileSource(url="https://contosoapp.com/abc.wav")]

        call_connection.play_media_to_all(
            play_source=file_prompt
        )

        play_failed_event = self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        if play_failed_event is None:
            raise ValueError("PlayFailed event is None")
        
        self.terminate_call(unique_id)
        return
    
    @recorded_by_proxy
    def test_play_with_invalid_and_valid_file_sources_with_play_media_all(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        file_prompt = [FileSource(url=self.file_source_url), FileSource(url="https://contosoapp.com/abc.wav")]

        call_connection.play_media_to_all(
            play_source=file_prompt
        )

        play_failed_event = self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        if play_failed_event is None:
            raise ValueError("PlayFailed event is None")
        
        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_play_with_invalid_file_sources_with_play_media(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        file_prompt = [FileSource(url="https://contosoapp.com/abc.wav")]

        call_connection._play_media(
            play_source=file_prompt,
            play_to=[target]
        )

        play_failed_event_to_target = self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        if play_failed_event_to_target is None:
            raise ValueError("PlayFailed event is None")
        
        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_play_with_invalid_and_valid_file_sources_with_play_media(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")
        
        file_prompt = [FileSource(url=self.file_source_url), FileSource(url="https://contosoapp.com/abc.wav")]

        call_connection._play_media(
            play_source=file_prompt,
            play_to=[target]
        )

        play_failed_event_to_target = self.check_for_event('PlayFailed', call_connection._call_connection_id, timedelta(seconds=30))
        print(play_failed_event_to_target)
        if play_failed_event_to_target is None:
            raise ValueError("PlayFailed event is None")
        
        self.terminate_call(unique_id)
        return