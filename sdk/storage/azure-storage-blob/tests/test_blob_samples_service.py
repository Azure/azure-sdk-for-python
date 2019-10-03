# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

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


class TestBlobServiceSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING

    @record
    def test_get_storage_account_information(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START get_blob_service_account_info]
        account_info = blob_service_client.get_account_information()
        print('Using Storage SKU: {}'.format(account_info['sku_name']))
        # [END get_blob_service_account_info]
        assert account_info is not None

    @record
    def test_blob_service_properties(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
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
        blob_service_client.set_service_properties(logging, hour_metrics, minute_metrics, cors)
        # [END set_blob_service_properties]

        # [START get_blob_service_properties]
        properties = blob_service_client.get_service_properties()
        # [END get_blob_service_properties]
        assert properties is not None

    @record
    def test_blob_service_stats(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START get_blob_service_stats]
        stats = blob_service_client.get_service_stats()
        # [END get_blob_service_stats]
        assert stats is not None

    @record
    def test_container_operations(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        try:
            # [START bsc_create_container]
            try:
                new_container = blob_service_client.create_container("containerfromblobservice")
                properties = new_container.get_container_properties()
            except ResourceExistsError:
                print("Container already exists.")
            # [END bsc_create_container]

            # [START bsc_list_containers]
            # List all containers
            all_containers = blob_service_client.list_containers(include_metadata=True)
            for container in all_containers:
                print(container['name'], container['metadata'])

            # Filter results with name prefix
            test_containers = blob_service_client.list_containers(name_starts_with='test-')
            for container in test_containers:
                blob_service_client.delete_container(container)
            # [END bsc_list_containers]
            assert test_containers is not None

        finally:
            # [START bsc_delete_container]
            # Delete container if it exists
            try:
                blob_service_client.delete_container("containerfromblobservice")
            except ResourceNotFoundError:
                print("Container already deleted.")
            # [END bsc_delete_container]

    @record
    def test_get_blob_and_container_clients(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START bsc_get_container_client]
        # Get a client to interact with a specific container - though it may not yet exist
        container_client = blob_service_client.get_container_client("containertest")
        try:
            for blob in container_client.list_blobs():
                print("Found blob: ", blob.name)
        except ResourceNotFoundError:
            print("Container not found.")
        # [END bsc_get_container_client]
        try:
            # Create new Container in the service
            container_client.create_container()

            # [START bsc_get_blob_client]
            blob_client = blob_service_client.get_blob_client(container="containertest", blob="my_blob")
            try:
                stream = blob_client.download_blob()
            except ResourceNotFoundError:
                print("No blob found.")
            # [END bsc_get_blob_client]

            assert container_client is not None
            assert blob_client is not None

        finally:
            # Delete the container
            blob_service_client.delete_container("containertest")