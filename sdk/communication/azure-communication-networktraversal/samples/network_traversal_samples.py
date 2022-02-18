# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: network_traversal_samples.py
DESCRIPTION:
    These samples demonstrate creating a user, issuing a token, revoking a token and deleting a user.

USAGE:
    python network_traversal_samples.py
    Set the environment variables with your own values before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) AZURE_CLIENT_ID - the client ID of your active directory application
    3) AZURE_CLIENT_SECRET - the secret of your active directory application
    4) AZURE_TENANT_ID - the tenant ID of your active directory application
"""
import os
from azure.communication.networktraversal._shared.utils import parse_connection_str

class CommunicationRelayClientSamples(object):

    def __init__(self):
        self.connection_string = os.getenv('COMMUNICATION_SAMPLES_CONNECTION_STRING')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')

    def get_relay_config(self):
        from azure.communication.networktraversal import (
            CommunicationRelayClient
        )
        from azure.communication.identity import (
            CommunicationIdentityClient
        )

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            endpoint, _ = parse_connection_str(self.connection_string)
            identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
            relay_client = CommunicationRelayClient(endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
            relay_client = CommunicationRelayClient.from_connection_string(self.connection_string)
        
        print("Creating new user")
        user = identity_client.create_user()
        print("User created with id:" + user.properties.get('id'))

        print("Getting relay configuration")
        relay_configuration = relay_client.get_relay_configuration(user=user)

        for iceServer in relay_configuration.ice_servers:
            print("Icer server:")
            print(iceServer)

if __name__ == '__main__':
    sample = CommunicationRelayClientSamples()
    sample.get_relay_config()
