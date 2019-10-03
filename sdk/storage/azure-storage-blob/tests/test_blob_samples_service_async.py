# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
try:
    import settings_real as settings
except ImportError:
    import blob_settings_fake as settings

from testcase import (
    StorageTestCase,
    TestMode,
    record
)


class TestBlobServiceSamplesAsync(StorageTestCase):

    connection_string = settings.BLOB_CONNECTION_STRING

    async def _test_get_storage_account_information_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START get_blob_service_account_info]
        account_info = await blob_service_client.get_account_information()
        print('Using Storage SKU: {}'.format(account_info['sku_name']))
        # [END get_blob_service_account_info]
        assert account_info is not None

    @record
    def test_get_storage_account_information_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_storage_account_information_async())

    async def _test_blob_service_properties_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START set_blob_service_properties]
        # Create service properties
        from azure.storage.blob import Logging, Metrics, CorsRule, RetentionPolicy

        # Create logging settings
        logging = Logging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create metrics for requests statistics
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create CORS rules
        cors_rule = CorsRule(['www.xyz.com'], ['GET'])
        cors = [cors_rule]

        # Set the service properties
        await blob_service_client.set_service_properties(logging, hour_metrics, minute_metrics, cors)
        # [END set_blob_service_properties]

        # [START get_blob_service_properties]
        properties = await blob_service_client.get_service_properties()
        # [END get_blob_service_properties]
        assert properties is not None

    @record
    def test_blob_service_properties_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_blob_service_properties_async())

    async def _test_blob_service_stats_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START get_blob_service_stats]
        stats = await blob_service_client.get_service_stats()
        # [END get_blob_service_stats]
        assert stats is not None

    @record
    def test_blob_service_stats_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_blob_service_stats_async())

    async def _test_container_operations_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        try:
            # [START bsc_create_container]
            try:
                new_container = await blob_service_client.create_container("containerfromblobserviceasync")
                properties = await new_container.get_container_properties()
            except ResourceExistsError:
                print("Container already exists.")
            # [END bsc_create_container]

            # [START bsc_list_containers]
            # List all containers
            all_containers = []
            async for container in blob_service_client.list_containers(include_metadata=True):
                all_containers.append(container)

            for container in all_containers:
                print(container['name'], container['metadata'])

            # Filter results with name prefix
            test_containers = []
            async for name in blob_service_client.list_containers(name_starts_with='test-'):
                test_containers.append(name)

            for container in test_containers:
                await blob_service_client.delete_container(container)
            # [END bsc_list_containers]
            assert test_containers is not None

        finally:
            # [START bsc_delete_container]
            # Delete container if it exists
            try:
                await blob_service_client.delete_container("containerfromblobserviceasync")
            except ResourceNotFoundError:
                print("Container already deleted.")
            # [END bsc_delete_container]

    @record
    def test_container_operations_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_container_operations_async())

    async def _test_get_blob_and_container_clients_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START bsc_get_container_client]
        # Get a client to interact with a specific container - though it may not yet exist
        container_client = blob_service_client.get_container_client("containertestasync")
        try:
            blobs_list = []
            async for blob in container_client.list_blobs():
                blobs_list.append(blob)

            for blob in blobs_list:
                print("Found blob: ", blob.name)
        except ResourceNotFoundError:
            print("Container not found.")
        # [END bsc_get_container_client]

        try:
            # Create new Container in the service
            await container_client.create_container()

            # [START bsc_get_blob_client]
            blob_client = blob_service_client.get_blob_client(container="containertestasync", blob="my_blob")
            try:
                stream = await blob_client.download_blob()
            except ResourceNotFoundError:
                print("No blob found.")
            # [END bsc_get_blob_client]

            assert container_client is not None
            assert blob_client is not None

        finally:
            # Delete the container
            await blob_service_client.delete_container("containertestasync")

    @record
    def test_get_blob_and_container_clients_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_and_container_clients_async())