# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer
from azure.storage.blob import (
    BlobServiceClient,
    DelimitedTextConfiguration,
)

# ------------------------------------------------------------------------------
CSV_DATA = b'Service,Package,Version,RepoPath,MissingDocs\r\nApp Configuration,' \
           b'azure-data-appconfiguration,1,appconfiguration,FALSE\r\nEvent Hubs' \
           b'\r\nEvent Hubs - Azure Storage CheckpointStore,' \
           b'azure-messaging-eventhubs-checkpointstore-blob,1.0.1,eventhubs,FALSE\r\nIdentity,azure-identity,' \
           b'1.1.0-beta.1,identity,FALSE\r\nKey Vault - Certificates,azure-security-keyvault-certificates,' \
           b'4.0.0,keyvault,FALSE\r\nKey Vault - Keys,azure-security-keyvault-keys,4.2.0-beta.1,keyvault,' \
           b'FALSE\r\nKey Vault - Secrets,azure-security-keyvault-secrets,4.1.0,keyvault,FALSE\r\n' \
           b'Storage - Blobs,azure-storage-blob,12.4.0,storage,FALSE\r\nStorage - Blobs Batch,' \
           b'azure-storage-blob-batch,12.4.0-beta.1,storage,FALSE\r\nStorage - Blobs Cryptography,' \
           b'azure-storage-blob-cryptography,12.4.0,storage,FALSE\r\nStorage - File Shares,' \
           b'azure-storage-file-share,12.2.0,storage,FALSE\r\nStorage - Queues,' \
           b'azure-storage-queue,12.3.0,storage,FALSE\r\nText Analytics,' \
           b'azure-ai-textanalytics,1.0.0-beta.2,textanalytics,FALSE\r\nTracing,' \
           b'azure-core-tracing-opentelemetry,1.0.0-beta.2,core,FALSE\r\nService,Package,Version,RepoPath,' \
           b'MissingDocs\r\nApp Configuration,azure-data-appconfiguration,1.0.1,appconfiguration,FALSE\r\n' \
           b'Event Hubs,azure-messaging-eventhubs,5.0.1,eventhubs,FALSE\r\n' \
           b'Event Hubs - Azure Storage CheckpointStore,azure-messaging-eventhubs-checkpointstore-blob,' \
           b'1.0.1,eventhubs,FALSE\r\nIdentity,azure-identity,1.1.0-beta.1,identity,FALSE\r\n' \
           b'Key Vault - Certificates,azure-security-keyvault-certificates,4.0.0,keyvault,FALSE\r\n' \
           b'Key Vault - Keys,azure-security-keyvault-keys,4.2.0-beta.1,keyvault,FALSE\r\n' \
           b'Key Vault - Secrets,azure-security-keyvault-secrets,4.1.0,keyvault,FALSE\r\n' \
           b'Storage - Blobs,azure-storage-blob,12.4.0,storage,FALSE\r\n' \
           b'Storage - Blobs Batch,azure-storage-blob-batch,12.4.0-beta.1,storage,FALSE\r\n' \
           b'Storage - Blobs Cryptography,azure-storage-blob-cryptography,12.4.0,storage,FALSE\r\n' \
           b'Storage - File Shares,azure-storage-file-share,12.2.0,storage,FALSE\r\n' \
           b'Storage - Queues,azure-storage-queue,12.3.0,storage,FALSE\r\n' \
           b'Text Analytics,azure-ai-textanalytics,1.0.0-beta.2,textanalytics,FALSE\r\n' \
           b'Tracing,azure-core-tracing-opentelemetry,1.0.0-beta.2,core,FALSE\r\n' \
           b'Service,Package,Version,RepoPath,MissingDocs\r\n' \
           b'App Configuration,azure-data-appconfiguration,1.0.1,appconfiguration,FALSE\r\n' \
           b'Event Hubs,azure-messaging-eventhubs,5.0.1,eventhubs,FALSE'


# ------------------------------------------------------------------------------


class StorageQuickQueryTest(StorageTestCase):
    def _setup(self, bsc):
        self.config = bsc._config
        self.container_name = self.get_resource_name('utqqcontainer')

        if self.is_live:
            try:
                bsc.create_container(self.container_name)
            except:
                pass

    def _teardown(self, bsc):
        if self.is_live:
            try:
                bsc.delete_container(self.container_name)
            except:
                pass

        return super(StorageQuickQueryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name("csvfile")

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @GlobalStorageAccountPreparer()
    def test_quick_query(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA)

        errors = []

        def progress_callback(error, bytes_processed, total_bytes):
            if error:
                errors.append(error)
            if not bytes_processed:
                print("All bytes have been processed")
                print("Total Bytes should be {}".format(total_bytes))
            else:
                print(bytes_processed)

        resp = blob_client.query("SELECT * from BlobStorage", progress_callback=progress_callback)
        resp.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(resp.total_bytes, len(CSV_DATA))

    @GlobalStorageAccountPreparer()
    def test_quick_query_with_serialization_setting(self, resource_group, location, storage_account,
                                                    storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []

        def progress_callback(error, bytes_processed, total_bytes):
            if error:
                errors.append(error)
            if not bytes_processed:
                print("All bytes have been processed")
                print("Total Bytes should be {}".format(total_bytes))
            else:
                print(bytes_processed)

        input_seri = DelimitedTextConfiguration(column_separator=',', field_quote='"', record_separator='\n',
                                                escape_char='', headers_present=False
                                                )
        output_seri = DelimitedTextConfiguration(column_separator=';', field_quote="'", record_separator='.',
                                                 escape_char='\\', headers_present=True
                                                 )
        resp = blob_client.query("SELECT * from BlobStorage", progress_callback=progress_callback,
                                 input_serialization=input_seri, output_serialization=output_seri)
        query_result = resp.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(resp.total_bytes, len(CSV_DATA))
        self.assertTrue(len(query_result) > 0)

    @GlobalStorageAccountPreparer()
    def test_quick_query_with_serialization_setting_throws_error(self, resource_group, location, storage_account,
                                                                 storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []

        def progress_callback(error, bytes_processed, total_bytes):
            if error:
                errors.append(error)
            if not bytes_processed:
                print("All bytes have been processed")
                print("Total Bytes should be {}".format(total_bytes))
            else:
                print(bytes_processed)

        input_seri = DelimitedTextConfiguration(column_separator=',', field_quote='"', record_separator='\n',
                                                escape_char='', headers_present=True
                                                )
        output_seri = DelimitedTextConfiguration(column_separator=';', field_quote="'", record_separator='.',
                                                 escape_char='\\', headers_present=True
                                                 )
        resp = blob_client.query("SELECT RepoPath from BlobStorage", progress_callback=progress_callback,
                                 input_serialization=input_seri, output_serialization=output_seri)
        query_result = resp.readall()

        # the error is because that line only has one column
        self.assertEqual(len(errors), 1)
        self.assertEqual(resp.total_bytes, len(CSV_DATA))
        self.assertTrue(len(query_result) > 0)

    @GlobalStorageAccountPreparer()
    def test_quick_query_with_serialization_json_setting(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{\"name\": \"owner\", \"id\": 1}'
        data2 = b'{\"name2\": \"owner2\"}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []

        def progress_callback(error, bytes_processed, total_bytes):
            if error:
                errors.append(error)
            if not bytes_processed:
                print("All bytes have been processed")
                print("Total Bytes should be {}".format(total_bytes))
            else:
                print(bytes_processed)

        input_seri = '\n'
        output_seri = ';'

        resp = blob_client.query("SELECT name from BlobStorage", progress_callback=progress_callback,
                                 input_serialization=input_seri, output_serialization=output_seri)
        query_result = resp.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(resp.total_bytes, len(data))
        self.assertTrue(len(query_result) > 0)
        blob_client.delete_blob()
# ------------------------------------------------------------------------------
