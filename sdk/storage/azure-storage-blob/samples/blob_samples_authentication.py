# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class AuthSamples(object):
    oauth_url = "{}://{}.blob.core.windows.net".format(
        os.getenv("PROTOCOL"),
        os.getenv("OAUTH_STORAGE_ACCOUNT_NAME")
    )

    def auth_default_azure_credential(self):
        # [START create_blob_service_client_oauth]
        # Get a credential for authentication
        # Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
        # For example user (who must be an Azure Event Hubs Data Owner role) to be logged in can be specified by the environment variable AZURE_USERNAME
        # Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
        # The docs above specify all mechanisms which the defaultCredential internally support.
        from azure.identity import DefaultAzureCredential
        default_credential = DefaultAzureCredential()
 
        # Instantiate a BlobServiceClient using a token credential
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self.oauth_url, credential=default_credential)
        # [END create_blob_service_client_oauth]
 
        # Get account information for the Blob Service
        account_info = blob_service_client.get_service_properties()
