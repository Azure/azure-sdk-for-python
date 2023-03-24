import pytest
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.callautomation import CallAutomationClient, CallInvite

class CallAutomationClientTest(AsyncCommunicationTestCase):
    def setUp(self):
        super(CallAutomationClientTest, self).setUp()

        # TODO what other setup needs to happen here??
        self.identity_client = CommunicationIdentityClient.from_connection_string(self.connection_str)

    
    def tearDown(self):
        super(CallAutomationClientTest, self).tearDown()

        # TODO what other tear down needs to happen here??

    @pytest.mark.live_test_only
    @AsyncCommunicationTestCase.await_prepared_test
    async def _create_VOIP_call_and_answer_then_hangup_automated_test(self):
        # TODO implement
        # create caller and receiver
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        call_automation_client = CallAutomationClient.from_connection_string(self.connection_str)
        unique_id = service_bus_with_new_call(caller, target)

        # create a call
        call_invite = CallInvite(target=target)
        call_automation_client.create_call(call_invite=call_invite, callback_uri=(DISPATCHER_CALLBACK + "?q={}".format(unique_id)))
        # wait for incomingCallContext
        # answer the call
        # check events to caller side
        # check events to receiver side
        # hang up the call
        # check if both parties had the call terminated
