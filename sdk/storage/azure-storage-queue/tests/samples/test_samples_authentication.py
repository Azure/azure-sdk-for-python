# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
import pytest

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
    url = "{}://{}.queue.core.windows.net".format(
        settings.PROTOCOL,
        settings.STORAGE_ACCOUNT_NAME
    )

    connection_string = settings.CONNECTION_STRING
    shared_access_key = settings.STORAGE_ACCOUNT_KEY
    active_directory_application_id = settings.ACTIVE_DIRECTORY_APPLICATION_ID
    active_directory_application_secret = settings.ACTIVE_DIRECTORY_APPLICATION_SECRET
    active_directory_tenant_id = settings.ACTIVE_DIRECTORY_TENANT_ID

    @record
    def test_auth_connection_string(self):
        # Instantiate a QueueServiceClient using a connection string
        # [START auth_from_connection_string]
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)
        # [END auth_from_connection_string]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

        assert properties is not None

    @record
    def test_auth_shared_key(self):

        # Instantiate a QueueServiceClient using a shared access key
        # [START create_queue_service_client]
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.url, credential=self.shared_access_key)
        # [END create_queue_service_client]
        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

        assert properties is not None

    @record
    def test_auth_active_directory(self):
        pytest.skip('pending azure identity')

        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_application_id,
            self.active_directory_application_secret,
            self.active_directory_tenant_id
        )

        # Instantiate a QueueServiceClient using a token credential
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.url, credential=token_credential)

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

        assert properties is not None

    def test_auth_shared_access_signature(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Instantiate a QueueServiceClient using a connection string
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # Create a SAS token to use for authentication of a client
        sas_token = queue_service.generate_shared_access_signature(
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        assert sas_token is not None
