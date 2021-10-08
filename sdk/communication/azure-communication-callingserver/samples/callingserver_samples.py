
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: callingserver_samples.py
DESCRIPTION:
    These samples demonstrate create a callingserver client, create a call_connection,
    create a server_call_with_calllocator.
    The CommunicationIdentityClient is authenticated using a connection string.
    The CallingServerClient is authenticated using AzureAD Managed Identity.
USAGE:
    python callingserver_samples.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
    2) COMMUNICATION_SAMPLES_CONNECTION_STRING - Azure Communication Service resource connection string
"""

import os

class CallingServerClientSamples(object):
    from azure.communication.identity import CommunicationIdentityClient
    connection_string = os.environ.get("COMMUNICATION_SAMPLES_CONNECTION_STRING", None)
    if not connection_string:
        raise ValueError("Set COMMUNICATION_SAMPLES_CONNECTION_STRING env before run this sample.")

    identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
    user = identity_client.create_user()

    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _thread_id = None

    def create_callingserver_client(self):
        endpoint = self.endpoint
        # [START create_callingserver_client]
        from azure.communication.callingserver import CallingServerClient
        from azure.identity import DefaultAzureCredential

        # set `endpoint` to an existing ACS endpoint
        calling_server_client = CallingServerClient(endpoint, DefaultAzureCredential())
        # [END create_callingserver_client]

    def create_call_connection(self):
        endpoint = self.endpoint
        from_user = self.user
        # [START create_call_connection]
        from azure.communication.callingserver import PhoneNumberIdentifier, CreateCallOptions, CallMediaType, CallingEventSubscriptionType
        from azure.communication.callingserver import CallingServerClient
        from azure.identity import DefaultAzureCredential
        to_user = PhoneNumberIdentifier("<your-phone-number>")
        options = CreateCallOptions(
            callback_uri="<your-callback-uri>",
            requested_media_types=[CallMediaType.AUDIO],
            requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED, CallingEventSubscriptionType.TONE_RECEIVED]
        )
        # set `endpoint` to an existing ACS endpoint
        calling_server_client = CallingServerClient(endpoint, DefaultAzureCredential())
        call_connection = calling_server_client.create_call_connection(
                    source=from_user,
                    targets=[to_user],
                    options=options,
                    )
        # [END create_call_connection]
        # [START hang_up_call]
        call_connection.hang_up()
        # [END hang_up_call]

    def create_server_call_with_calllocator(self):
        endpoint = self.endpoint
        from_user = self.user
        # [START create_server_call_with_calllocator]
        # set `endpoint` to an existing ACS endpoint
        from azure.communication.callingserver import ServerCallLocator, CommunicationUserIdentifier, CallMediaType, CallingEventSubscriptionType, JoinCallOptions
        from azure.communication.callingserver import CallingServerClient
        from azure.identity import DefaultAzureCredential

        join_options = JoinCallOptions(
            callback_uri="<your-callback-uri>",
            requested_media_types=[CallMediaType.AUDIO],
            requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED]
        )
        # set `endpoint` to an existing ACS endpoint
        calling_server_client = CallingServerClient(endpoint, DefaultAzureCredential())
        server_call_id = "<your-server-call-id>"
        call_locator = ServerCallLocator(server_call_id)
        call_connection = calling_server_client.join_call(call_locator, CommunicationUserIdentifier(from_user), join_options)
        # [END create_server_call_with_calllocator]
        # [START hang_up_call]
        call_connection.hang_up()
        # [END hang_up_call]`

if __name__ == '__main__':
    sample = CallingServerClientSamples()
    sample.create_callingserver_client()
    sample.create_server_call_with_calllocator()