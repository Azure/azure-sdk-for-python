# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_authentication.py
DESCRIPTION:
    These samples demonstrate authenticating a client via a connection string,
    shared access key, or by generating a sas token with which the returned signature
    can be used with the credential parameter of any BlobServiceClient,
    ContainerClient, BlobClient.
USAGE:
    python blob_samples_authentication.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) OAUTH_STORAGE_ACCOUNT_NAME - the oath storage account name
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
    5) ACTIVE_DIRECTORY_APPLICATION_ID - Azure Active Directory application ID
    6) ACTIVE_DIRECTORY_APPLICATION_SECRET - Azure Active Directory application secret
    7) ACTIVE_DIRECTORY_TENANT_ID - Azure Active Directory tenant ID
"""

import os

class AuthSamples(object):
    url = "https://{}.blob.core.windows.net".format(
        os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    )
    oauth_url = "https://{}.blob.core.windows.net".format(
        os.getenv("OAUTH_STORAGE_ACCOUNT_NAME")
    )

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    shared_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")
    active_directory_application_id = os.getenv("ACTIVE_DIRECTORY_APPLICATION_ID")
    active_directory_application_secret = os.getenv("ACTIVE_DIRECTORY_APPLICATION_SECRET")
    active_directory_tenant_id = os.getenv("ACTIVE_DIRECTORY_TENANT_ID")

    def auth_connection_string(self):
        # [START auth_from_connection_string]
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        # [END auth_from_connection_string]

        # [START auth_from_connection_string_container]
        from azure.storage.blob import ContainerClient
        container_client = ContainerClient.from_connection_string(
            self.connection_string, container_name="mycontainer")
        # [END auth_from_connection_string_container]

        # [START auth_from_connection_string_blob]
        from azure.storage.blob import BlobClient
        blob_client = BlobClient.from_connection_string(
            self.connection_string, container_name="mycontainer", blob_name="blobname.txt")
        # [END auth_from_connection_string_blob]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()

    def auth_shared_key(self):
        # [START create_blob_service_client]
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self.url, credential=self.shared_access_key)
        # [END create_blob_service_client]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()

    def auth_blob_url(self):
        # [START create_blob_client]
        from azure.storage.blob import BlobClient
        blob_client = BlobClient.from_blob_url(blob_url="https://account.blob.core.windows.net/container/blob-name")
        # [END create_blob_client]

        # [START create_blob_client_sas_url]
        from azure.storage.blob import BlobClient

        sas_url = "https://account.blob.core.windows.net/container/blob-name?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D"
        blob_client = BlobClient.from_blob_url(sas_url)
        # [END create_blob_client_sas_url]

    def auth_active_directory(self):
        # [START create_blob_service_client_oauth]
        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_tenant_id,
            self.active_directory_application_id,
            self.active_directory_application_secret
        )

        # Instantiate a BlobServiceClient using a token credential
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self.oauth_url, credential=token_credential)
        # [END create_blob_service_client_oauth]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_service_properties()

    def auth_shared_access_signature(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
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

    def auth_default_azure_credential(self):
        # [START create_blob_service_client_oauth]
        # Get a credential for authentication
        # Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
        # For example user (who must be an Azure Event Hubs Data Owner role) to be logged in can be specified by the environment variable AZURE_USERNAME
        # Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
        # The docs above specify all mechanisms which the defaultCredential internally support.
        from azure.identity import DefaultAzureCredential
        default_credential = DefaultAzureCredential()

        # Instantiate a BlobServiceClient using a token credential
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(
            account_url=self.oauth_url,
            credential=default_credential
        )
        # [END create_blob_service_client_oauth]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_service_properties()

if __name__ == '__main__':
    sample = AuthSamples()
    sample.auth_connection_string()
    sample.auth_active_directory()
    sample.auth_shared_access_signature()
    sample.auth_blob_url()
    sample.auth_default_azure_credential()
