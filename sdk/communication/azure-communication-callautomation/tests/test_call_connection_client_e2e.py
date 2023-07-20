# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import inspect
from datetime import timedelta

from azure.communication.callautomation import CallAutomationClient, CallConnectionClient, CallInvite
from azure.communication.callautomation._shared.utils import parse_connection_str
from azure.communication.identity import CommunicationIdentityClient

from _shared.asynctestcase import AsyncCommunicationTestCase
from call_automation_automated_live_test_base import CallAutomationAutomatedLiveTestBase


class CallConnectionClientAsyncAutomatedLiveTest(CallAutomationAutomatedLiveTestBase):
    def setUp(self):
        super(CallConnectionClientAsyncAutomatedLiveTest, self).setUp()
        self.connection_str = os.environ.get('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING', 'endpoint=https://sanitized.communication.azure.com/;accesskey=QWNjZXNzS2V5')
        self.identity_client = CommunicationIdentityClient.from_connection_string(self.connection_str)
        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint
        self.test_name = ''
    
    def tearDown(self):
        super(CallConnectionClientAsyncAutomatedLiveTest, self).tearDown()
        self.persist_events(self.test_name)

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def test_add_and_mute_participant_in_a_call(self):
        call_connection_list = []
        self.test_name = inspect.currentframe().f_code.co_name
        self.load_persisted_events(self.test_name)
        print("starting test")
        try:
            # create caller and receiver
            print('TEST SCENARIO: _create_VOIP_call_and_add_and_mute_participant_then_hangup')
            caller = self.identity_client.create_user()
            target_1 = self.identity_client.create_user()
            target_2 = self.identity_client.create_user()
            call_automation_client_caller = CallAutomationClient.from_connection_string(self.connection_str, source=caller) # for creating call
            call_automation_client_target_1 = CallAutomationClient.from_connection_string(self.connection_str, source=target_1) # answering call, all other actions
            call_automation_client_target_2 = CallAutomationClient.from_connection_string(self.connection_str, source=target_2)  # answering call, all other actions

            unique_id_1 = self.service_bus_with_new_call(caller, target_1)
            callback_url_1 = self.dispatcher_callback + "?q={}".format(unique_id_1)

            # create a call
            call_invite_1 = CallInvite(target=target_1)
            create_call_result = call_automation_client_caller.create_call(target_participant=call_invite_1,
                                                                           callback_url=callback_url_1)
            if create_call_result is None:
                raise ValueError("Invalid create_call_result")
            
            caller_connection_id = create_call_result.call_connection_id
            if caller_connection_id is None:
                raise ValueError("Caller connection ID is None")
            print('Caller connection ID: ' + caller_connection_id)

            # wait for incomingCallContext
            self.wait_for_messages(unique_id_1, timedelta(seconds=30))
            incoming_call_context_1 = self.incoming_call_context_store[unique_id_1]
            if incoming_call_context_1 is None:
                raise ValueError("Incoming call context 1 is None")

            # answer the call
            answer_call_result_1 = call_automation_client_target_1.answer_call(incoming_call_context=incoming_call_context_1,
                                                                             callback_url=callback_url_1)
            if answer_call_result_1 is None:
                raise ValueError("Invalid answer_call_result_1")

            receiver_connection_id_1 = answer_call_result_1.call_connection_id
            print('Receiver 1 connection ID: ' + receiver_connection_id_1)

            # check events to caller side
            self.wait_for_messages(unique_id_1, timedelta(seconds=8))
            caller_connected_event = self.check_for_event(event_type='CallConnected', call_connection_id=caller_connection_id)
            caller_participant_updated_event = self.check_for_event(event_type='ParticipantsUpdated', call_connection_id=caller_connection_id)
            if caller_connected_event is None:
                raise ValueError("Caller CallConnected event is None")
            if caller_participant_updated_event is None:
                raise ValueError("Caller ParticipantsUpdated event is None")
            

            # check events to receiver side
            self.wait_for_messages(unique_id_1, timedelta(seconds=8))
            receiver_connected_event = self.check_for_event(event_type='CallConnected', call_connection_id=receiver_connection_id_1)
            receiver_participant_updated_event = self.check_for_event(event_type='ParticipantsUpdated', call_connection_id=receiver_connection_id_1)
            if receiver_connected_event is None:
                raise ValueError("Receiver CallConnected event is None")
            if receiver_participant_updated_event is None:
                raise ValueError("Receiver ParticipantsUpdated event is None")

            unique_id_2 = self.service_bus_with_new_call(caller, target_2)
            callback_url_2 = self.dispatcher_callback + "?q={}".format(unique_id_2)

            # Add participant
            call_invite_2 = CallInvite(target=target_2)

            caller_call_connection = CallConnectionClient.from_connection_string(self.connection_str, caller_connection_id)
            call_connection_list.append(caller_call_connection)
            add_participant_result = caller_call_connection.add_participant(target_participant=call_invite_2)
            if add_participant_result is None:
                raise ValueError("Invalid add_participant_result")

            # wait for incomingCallContext
            self.wait_for_messages(unique_id_2, timedelta(seconds=30))
            incoming_call_context_2 = self.incoming_call_context_store[unique_id_2]
            if incoming_call_context_2 is None:
                raise ValueError("Incoming call context 2 is None")

            # answer the call
            answer_call_result_2 = call_automation_client_target_2.answer_call(incoming_call_context=incoming_call_context_2,
                                                                               callback_url=callback_url_2)
            if answer_call_result_2 is None:
                raise ValueError("Invalid answer_call_2 result")
            receiver_connection_id_2 = answer_call_result_2.call_connection_id
            print('Receiver 2 connection ID: ' + receiver_connection_id_2)

            # check if participant added
            self.wait_for_messages(unique_id_1, timedelta(seconds=8))
            participant_added_event = self.check_for_event(event_type='AddParticipantSucceeded',
                                                           call_connection_id=caller_connection_id)
            if participant_added_event is None:
                raise ValueError("AddParticipantSucceeded event is None")

            # Mute participant
            mute_participant_result = caller_call_connection.mute_participant(target_2)
            if mute_participant_result is None:
                raise ValueError("Invalid mute_participant_result")

            # check if participant muted
            self.wait_for_messages(unique_id_1, timedelta(seconds=8))
            mute_participant_updated_event = self.check_for_event(event_type='ParticipantsUpdated',
                                                                    call_connection_id=caller_connection_id)
            if mute_participant_updated_event is None:
                raise ValueError("Mute related ParticipantsUpdated event is None")

            is_muted = False
            for participant in mute_participant_updated_event['data']['participants']:
                if participant['identifier']['rawId'] == target_2.raw_id:
                    is_muted = participant['isMuted']
                    break

            if is_muted is False:
                raise ValueError("Failed to mute participant")

            # hang up the call
            caller_call_connection.hang_up(is_for_everyone=True)
            self.wait_for_messages(unique_id_1, timedelta(seconds=10))

            # check if call terminated
            receiver_call_disconnected_event = self.check_for_event(event_type='CallDisconnected', call_connection_id=caller_connection_id)
            if receiver_call_disconnected_event is None:
                raise ValueError("Caller CallDisconnected event is None")
            
            call_connection_list.clear()

        except Exception as e:
             print(f"Threw Exception: {e}")
             raise
        finally:
            # hang up the call
            for cc in call_connection_list:
                cc.hang_up(is_for_everyone=True)