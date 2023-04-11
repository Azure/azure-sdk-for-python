import os
import pytest
from datetime import timedelta

from azure.communication.callautomation import CallAutomationClient, CallInvite, CallConnected, ParticipantsUpdated, CallDisconnected, PlayCompleted, FileSource
from azure.communication.callautomation._shared.utils import parse_connection_str
from azure.communication.identity import CommunicationIdentityClient

from _shared.asynctestcase import AsyncCommunicationTestCase
from call_automation_automated_live_test_base import CallAutomationAutomatedLiveTestBase

play_source_uri = 'https://acstestapp1.azurewebsites.net/audio/bot-hold-music-1.wav'

class CallMediaClientAsyncAutomatedLiveTest(CallAutomationAutomatedLiveTestBase):
    def setUp(self):
        super(CallMediaClientAsyncAutomatedLiveTest, self).setUp()
        self.connection_str = os.environ.get('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING', 'endpoint=https://REDACTED.communication.azure.com/;accesskey=QWNjZXNzS2V5')
        self.identity_client = CommunicationIdentityClient.from_connection_string(self.connection_str)
        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint
    
    def tearDown(self):
        super(CallMediaClientAsyncAutomatedLiveTest, self).tearDown()

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_play_media_in_a_call(self):
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
            create_call_result = call_automation_client_caller.create_call(target=call_invite, callback_uri=(self.dispatcher_callback + "?q={}".format(unique_id)))
            if create_call_result is None or create_call_result.call_connection_properties is None:
                raise ValueError("Invalid create_call_result")

            caller_connection_id = create_call_result.call_connection_properties.call_connection_id
            if caller_connection_id is None:
                raise ValueError("Caller connection ID is None")
            print('Caller connection ID: ' + caller_connection_id)

            # wait for incomingCallContext
            self.wait_for_messages(unique_id, timedelta(seconds=30))
            incoming_call_context = self.incoming_call_context_store[unique_id]
            if incoming_call_context is None:
                raise ValueError("Incoming call context is None")

            # answer the call
            answer_call_result = call_automation_client_target.answer_call(incoming_call_context=incoming_call_context, callback_uri=self.dispatcher_callback)
            if answer_call_result is None or answer_call_result.call_connection is None or answer_call_result.call_connection_properties is None:
                raise ValueError("Invalid answer_call_result")

            receiver_connection_id = answer_call_result.call_connection_properties.call_connection_id
            print('Receiver connection ID: ' + receiver_connection_id)
            call_connection_list.append(answer_call_result.call_connection)

            # check events to caller side
            self.wait_for_messages(unique_id, timedelta(seconds=3))
            caller_connected_event = self.check_for_event(event_type=CallConnected, call_connection_id=caller_connection_id)
            caller_participant_updated_event = self.check_for_event(event_type=ParticipantsUpdated, call_connection_id=caller_connection_id)
            if caller_connected_event is None:
                raise ValueError("Caller CallConnected event is None")
            if caller_participant_updated_event is None:
                raise ValueError("Caller ParticipantsUpdated event is None")
            

            # check events to receiver side
            self.wait_for_messages(unique_id, timedelta(seconds=3))
            receiver_connected_event = self.check_for_event(event_type=CallConnected, call_connection_id=caller_connection_id)
            receiver_participant_updated_event = self.check_for_event(event_type=ParticipantsUpdated, call_connection_id=caller_connection_id)
            if receiver_connected_event is None:
                raise ValueError("Receiver CallConnected event is None")
            if receiver_participant_updated_event is None:
                raise ValueError("Receiver ParticipantsUpdated event is None")

            # play media to all participants
            call_media_client = create_call_result.call_connection.get_call_media()
            file_source = FileSource(uri=play_source_uri)

            call_media_client.play_to_all(
                play_source=file_source,
            )

            # check for PlayCompleted event
            self.wait_for_messages(unique_id, timedelta(seconds=20))
            play_completed_event = self.check_for_event(event_type=PlayCompleted, call_connection_id=caller_connection_id)
            if play_completed_event is None:
                raise ValueError("PlayCompleted event is None")
            
            # hang up the call
            answer_call_result.call_connection.hang_up(is_for_everyone=True)
            self.wait_for_messages(unique_id, timedelta(seconds=10))

            # check if call terminated
            receiver_call_disconnected_event = self.check_for_event(event_type=CallDisconnected, call_connection_id=caller_connection_id)
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