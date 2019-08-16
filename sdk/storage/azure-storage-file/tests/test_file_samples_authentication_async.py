# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from datetime import datetime, timedelta

try:
    import settings_real as settings
except ImportError:
    import file_settings_fake as settings

from filetestcase import (
    FileTestCase,
    TestMode,
    record
)


class TestFileAuthSamples(FileTestCase):
    url = "{}://{}.file.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    connection_string = settings.CONNECTION_STRING
    shared_access_key = settings.STORAGE_ACCOUNT_KEY

    async def _test_auth_connection_string(self):
        # Instantiate the FileServiceClient from a connection string
        # [START create_file_service_client_from_conn_string]
        from azure.storage.file.aio import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)
        # [END create_file_service_client_from_conn_string]

        # Get queue service properties
        properties = await file_service.get_service_properties()
        assert properties is not None

    def test_auth_connection_string(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_connection_string())

    async def _test_auth_shared_key(self):
        # Instantiate a FileServiceClient using a shared access key
        # [START create_file_service_client]
        from azure.storage.file.aio import FileServiceClient
        file_service_client = FileServiceClient(account_url=self.url, credential=self.shared_access_key)
        # [END create_file_service_client]

        # Get account information for the File Service
        account_info = await file_service_client.get_service_properties()
        assert account_info is not None

    def test_auth_shared_key(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_shared_key())

    async def _test_auth_shared_access_signature(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Instantiate a FileServiceClient using a connection string
        from azure.storage.file.aio import FileServiceClient
        file_service_client = FileServiceClient.from_connection_string(self.connection_string)

        # Create a SAS token to use to authenticate a new client
        # [START generate_sas_token]
        sas_token = file_service_client.generate_shared_access_signature(
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        # [END generate_sas_token]
        assert sas_token is not None
    
    def test_auth_shared_access_signature(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_auth_shared_access_signature())
