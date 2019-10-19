# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from collections import namedtuple
import pytest
import asyncio
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer, mgmt_settings_fake as settings

from asyncqueuetestcase import (
    AsyncQueueTestCase
)


class TestQueueAuthSamplesAsync(AsyncQueueTestCase):

    active_directory_application_id = settings.ACTIVE_DIRECTORY_APPLICATION_ID
    active_directory_application_secret = settings.ACTIVE_DIRECTORY_APPLICATION_SECRET
    active_directory_tenant_id = settings.ACTIVE_DIRECTORY_TENANT_ID

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_auth_connection_string(self, resource_group, location, storage_account, storage_account_key):
        # Instantiate a QueueServiceClient using a connection string
        # [START async_auth_from_connection_string]
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        # [END async_auth_from_connection_string]

        # Get information for the Queue Service
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_auth_shared_key(self, resource_group, location, storage_account, storage_account_key):

        # Instantiate a QueueServiceClient using a shared access key
        # [START async_create_queue_service_client]
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        # [END async_create_queue_service_client]
        # Get information for the Queue Service
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_auth_active_directory(self, resource_group, location, storage_account, storage_account_key):

        # [START async_create_queue_service_client_token]
        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_application_id,
            self.active_directory_application_secret,
            self.active_directory_tenant_id
        )

        # Instantiate a QueueServiceClient using a token credential
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)
        # [END async_create_queue_service_client_token]

        # Get information for the Queue Service
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_auth_shared_access_signature(self, resource_group, location, storage_account, storage_account_key):
 
        # Instantiate a QueueServiceClient using a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient(self._account_url(storage_account.name), storage_account_key)

        # Create a SAS token to use for authentication of a client
        from azure.storage.queue import generate_account_sas

        sas_token = generate_account_sas(
            queue_service.account_name,
            queue_service.credential.account_key,
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        assert sas_token is not None
