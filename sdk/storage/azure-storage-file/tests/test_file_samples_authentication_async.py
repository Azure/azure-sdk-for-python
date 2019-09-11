# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from datetime import datetime, timedelta

from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer, FakeStorageAccount

from asyncfiletestcase import (
    AsyncFileTestCase
)


FAKE_STORAGE = FakeStorageAccount(
    name='pyacrstorage',
    id='')

class TestFileAuthSamples(AsyncFileTestCase):
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    @AsyncFileTestCase.await_prepared_test
    async def test_auth_connection_string(self, resource_group, location, storage_account, storage_account_key):
        connection_string = self.connection_string(storage_account, storage_account_key)
        # Instantiate the FileServiceClient from a connection string
        # [START create_file_service_client_from_conn_string]
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(connection_string)
        # [END create_file_service_client_from_conn_string]

        # Get queue service properties
        properties = await file_service.get_service_properties()
        assert properties is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    @AsyncFileTestCase.await_prepared_test
    async def test_auth_shared_key(self, resource_group, location, storage_account, storage_account_key):
        url = self._account_url(storage_account.name)
        connection_string = self.connection_string(storage_account, storage_account_key)
        # Instantiate a FileServiceClient using a shared access key
        # [START create_file_service_client]
        from azure.storage.file.aio import FileServiceClient
        file_service_client = FileServiceClient(account_url=url, credential=storage_account_key)
        # [END create_file_service_client]

        # Get account information for the File Service
        account_info = await file_service_client.get_service_properties()
        assert account_info is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    @AsyncFileTestCase.await_prepared_test
    async def test_auth_shared_access_signature(self, resource_group, location, storage_account, storage_account_key):
        connection_string = self.connection_string(storage_account, storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        # Instantiate a FileServiceClient using a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service_client = FileServiceClient.from_connection_string(self.connection_string(storage_account, storage_account_key))

        # Create a SAS token to use to authenticate a new client
        # [START generate_sas_token]
        sas_token = file_service_client.generate_shared_access_signature(
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        # [END generate_sas_token]
        assert sas_token is not None
