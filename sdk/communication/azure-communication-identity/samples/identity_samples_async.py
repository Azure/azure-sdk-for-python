# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: identity_sample_async.py
DESCRIPTION:
    These samples demonstrate async identity client samples.

    ///authenticating a client via a connection string
USAGE:
    python identity_samples_async.py
"""

import asyncio
import os


class CommunicationIdentityClientSamples(object):

    def __init__(self):
        self.connection_string = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
        self.endpoint = os.getenv('AZURE_COMMUNICATION_SERVICE_ENDPOINT')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getnenv('AZURE_TENANT_ID')

    async def issue_token(self):
        from azure.communication.identity.aio import CommunicationIdentityClient
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)

        async with identity_client:
            user = await identity_client.create_user()
            print(user.identifier)
            tokenresponse = await identity_client.issue_token(user, scopes=["chat"])
            print(tokenresponse)
    
    async def revoke_tokens(self):
        from azure.communication.identity.aio import CommunicationIdentityClient
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)

        async with identity_client:
            user = await identity_client.create_user()
            tokenresponse = await identity_client.issue_token(user, scopes=["chat"])
            await identity_client.revoke_tokens(user)
            print(tokenresponse)

    async def create_user(self):
        from azure.communication.identity.aio import CommunicationIdentityClient
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)

        async with identity_client:
            user = await identity_client.create_user()
            print(user.identifier)

    async def delete_user(self):
        from azure.communication.identity.aio import CommunicationIdentityClient
        if self.client_id is not None and self.client_secret is not None and self.tenant_id is not None:
            from azure.identity import DefaultAzureCredential
            identity_client = CommunicationIdentityClient(self.endpoint, DefaultAzureCredential())
        else:
            identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)

        async with identity_client:
            user = await identity_client.create_user()
            await identity_client.delete_user(user)

async def main():
    sample = CommunicationIdentityClientSamples()
    await sample.create_user()
    await sample.delete_user()
    await sample.issue_token()
    await sample.revoke_tokens()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
