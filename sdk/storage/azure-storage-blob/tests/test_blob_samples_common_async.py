# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from azure.core.exceptions import ResourceExistsError

try:
    import settings_real as settings
except ImportError:
    import blob_settings_fake as settings

from testcase import (
    StorageTestCase,
    TestMode,
    record
)

SOURCE_FILE = 'SampleSource.txt'


class TestCommonBlobSamplesAsync(StorageTestCase):

    connection_string = settings.BLOB_CONNECTION_STRING

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)

        super(TestCommonBlobSamplesAsync, self).setUp()

    def tearDown(self):
        if os.path.isfile(SOURCE_FILE):
            try:
                os.remove(SOURCE_FILE)
            except:
                pass

        return super(TestCommonBlobSamplesAsync, self).tearDown()

    #--Begin Blob Samples-----------------------------------------------------------------

    async def _test_blob_snapshots_async(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerformyblobsasync")

        # Create new Container
        await container_client.create_container()

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            await container_client.upload_blob(name="my_blob", data=data)

        # Get a BlobClient for a specific blob
        blob_client = blob_service_client.get_blob_client(container="containerformyblobsasync", blob="my_blob")

        # [START create_blob_snapshot]
        # Create a read-only snapshot of the blob at this point in time
        snapshot_blob = await blob_client.create_snapshot()

        # Get the snapshot ID
        print(snapshot_blob.get('snapshot'))

        # Delete only the snapshot (blob itself is retained)
        await blob_client.delete_blob(delete_snapshots="only")
        # [END create_blob_snapshot]

        # Delete container
        await blob_service_client.delete_container("containerformyblobsasync")

    @record
    def test_blob_snapshots_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_blob_snapshots_async())

    async def _test_soft_delete_and_undelete_blob_async(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a retention policy to retain deleted blobs
        from azure.storage.blob import RetentionPolicy
        delete_retention_policy = RetentionPolicy(enabled=True, days=1)

        # Set the retention policy on the service
        await blob_service_client.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerfordeletedblobsasync")

        # Create new Container
        try:
            await container_client.create_container()
        except ResourceExistsError:
            # Container already created
            pass

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            blob_client = await container_client.upload_blob(name="my_blob", data=data)

        # Soft delete blob in the container (blob can be recovered with undelete)
        await blob_client.delete_blob()

        # [START undelete_blob]
        # Undelete the blob before the retention policy expires
        await blob_client.undelete_blob()
        # [END undelete_blob]

        # [START get_blob_properties]
        properties = await blob_client.get_blob_properties()
        # [END get_blob_properties]

        assert properties is not None

        # Delete container
        await blob_service_client.delete_container("containerfordeletedblobsasync")

    @record
    def test_soft_delete_and_undelete_blob_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_soft_delete_and_undelete_blob_async())

    async def _test_acquire_lease_on_blob_async(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("leasemyblobscontainerasync")

        # Create new Container
        await container_client.create_container()

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            await container_client.upload_blob(name="my_blob", data=data)

        # [START acquire_lease_on_blob]
        # Get the blob client
        blob_client = blob_service_client.get_blob_client("leasemyblobscontainerasync", "my_blob")

        # Acquire a lease on the blob
        lease = await blob_client.acquire_lease()

        # Delete blob by passing in the lease
        await blob_client.delete_blob(lease=lease)
        # [END acquire_lease_on_blob]

        # Delete container
        await blob_service_client.delete_container("leasemyblobscontainerasync")

    @record
    def test_acquire_lease_on_blob_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_acquire_lease_on_blob_async())

    async def _test_copy_blob_from_url_and_abort_copy_async(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("copyblobcontainerasync")

        # Create new Container
        await container_client.create_container()

        try:
            # [START copy_blob_from_url]
            # Get the blob client with the source blob
            source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
            copied_blob = blob_service_client.get_blob_client("copyblobcontainerasync", '59466-0.txt')

            # start copy and check copy status
            copy = await copied_blob.start_copy_from_url(source_blob)
            props = await copied_blob.get_blob_properties()
            print(props.copy.status)
            # [END copy_blob_from_url]

            copy_id = props.copy.id
            # [START abort_copy_blob_from_url]
            # Passing in copy id to abort copy operation
            await copied_blob.abort_copy(copy_id)

            # check copy status
            props = await copied_blob.get_blob_properties()
            print(props.copy.status)
            # [END abort_copy_blob_from_url]

        finally:
            await blob_service_client.delete_container("copyblobcontainerasync")

    @record
    def test_copy_blob_from_url_and_abort_copy_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_copy_blob_from_url_and_abort_copy_async())