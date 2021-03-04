# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: identity_sample.py
DESCRIPTION:
    These samples demonstrate creating a user, issuing a token, revoking a token and deleting a user.

    ///authenticating a client via a connection string
USAGE:
    python identity_samples.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""
import os

class CommunicationIdentityClientSamples(object):

    def __init__(self):
        self.connection_string = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.endpoint = os.getenv('AZURE_COMMUNICATION_SERVICE_ENDPOINT')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')

    def get_token(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        print("Getting token for: " + user.identifier)
        tokenresponse = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        print("Token issued with value: " + tokenresponse.token)

    def revoke_tokens(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        tokenresponse = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
        print("Revoking token: " + tokenresponse.token)
        identity_client.revoke_tokens(user)
        print(tokenresponse.token + " revoked successfully")

    def create_user(self):
        from azure.communication.identity import CommunicationIdentityClient

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        print("Creating new user")
        user = identity_client.create_user()
        print("User created with id:" + user.identifier)

    def create_user_and_token(self):
        from azure.communication.identity import (
            CommunicationIdentityClient,
            CommunicationTokenScope
        )
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        print("Creating new user with token")
        user, tokenresponse = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
        print("User created with id:" + user.identifier)
        print("Token issued with value: " + tokenresponse.token)

    def delete_user(self):
        from azure.communication.identity import CommunicationIdentityClient

        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
        user = identity_client.create_user()
        print("Deleting user: " + user.identifier)
        identity_client.delete_user(user)
        print(user.identifier + " deleted")

if __name__ == '__main__':
    sample = CommunicationIdentityClientSamples()
    sample.create_user()
    sample.create_user_and_token()
    sample.get_token()
    sample.revoke_tokens()
    sample.delete_user()
