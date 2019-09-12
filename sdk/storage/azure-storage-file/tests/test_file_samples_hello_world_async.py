# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer

from asyncfiletestcase import (
    AsyncFileTestCase
)

SOURCE_FILE = 'SampleSourceAsync.txt'


class TestHelloWorldSamples(AsyncFileTestCase):

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)
        super(TestHelloWorldSamples, self).setUp()

    #--Begin File Samples-----------------------------------------------------------------

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncFileTestCase.await_prepared_test
    async def test_create_client_with_connection_string(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string(storage_account, storage_account_key))

        # Get queue service properties
        properties = await file_service.get_service_properties()
        assert properties is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncFileTestCase.await_prepared_test
    async def test_create_file_share(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string(storage_account, storage_account_key), share="myshare")

        # Create the share
        await share.create_share()

        try:
            # [START get_share_properties]
            properties = await share.get_share_properties()
            # [END get_share_properties]
            assert properties is not None

        finally:
            # Delete the share
            await share.delete_share()

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncFileTestCase.await_prepared_test
    async def test_upload_file_to_share(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate the ShareClient from a connection string
        from azure.storage.file.aio import ShareClient
        share = ShareClient.from_connection_string(self.connection_string(storage_account, storage_account_key), share="share")

        # Create the share
        await share.create_share()

        try:
            # Instantiate the FileClient from a connection string
            # [START create_file_client]
            from azure.storage.file.aio import FileClient
            file = FileClient.from_connection_string(self.connection_string(storage_account, storage_account_key), share="share", file_path="myfile")
            # [END create_file_client]

            # Upload a file
            with open(SOURCE_FILE, "rb") as source_file:
                await file.upload_file(source_file)

        finally:
            # Delete the share
            await share.delete_share()
