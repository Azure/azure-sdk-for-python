# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import inspect
from datetime import timedelta

from azure.communication.callautomation import CallAutomationClient, CallConnectionClient, CallInvite, FileSource,\
    DtmfTone, PhoneNumberIdentifier
from azure.communication.callautomation._shared.utils import parse_connection_str
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.phonenumbers import PhoneNumbersClient

from _shared.asynctestcase import AsyncCommunicationTestCase
from call_automation_automated_live_test_base import CallAutomationAutomatedLiveTestBase

play_source_uri = 'https://acstestapp1.azurewebsites.net/audio/bot-hold-music-1.wav'

class CallMediaClientAsyncAutomatedLiveTest(CallAutomationAutomatedLiveTestBase):
    def setUp(self):
        super(CallMediaClientAsyncAutomatedLiveTest, self).setUp()
        self.connection_str = os.environ.get('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING', 'endpoint=https://sanitized.communication.azure.com/;accesskey=REDACTED')
        self.identity_client = CommunicationIdentityClient.from_connection_string(self.connection_str)
        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint
        self.test_name = ''
    
    def tearDown(self):
        super(CallMediaClientAsyncAutomatedLiveTest, self).tearDown()
        self.persist_events(self.test_name)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_play_media_in_a_call(self):
        self.test_name = inspect.currentframe().f_code.co_name
        self.load_persisted_events(self.test_name)
        call_connection_list = []
        print("starting test")
        try:
            # create caller and receiver
            print('TEST SCENARIO: _create_VOIP_call_and_answer_then_hangup')
            caller = self.identity_client.create_user()
            target = self.identity_client.create_user()
            call_automation_client_caller = CallAutomationClient.from_connection_string(self.connection_str, source_identity=caller) # for creating call
            call_automation_client_target = CallAutomationClient.from_connection_string(self.connection_str, source_identity=target) # answering call, all other actions
            unique_id = self.service_bus_with_new_call(caller, target)

            # create a call
            call_invite = CallInvite(target=target)
            create_call_result = call_automation_client_caller.create_call(target_participant=call_invite, callback_url=(self.dispatcher_callback + "?q={}".format(unique_id)))
            if create_call_result is None:
                raise ValueError("Invalid create_call result")

            caller_connection_id = create_call_result.call_connection_id
            if caller_connection_id is None:
                raise ValueError("Caller connection ID is None")
            print('Caller connection ID: ' + caller_connection_id)

            # wait for incomingCallContext
            self.wait_for_messages(unique_id, timedelta(seconds=30))
            incoming_call_context = self.incoming_call_context_store[unique_id]
            if incoming_call_context is None:
                raise ValueError("Incoming call context is None")

            # answer the call
            answer_call_result = call_automation_client_target.answer_call(incoming_call_context=incoming_call_context, callback_url=self.dispatcher_callback)
            if answer_call_result is None:
                raise ValueError("Invalid answer_call result")

            receiver_connection_id = answer_call_result.call_connection_id
            print('Receiver connection ID: ' + receiver_connection_id)
            receiver_call_connection = CallConnectionClient.from_connection_string(self.connection_str, answer_call_result.call_connection_id)
            call_connection_list.append(receiver_call_connection)

            # check events to caller side
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            caller_connected_event = self.check_for_event(event_type='CallConnected', call_connection_id=caller_connection_id)
            caller_participant_updated_event = self.check_for_event(event_type='ParticipantsUpdated', call_connection_id=caller_connection_id)
            if caller_connected_event is None:
                raise ValueError("Caller CallConnected event is None")
            if caller_participant_updated_event is None:
                raise ValueError("Caller ParticipantsUpdated event is None")
            

            # check events to receiver side
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            receiver_connected_event = self.check_for_event(event_type='CallConnected', call_connection_id=caller_connection_id)
            receiver_participant_updated_event = self.check_for_event(event_type='ParticipantsUpdated', call_connection_id=caller_connection_id)
            if receiver_connected_event is None:
                raise ValueError("Receiver CallConnected event is None")
            if receiver_participant_updated_event is None:
                raise ValueError("Receiver ParticipantsUpdated event is None")

            # play media to all participants
            caller_call_connection = CallConnectionClient.from_connection_string(self.connection_str, create_call_result.call_connection_id)
            file_source = FileSource(url=play_source_uri)

            caller_call_connection.play_media_to_all(
                play_source=file_source,
            )

            # check for PlayCompleted event
            self.wait_for_messages(unique_id, timedelta(seconds=20))
            play_completed_event = self.check_for_event(event_type='PlayCompleted', call_connection_id=caller_connection_id)
            if play_completed_event is None:
                raise ValueError("PlayCompleted event is None")
            
            # hang up the call
            receiver_call_connection.hang_up(is_for_everyone=True)
            self.wait_for_messages(unique_id, timedelta(seconds=8))

            # check if call terminated
            receiver_call_disconnected_event = self.check_for_event(event_type='CallDisconnected', call_connection_id=caller_connection_id)
            if receiver_call_disconnected_event is None:
                raise ValueError("Receiver CallDisconnected event is None")
            
            call_connection_list.clear()

        except Exception as e:
             print(f"Threw Exception: {e}")
             raise
        finally:
            # hang up the call
            for cc in call_connection_list:
                cc.hang_up(is_for_everyone=True)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_dtmf_actions_in_a_call(self):
        self.test_name = inspect.currentframe().f_code.co_name
        self.load_persisted_events(self.test_name)
        call_connection_list = []
        print("starting test")
        try:
            print('TEST SCENARIO: _create_VOIP_call_and_trigger_dtmf_actions_then_hangup')

            # Get purchased PSTN numbers and create caller and receiver
            phone_numbers_client = PhoneNumbersClient.from_connection_string(self.connection_str)
            purchased_numbers = list(phone_numbers_client.list_purchased_phone_numbers())
            if len(purchased_numbers) >= 2:
                caller_phone = PhoneNumberIdentifier(purchased_numbers[0].phone_number)
                target_phone = PhoneNumberIdentifier(purchased_numbers[1].phone_number)
            else:
                raise ValueError("Invalid PSTN setup, test needs at least 2 phone numbers")

            call_automation_client_caller = CallAutomationClient.from_connection_string(
                self.connection_str)  # for creating call
            call_automation_client_target = CallAutomationClient.from_connection_string(
                self.connection_str)  # answering call, all other actions
            unique_id = self.service_bus_with_new_call(caller_phone, target_phone)
            self.clean_old_messages(unique_id)
            callback_url = self.dispatcher_callback + "?q={}".format(unique_id)

            # create a call
            call_invite = CallInvite(target=target_phone, source_caller_id_number=caller_phone)
            create_call_result = call_automation_client_caller.create_call(target_participant=call_invite,
                                                                           callback_url=callback_url)
            if create_call_result is None:
                raise ValueError("Invalid create_call result")

            caller_connection_id = create_call_result.call_connection_id
            if caller_connection_id is None:
                raise ValueError("Caller connection ID is None")
            print('Caller connection ID: ' + caller_connection_id)

            # wait for incomingCallContext
            self.wait_for_messages(unique_id, timedelta(seconds=30))
            incoming_call_context = self.incoming_call_context_store[unique_id]
            if incoming_call_context is None:
                raise ValueError("Incoming call context is None")

            # answer the call
            answer_call_result = call_automation_client_target.answer_call(incoming_call_context=incoming_call_context,
                                                                           callback_url=callback_url)
            if answer_call_result is None:
                raise ValueError("Invalid answer_call result")

            receiver_connection_id = answer_call_result.call_connection_id
            print('Receiver connection ID: ' + receiver_connection_id)
            receiver_call_connection = CallConnectionClient.from_connection_string(self.connection_str,
                                                                                   answer_call_result.call_connection_id)
            call_connection_list.append(receiver_call_connection)

            # check events to caller side
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            caller_connected_event = self.check_for_event(event_type='CallConnected',
                                                          call_connection_id=caller_connection_id)
            if caller_connected_event is None:
                raise ValueError("Caller CallConnected event is None")

            # check events to receiver side
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            receiver_connected_event = self.check_for_event(event_type='CallConnected',
                                                            call_connection_id=receiver_connection_id)
            if receiver_connected_event is None:
                raise ValueError("Receiver CallConnected event is None")

            # start continuous DTMF recognition
            caller_call_connection = CallConnectionClient.from_connection_string(self.connection_str,
                                                                                 caller_connection_id)
            caller_call_connection.start_continuous_dtmf_recognition(target_participant=target_phone)

            # send DTMF tones
            caller_call_connection.send_dtmf(tones=[DtmfTone.POUND], target_participant=target_phone)
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            send_dtmf_completed_event = self.check_for_event(event_type='SendDtmfCompleted',
                                                             call_connection_id=caller_connection_id)
            if send_dtmf_completed_event is None:
                raise ValueError("SendDtmfCompleted event is None")

            # check DTMF tone received events to receiver
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            continuous_dtmf_recognition_tone_received_event = self.check_for_event(
                event_type='ContinuousDtmfRecognitionToneReceived',
                call_connection_id=receiver_connection_id)
            if continuous_dtmf_recognition_tone_received_event is None:
                raise ValueError("ContinuousDtmfRecognitionToneReceived event is None")

            # stop continuous DTMF recognition
            caller_call_connection.stop_continuous_dtmf_recognition(target_participant=target_phone)
            self.wait_for_messages(unique_id, timedelta(seconds=8))
            continuous_dtmf_recognition_stopped_event = self.check_for_event(
                event_type='ContinuousDtmfRecognitionStopped',
                call_connection_id=caller_connection_id)
            if continuous_dtmf_recognition_stopped_event is None:
                raise ValueError("ContinuousDtmfRecognitionStopped event is None")

            # hang up the calls
            receiver_call_connection.hang_up(is_for_everyone=True)
            self.wait_for_messages(unique_id, timedelta(seconds=10))

            # check if call terminated
            receiver_call_disconnected_event = self.check_for_event(event_type='CallDisconnected',
                                                                    call_connection_id=receiver_connection_id)
            if receiver_call_disconnected_event is None:
                raise ValueError("Receiver CallDisconnected event is None")
            call_connection_list.clear()

        except Exception as e:
            print(f"Threw Exception: {e}")
            raise
        finally:
            # hang up the call
            for cc in call_connection_list:
                cc.hang_up(is_for_everyone=True)
