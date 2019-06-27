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
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record
)


class TestAuthSamples(StorageTestCase):
    url = "{}://{}.file.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    connection_string = settings.CONNECTION_STRING
    shared_access_key = settings.STORAGE_ACCOUNT_KEY

    @record
    def test_auth_connection_string(self):
        # Instantiate the FileServiceClient from a connection string
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = file_service.get_service_properties()
        assert properties is not None

    @record
    def test_auth_shared_key(self):
        # Instantiate a FileServiceClient using a shared access key
        from azure.storage.file import FileServiceClient
        file_service_client = FileServiceClient(account_url=self.url, credential=self.shared_access_key)

        # Get account information for the File Service
        account_info = file_service_client.get_service_properties()
        assert account_info is not None

    def test_auth_shared_access_signature(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Instantiate a FileServiceClient using a connection string
        from azure.storage.file import FileServiceClient
        file_service_client = FileServiceClient.from_connection_string(self.connection_string)

        # Create a SAS token to use to authenticate a new client
        sas_token = file_service_client.generate_shared_access_signature(
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        assert sas_token is not None
