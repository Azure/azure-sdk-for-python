# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: file_samples_authentication_async.py

DESCRIPTION:
    These samples demonstrate authenticating a client via a connection string,
    shared access key, or by generating a sas token with which the returned signature
    can be used with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

USAGE:
    python file_samples_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ACCOUNT_URL - the queue service account URL
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""

import os
import asyncio
from datetime import datetime, timedelta


class FileAuthSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

    async def authentication_connection_string_async(self):
        # Instantiate the ShareServiceClient from a connection string
        # [START create_share_service_client_from_conn_string]
        from azure.storage.fileshare.aio import ShareServiceClient
        file_service = ShareServiceClient.from_connection_string(self.connection_string)
        # [END create_share_service_client_from_conn_string]

    async def authentication_shared_access_key_async(self):
        # Instantiate a ShareServiceClient using a shared access key
        # [START create_share_service_client]
        from azure.storage.fileshare.aio import ShareServiceClient
        share_service_client = ShareServiceClient(
            account_url=self.account_url,
            credential=self.access_key
        )
        # [END create_share_service_client]

    async def authentication_shared_access_signature_async(self):
        # Instantiate a ShareServiceClient using a connection string
        from azure.storage.fileshare.aio import ShareServiceClient
        share_service_client = ShareServiceClient.from_connection_string(self.connection_string)

        # Create a SAS token to use to authenticate a new client
        from azure.storage.fileshare import generate_account_sas, ResourceTypes, AccountSasPermissions

        sas_token = generate_account_sas(
            share_service_client.account_name,
            share_service_client.credential.account_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

    async def authentication_default_azure_credential_async(self):
        # [START file_share_oauth]
        # Get a credential for authentication
        # DefaultAzureCredential attempts a chained set of authentication methods.
        # See documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
        from azure.identity.aio import DefaultAzureCredential
        default_credential = DefaultAzureCredential()

        # Instantiate a ShareServiceClient using a token credential and token_intent
        from azure.storage.fileshare.aio import ShareServiceClient
        share_service_client = ShareServiceClient(
            account_url=self.account_url,
            credential=default_credential,
            # When using a token credential, you MUST also specify a token_intent
            token_intent='backup'
        )

        # Only Directory and File operations, and a certain few Share operations, are currently supported for OAuth.
        # Create a ShareFileClient from the ShareServiceClient.
        share_client = share_service_client.get_share_client('myshare')
        share_file_client = share_client.get_file_client('mydirectory/myfile')

        properties = await share_file_client.get_file_properties()
        # [END file_share_oauth]


async def main():
    sample = FileAuthSamplesAsync()
    await sample.authentication_connection_string_async()
    await sample.authentication_shared_access_key_async()
    await sample.authentication_shared_access_signature_async()
    await sample.authentication_default_azure_credential_async()

if __name__ == '__main__':
    asyncio.run(main())
