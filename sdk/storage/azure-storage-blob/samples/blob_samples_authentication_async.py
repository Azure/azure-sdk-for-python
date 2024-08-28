# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_authentication_async.py
DESCRIPTION:
    These samples demonstrate authenticating a client via a connection string,
    shared access key, or by generating a sas token with which the returned signature
    can be used with the credential parameter of any BlobServiceClient,
    ContainerClient, BlobClient.
USAGE:
    python blob_samples_authentication_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) OAUTH_STORAGE_ACCOUNT_NAME - the oauth storage account name
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""


import os
import sys
import asyncio

class AuthSamplesAsync(object):
    url = "https://{}.blob.core.windows.net".format(
        os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    )
    oauth_url = "https://{}.blob.core.windows.net".format(
        os.getenv("OAUTH_STORAGE_ACCOUNT_NAME")
    )

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    shared_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

    async def auth_connection_string_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: auth_connection_string_async")
            sys.exit(1)
        # [START auth_from_connection_string]
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        # [END auth_from_connection_string]

        # [START auth_from_connection_string_container]
        from azure.storage.blob.aio import ContainerClient
        container_client = ContainerClient.from_connection_string(
            self.connection_string, container_name="mycontainer")
        # [END auth_from_connection_string_container]

        # [START auth_from_connection_string_blob]
        from azure.storage.blob.aio import BlobClient
        blob_client = BlobClient.from_connection_string(
            self.connection_string, container_name="mycontainer", blob_name="blobname.txt")
        # [END auth_from_connection_string_blob]

    async def auth_shared_key_async(self):
        if self.shared_access_key is None:
            print("Missing required environment variable: AZURE_STORAGE_ACCESS_KEY." + '\n' +
                  "Test: auth_shared_key_async")
            sys.exit(1)
        # [START create_blob_service_client]
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self.url, credential=self.shared_access_key)
        # [END create_blob_service_client]

    async def auth_blob_url_async(self):
        # [START create_blob_client]
        from azure.storage.blob.aio import BlobClient
        blob_client = BlobClient.from_blob_url(blob_url="https://account.blob.core.windows.net/container/blob-name")
        # [END create_blob_client]

        # [START create_blob_client_sas_url]
        from azure.storage.blob.aio import BlobClient

        sas_url = "https://account.blob.core.windows.net/container/blob-name?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D"
        blob_client = BlobClient.from_blob_url(sas_url)
        # [END create_blob_client_sas_url]

    async def auth_shared_access_signature_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: auth_shared_access_signature_async")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START create_sas_token]
        # Create a SAS token to use to authenticate a new client
        from datetime import datetime, timedelta
        from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas

        sas_token = generate_account_sas(
            blob_service_client.account_name,
            account_key=blob_service_client.credential.account_key,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        # [END create_sas_token]

    async def auth_default_azure_credential(self):
        # [START create_blob_service_client_oauth]
        # Get a credential for authentication
        # Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
        # For example user (who must be an Azure Event Hubs Data Owner role) to be logged in can be specified by the environment variable AZURE_USERNAME
        # Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
        # The docs above specify all mechanisms which the defaultCredential internally support.
        from azure.identity.aio import DefaultAzureCredential
        default_credential = DefaultAzureCredential()

        # Instantiate a BlobServiceClient using a token credential
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient(
            account_url=self.oauth_url,
            credential=default_credential
        )
        # [END create_blob_service_client_oauth]

        # Get account information for the Blob Service
        account_info = await blob_service_client.get_service_properties()

async def main():
    sample = AuthSamplesAsync()
    await sample.auth_connection_string_async()
    await sample.auth_shared_access_signature_async()
    await sample.auth_blob_url_async()
    await sample.auth_default_azure_credential()

if __name__ == '__main__':
    asyncio.run(main())
