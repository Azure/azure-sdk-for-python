
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: callingserver_samples_async.py
DESCRIPTION:
    These samples demonstrate create a callingserver client, create a call_connection,
    create a server_call_with_calllocator.
    The CommunicationIdentityClient is authenticated using a connection string.
    The CallingServerClient is authenticated using AzureAD Managed Identity.
USAGE:
    python callingserver_samples_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
    2) COMMUNICATION_SAMPLES_CONNECTION_STRING - Azure Communication Service resource connection string
"""

import os

class CallingServerClientSamplesAsync(object):
    from azure.communication.identity.aio import CommunicationIdentityClient
    connection_string = os.environ.get("COMMUNICATION_SAMPLES_CONNECTION_STRING", None)
    if not connection_string:
        raise ValueError("Set COMMUNICATION_SAMPLES_CONNECTION_STRING env before run this sample.")

    identity_client = CommunicationIdentityClient.from_connection_string(connection_string)
    user = identity_client.create_user()

    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _thread_id = None

    def create_callingserver_client_async(self):
        endpoint = self.endpoint
        # [START create_callingserver_client]
        from azure.communication.callingserver.aio import CallingServerClient
        from azure.identity.aio import DefaultAzureCredential

        # set `endpoint` to an existing ACS endpoint
        calling_server_client_async = CallingServerClient(endpoint, DefaultAzureCredential())
        # [END create_callingserver_client]

    async def create_call_connection_async(self):
        endpoint = self.endpoint
        from_user = self.user
        # [START create_call_connection]
        from azure.communication.callingserver import PhoneNumberIdentifier, CreateCallOptions, MediaType, EventSubscriptionType
        from azure.communication.callingserver.aio import CallingServerClient
        from azure.identity.aio import DefaultAzureCredential
        to_user = PhoneNumberIdentifier(self.to_phone_number)
        options = CreateCallOptions(
            callback_uri="<your-callback-uri>",
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED, EventSubscriptionType.DTMF_RECEIVED]
        )
        # set `endpoint` to an existing ACS endpoint
        calling_server_client_async = CallingServerClient(endpoint, DefaultAzureCredential())
        call_connection_async = await calling_server_client_async.create_call_connection(
                    source=from_user,
                    targets=[to_user],
                    options=options,
                    )
        # [END create_call_connection]
        # [START hang_up_call]
        await call_connection_async.hang_up()
        # [END hang_up_call]

    async def create_server_call_with_calllocator_async(self):
        endpoint = self.endpoint
        from_user = self.user
        # [START create_server_call_with_calllocator]
        # set `endpoint` to an existing ACS endpoint
        from azure.communication.callingserver import ServerCallLocator, CommunicationUserIdentifier, MediaType, EventSubscriptionType, JoinCallOptions
        from azure.communication.callingserver.aio import CallingServerClient
        from azure.identity.aio import DefaultAzureCredential

        join_options = JoinCallOptions(
            callback_uri="<your-callback-uri>",
            requested_media_types=[MediaType.AUDIO],
            requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED]
        )
        # set `endpoint` to an existing ACS endpoint
        calling_server_client_async = CallingServerClient(endpoint, DefaultAzureCredential())
        server_call_id = "<your-server-call-id>"
        call_locator = ServerCallLocator(server_call_id)
        call_connection_async = await calling_server_client_async.join_call(call_locator, CommunicationUserIdentifier(from_user), join_options)
        # [END create_server_call_with_calllocator]
        # [START hang_up_call]
        await call_connection_async.hang_up()
        # [END hang_up_call]`

if __name__ == '__main__':
    sample = CallingServerClientSamplesAsync()
    sample.create_callingserver_client_async()
    sample.create_server_call_with_calllocator_async()