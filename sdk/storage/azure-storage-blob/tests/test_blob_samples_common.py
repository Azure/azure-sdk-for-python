# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.storage.blob import BlobServiceClient

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


class TestCommonBlobSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING

    def setUp(self):
        data = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        with open(SOURCE_FILE, 'wb') as stream:
            stream.write(data)

        super(TestCommonBlobSamples, self).setUp()

    def tearDown(self):
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        for container in ['containerformyblobs', 'containerfordeletedblobs', 'leasemyblobscontainer']:
            try:
                blob_service_client.delete_container(container)
            except HttpResponseError:
                pass

        if os.path.isfile(SOURCE_FILE):
            try:
                os.remove(SOURCE_FILE)
            except:
                pass

        return super(TestCommonBlobSamples, self).tearDown()

    #--Begin Blob Samples-----------------------------------------------------------------

    @record
    def test_blob_snapshots(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerformyblobs")

        # Create new Container
        container_client.create_container()

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get a BlobClient for a specific blob
        blob_client = blob_service_client.get_blob_client(container="containerformyblobs", blob="my_blob")

        # [START create_blob_snapshot]
        # Create a read-only snapshot of the blob at this point in time
        snapshot_blob = blob_client.create_snapshot()

        # Get the snapshot ID
        print(snapshot_blob.get('snapshot'))
        # [END create_blob_snapshot]

        # Delete only the snapshot (blob itself is retained)
        blob_client.delete_blob(delete_snapshots="only")

        # Delete container
        blob_service_client.delete_container("containerformyblobs")

    @record
    def test_soft_delete_and_undelete_blob(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a retention policy to retain deleted blobs
        from azure.storage.blob import RetentionPolicy
        delete_retention_policy = RetentionPolicy(enabled=True, days=1)

        # Set the retention policy on the service
        blob_service_client.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerfordeletedblobs")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            # Container already created
            pass

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            blob_client = container_client.upload_blob(name="my_blob", data=data)

        # Soft delete blob in the container (blob can be recovered with undelete)
        blob_client.delete_blob()

        # [START undelete_blob]
        # Undelete the blob before the retention policy expires
        blob_client.undelete_blob()
        # [END undelete_blob]

        # [START get_blob_properties]
        properties = blob_client.get_blob_properties()
        # [END get_blob_properties]

        assert properties is not None

        # Delete container
        blob_service_client.delete_container("containerfordeletedblobs")

    @record
    def test_acquire_lease_on_blob(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("leasemyblobscontainer")

        # Create new Container
        container_client.create_container()

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get the blob client
        blob_client = blob_service_client.get_blob_client("leasemyblobscontainer", "my_blob")

        # [START acquire_lease_on_blob]
        # Acquire a lease on the blob
        lease = blob_client.acquire_lease()

        # Delete blob by passing in the lease
        blob_client.delete_blob(lease=lease)
        # [END acquire_lease_on_blob]

        # Delete container
        blob_service_client.delete_container("leasemyblobscontainer")

    @record
    def test_start_copy_blob_from_url_and_abort_copy(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("copyblobcontainer")

        # Create new Container
        container_client.create_container()

        try:
            # [START copy_blob_from_url]
            # Get the blob client with the source blob
            source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
            copied_blob = blob_service_client.get_blob_client("copyblobcontainer", '59466-0.txt')

            # start copy and check copy status
            copy = copied_blob.start_copy_from_url(source_blob)
            props = copied_blob.get_blob_properties()
            print(props.copy.status)
            # [END copy_blob_from_url]

            copy_id = props.copy.id
            # [START abort_copy_blob_from_url]
            # Passing in copy id to abort copy operation
            copied_blob.abort_copy(copy_id)

            # check copy status
            props = copied_blob.get_blob_properties()
            print(props.copy.status)
            # [END abort_copy_blob_from_url]

        finally:
            blob_service_client.delete_container("copyblobcontainer")