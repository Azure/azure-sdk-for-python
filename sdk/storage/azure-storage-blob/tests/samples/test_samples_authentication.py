# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta

try:
    import tests.settings_real as settings
except ImportError:
    settings = None


class TestAuthSamples(object):
    url = "{}://{}.blob.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    connection_string = settings.CONNECTION_STRING
    shared_access_key = settings.STORAGE_ACCOUNT_KEY
    active_directory_application_id = settings.ACTIVE_DIRECTORY_APPLICATION_ID
    active_directory_application_secret = settings.ACTIVE_DIRECTORY_APPLICATION_SECRET
    active_directory_tenant_id = settings.ACTIVE_DIRECTORY_TENANT_ID

    def test_auth_connection_string(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()

        assert account_info is not None

    def test_auth_shared_key(self):

        # Instantiate a BlobServiceClient using a shared access key
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self.url, credential=self.shared_access_key)

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()

        assert account_info is not None

    def test_auth_active_directory(self):

        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_application_id,
            self.active_directory_application_secret,
            self.active_directory_tenant_id
        )

        # Instantiate a BlobServiceClient using a token credential
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self.url, credential=token_credential)

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()

        assert account_info is not None

    def test_auth_shared_access_signature(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a SAS token to use to authenticate a BlobClient or ContainerClient
        sas_token = blob_service_client.generate_shared_access_signature(
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        assert sas_token is not None

