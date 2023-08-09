# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import sys
from azure.communication.callautomation import (
    CallAutomationClient,
    CallInvite,
    CommunicationUserIdentifier
)

sys.path.append("..")

class CallAutomationCreateCallSample(object):

    connection_string = os.getenv("COMMUNICATION_CONNECTION_STRING")

    def create_call_to_single(self):
        callautomation_client = CallAutomationClient.from_connection_string(self.connection_string)

        # Creating a call
        user = CommunicationUserIdentifier("8:acs:123")
        call_invite = CallInvite(target=user)
        callback_uri = "https://contoso.com/event"

        call_connection_properties = callautomation_client.create_call(call_invite, callback_uri)

        # callconnection id of the call
        print(call_connection_properties.call_connection_id)

if __name__ == '__main__':
    sample = CallAutomationCreateCallSample()
    sample.create_call_to_single()