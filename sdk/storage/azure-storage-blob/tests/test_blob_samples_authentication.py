# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
try:
    from devtools_testutils import mgmt_settings_real as settings
except ImportError:
    from devtools_testutils import mgmt_settings_fake as settings


from testcase import (
    StorageTestCase
)


class TestAuthSamples(StorageTestCase):
    active_directory_application_id = settings.ACTIVE_DIRECTORY_APPLICATION_ID
    active_directory_application_secret = settings.ACTIVE_DIRECTORY_APPLICATION_SECRET
    active_directory_tenant_id = settings.ACTIVE_DIRECTORY_TENANT_ID

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_auth_connection_string(self, resource_group, location, storage_account, storage_account_key):
        connection_string = self.connection_string(storage_account, storage_account_key)

        # [START auth_from_connection_string]
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # [END auth_from_connection_string]

        # [START auth_from_connection_string_container]
        from azure.storage.blob import ContainerClient
        container_client = ContainerClient.from_connection_string(
            connection_string, container_name="mycontainer")
        # [END auth_from_connection_string_container]

        # [START auth_from_connection_string_blob]
        from azure.storage.blob import BlobClient
        blob_client = BlobClient.from_connection_string(
            connection_string, container_name="mycontainer", blob_name="blobname.txt")
        # [END auth_from_connection_string_blob]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()
        assert account_info is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_auth_shared_key(self, resource_group, location, storage_account, storage_account_key):
        # [START create_blob_service_client]
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self._account_url(storage_account.name), credential=storage_account_key)
        # [END create_blob_service_client]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()
        assert account_info is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_auth_blob_url(self, resource_group, location, storage_account, storage_account_key):
        # [START create_blob_client]
        from azure.storage.blob import BlobClient
        blob_client = BlobClient.from_blob_url(blob_url="https://account.blob.core.windows.net/container/blob-name")
        # [END create_blob_client]

        # [START create_blob_client_sas_url]
        from azure.storage.blob import BlobClient

        sas_url = "https://account.blob.core.windows.net/container/blob-name?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D"
        blob_client = BlobClient.from_blob_url(sas_url)
        # [END create_blob_client_sas_url]

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_auth_active_directory(self, resource_group, location, storage_account, storage_account_key):
        if not self.is_live:
            return
        # [START create_blob_service_client_oauth]
        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_application_id,
            self.active_directory_application_secret,
            self.active_directory_tenant_id
        )

        # Instantiate a BlobServiceClient using a token credential
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=self._account_url(storage_account.name), credential=token_credential)
        # [END create_blob_service_client_oauth]

        # Get account information for the Blob Service
        account_info = blob_service_client.get_service_properties()
        assert account_info is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    def test_auth_shared_access_signature(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string(storage_account, storage_account_key))

        # [START create_sas_token]
        # Create a SAS token to use to authenticate a new client
        from datetime import datetime, timedelta
        from azure.storage.blob import ResourceTypes, AccountSasPermissions

        sas_token = blob_service_client.generate_shared_access_signature(
            resource_types=ResourceTypes.OBJECT,
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        # [END create_sas_token]
        assert sas_token is not None
