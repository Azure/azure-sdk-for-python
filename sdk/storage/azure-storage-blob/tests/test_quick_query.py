# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import os

import pytest

from devtools_testutils import recorded_by_proxy
from settings.testcase import BlobPreparer
from devtools_testutils.storage import StorageRecordedTestCase
from azure.storage.blob import (
    BlobServiceClient,
    DelimitedJsonDialect,
    DelimitedTextDialect
)

# ------------------------------------------------------------------------------
from azure.storage.blob._models import ArrowDialect, ArrowType, QuickQueryDialect

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
           b'Event Hubs,azure-messaging-eventhubs,5.0.1,eventhubs,FALSE\r\n'

CONVERTED_CSV_DATA = b"Service;Package;Version;RepoPath;MissingDocs.App Configuration;azure-data-appconfiguration;" \
                     b"1;appconfiguration;FALSE.Event Hubs.Event Hubs - Azure Storage CheckpointStore;azure-messaging-eventhubs-checkpointstore-blob;" \
                     b"'1.0.1';eventhubs;FALSE.Identity;azure-identity;'1.1.0-beta.1';identity;FALSE.Key Vault - Certificates;" \
                     b"azure-security-keyvault-certificates;'4.0.0';keyvault;FALSE.Key Vault - Keys;azure-security-keyvault-keys;" \
                     b"'4.2.0-beta.1';keyvault;FALSE.Key Vault - Secrets;azure-security-keyvault-secrets;'4.1.0';keyvault;" \
                     b"FALSE.Storage - Blobs;azure-storage-blob;'12.4.0';storage;FALSE.Storage - Blobs Batch;" \
                     b"azure-storage-blob-batch;'12.4.0-beta.1';storage;FALSE.Storage - Blobs Cryptography;" \
                     b"azure-storage-blob-cryptography;'12.4.0';storage;FALSE.Storage - File Shares;azure-storage-file-share;" \
                     b"'12.2.0';storage;FALSE.Storage - Queues;azure-storage-queue;'12.3.0';storage;FALSE.Text Analytics;" \
                     b"azure-ai-textanalytics;'1.0.0-beta.2';textanalytics;FALSE.Tracing;azure-core-tracing-opentelemetry;" \
                     b"'1.0.0-beta.2';core;FALSE.Service;Package;Version;RepoPath;MissingDocs.App Configuration;" \
                     b"azure-data-appconfiguration;'1.0.1';appconfiguration;FALSE.Event Hubs;azure-messaging-eventhubs;" \
                     b"'5.0.1';eventhubs;FALSE.Event Hubs - Azure Storage CheckpointStore;azure-messaging-eventhubs-checkpointstore-blob;" \
                     b"'1.0.1';eventhubs;FALSE.Identity;azure-identity;'1.1.0-beta.1';identity;" \
                     b"FALSE.Key Vault - Certificates;azure-security-keyvault-certificates;'4.0.0';" \
                     b"keyvault;FALSE.Key Vault - Keys;azure-security-keyvault-keys;'4.2.0-beta.1';keyvault;FALSE.Key Vault - Secrets;" \
                     b"azure-security-keyvault-secrets;'4.1.0';keyvault;FALSE.Storage - Blobs;azure-storage-blob;'12.4.0';" \
                     b"storage;FALSE.Storage - Blobs Batch;azure-storage-blob-batch;'12.4.0-beta.1';storage;FALSE.Storage - Blobs Cryptography;" \
                     b"azure-storage-blob-cryptography;'12.4.0';storage;FALSE.Storage - File Shares;azure-storage-file-share;" \
                     b"'12.2.0';storage;FALSE.Storage - Queues;azure-storage-queue;'12.3.0';storage;FALSE.Text Analytics;" \
                     b"azure-ai-textanalytics;'1.0.0-beta.2';textanalytics;FALSE.Tracing;azure-core-tracing-opentelemetry;" \
                     b"'1.0.0-beta.2';core;FALSE.Service;Package;Version;RepoPath;MissingDocs.App Configuration;" \
                     b"azure-data-appconfiguration;'1.0.1';appconfiguration;FALSE.Event Hubs;azure-messaging-eventhubs;" \
                     b"'5.0.1';eventhubs;FALSE."

# ------------------------------------------------------------------------------


class TestStorageQuickQuery(StorageRecordedTestCase):
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

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name("csvfile")

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        reader = blob_client.query_blob("SELECT * from BlobStorage", on_error=on_error)
        data = reader.readall()

        assert len(errors) == 0
        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'\n')
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        reader = blob_client.query_blob("SELECT * from BlobStorage")
        read_records = reader.records()

        # Assert first line has header
        data = next(read_records)
        assert data == b'Service,Package,Version,RepoPath,MissingDocs'

        for record in read_records:
            data += record

        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'')
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_encoding(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        reader = blob_client.query_blob("SELECT * from BlobStorage", on_error=on_error, encoding='utf-8')
        data = reader.readall()

        assert len(errors) == 0
        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'\n').decode('utf-8')
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_encoding(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        reader = blob_client.query_blob("SELECT * from BlobStorage", encoding='utf-8')
        data = ''
        for record in reader.records():
            data += record

        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'').decode('utf-8')
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_output_records_excluding_headers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        input_format = DelimitedTextDialect(has_header=True)
        output_format = DelimitedTextDialect(has_header=False)
        reader = blob_client.query_blob("SELECT * from BlobStorage", blob_format=input_format, output_format=output_format)
        read_records = reader.records()

        # Assert first line does not include header
        data = next(read_records)
        assert data == b'App Configuration,azure-data-appconfiguration,1,appconfiguration,FALSE'

        for record in read_records:
            data += record

        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'')[44:]
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_output_records_including_headers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        input_format = DelimitedTextDialect(has_header=True)
        reader = blob_client.query_blob("SELECT * from BlobStorage", blob_format=input_format)
        read_records = reader.records()

        # Assert first line does not include header
        data = next(read_records)
        assert data == b'Service,Package,Version,RepoPath,MissingDocs'

        for record in read_records:
            data += record

        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'')
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        reader = blob_client.query_blob("SELECT * from BlobStorage")
        data = b''
        progress = 0
        for record in reader.records():
            if record:
                data += record
                progress += len(record) + 2
        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert data, CSV_DATA.replace(b'\r\n' == b'')
        assert progress == reader._size
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_serialization_setting(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        input_format = DelimitedTextDialect(
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            escapechar='',
            has_header=False
        )
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        assert len(errors) == 0
        assert resp._size == len(CSV_DATA)
        assert query_result == CONVERTED_CSV_DATA
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_serialization_setting(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        input_format = DelimitedTextDialect(
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            escapechar='',
            has_header=False
        )
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='%',
            escapechar='\\'
        )

        reader = blob_client.query_blob(
            "SELECT * from BlobStorage",
            blob_format=input_format,
            output_format=output_format)
        data = []
        for record in reader.records():
            if record:
                data.append(record)

        assert len(reader) == len(CSV_DATA)
        assert reader._size == reader._bytes_processed
        assert len(data) == 33
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_fatal_error_handler(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        assert len(errors) == 1
        assert resp._size == 43
        assert query_result == b''
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_fatal_error_handler(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        data = []
        for record in resp.records():
            data.append(record)

        assert len(errors) == 1
        assert resp._size == 43
        assert data == [b'']
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_fatal_error_handler_raise(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []

        def on_error(error):
            raise Exception(error.description)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        with pytest.raises(Exception):
            query_result = resp.readall()
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_fatal_error_handler_raise(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []

        def on_error(error):
            raise Exception(error.description)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)

        with pytest.raises(Exception):
            for record in resp.records():
                print(record)
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_fatal_error_ignore(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            blob_format=input_format,
            output_format=output_format)
        query_result = resp.readall()
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_fatal_error_ignore(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = blob_client.query_blob(
            "SELECT * from BlobStorage",
            blob_format=input_format,
            output_format=output_format)

        for record in resp.records():
            print(record)
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_nonfatal_error_handler(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = DelimitedTextDialect(
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            escapechar='',
            has_header=True
        )
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\',
        )
        resp = blob_client.query_blob(
            "SELECT RepoPath from BlobStorage",
            blob_format=input_format,
            output_format=output_format,
            on_error=on_error)
        query_result = resp.readall()

        # the error is because that line only has one column
        assert len(errors) == 1
        assert resp._size == len(CSV_DATA)
        assert len(query_result) > 0
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_nonfatal_error_handler(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = DelimitedTextDialect(
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            escapechar='',
            has_header=True
        )
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='%',
            escapechar='\\',
        )
        resp = blob_client.query_blob(
            "SELECT RepoPath from BlobStorage",
            blob_format=input_format,
            output_format=output_format,
            on_error=on_error)
        data = list(resp.records())

        # the error is because that line only has one column
        assert len(errors) == 1
        assert resp._size == len(CSV_DATA)
        assert len(data) == 32
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_nonfatal_error_ignore(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        input_format = DelimitedTextDialect(
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            escapechar='',
            has_header=True
        )
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\',
        )
        resp = blob_client.query_blob(
            "SELECT RepoPath from BlobStorage",
            blob_format=input_format,
            output_format=output_format)
        query_result = resp.readall()
        assert resp._size == len(CSV_DATA)
        assert len(query_result) > 0
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_nonfatal_error_ignore(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the csv file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(CSV_DATA, overwrite=True)

        input_format = DelimitedTextDialect(
            delimiter=',',
            quotechar='"',
            lineterminator='\n',
            escapechar='',
            has_header=True
        )
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='$',
            escapechar='\\',
        )
        resp = blob_client.query_blob(
            "SELECT RepoPath from BlobStorage",
            blob_format=input_format,
            output_format=output_format)
        data = list(resp.records())
        assert resp._size == len(CSV_DATA)
        assert len(data) == 32
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_readall_with_json_serialization_setting(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
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
        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect(delimiter='\n')
        output_format = DelimitedJsonDialect(delimiter=';')

        resp = blob_client.query_blob(
            "SELECT name from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        assert len(errors) == 0
        assert resp._size == len(data)
        assert query_result == b'{"name":"owner"};{};{"name":"owner"};'
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_iter_records_with_json_serialization_setting(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
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
        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect(delimiter='\n')
        output_format = DelimitedJsonDialect(delimiter=';')

        resp = blob_client.query_blob(
            "SELECT name from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        listdata = list(resp.records())

        assert len(errors) == 0
        assert resp._size == len(data)
        assert listdata, [b'{"name":"owner"}',b'{}',b'{"name":"owner"}' == b'']
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_with_only_input_json_serialization_setting(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data1 = b'{\"name\": \"owner\", \"id\": 1}'
        data2 = b'{\"name2\": \"owner2\"}'
        data = data1 + data2 + data1

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect(delimiter='\n')
        output_format = None

        resp = blob_client.query_blob(
            "SELECT name from BlobStorage",
            on_error=on_error,
            blob_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        assert len(errors) == 0
        assert resp._size == len(data)
        assert query_result == b'{"name":"owner"}\n{}\n{"name":"owner"}\n'
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_output_in_arrow_format(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        data = b'100,200,300,400\n300,400,500,600\n'

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        blob_client.upload_blob(data, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        output_format = [ArrowDialect(ArrowType.DECIMAL, name="abc", precision=4, scale=2)]

        resp = blob_client.query_blob(
            "SELECT _2 from BlobStorage WHERE _1 > 250",
            on_error=on_error,
            output_format=output_format)
        query_result = base64.b64encode(resp.readall())
        # expected_result = b'/////3gAAAAQAAAAAAAKAAwABgAFAAgACgAAAAABBAAMAAAACAAIAAAABAAIAAAABAAAAAEAAAAUAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEHEAAAABwAAAAEAAAAAAAAAAMAAABhYmMACAAMAAQACAAIAAAABAAAAAIAAAD/////cAAAABAAAAAAAAoADgAGAAUACAAKAAAAAAMEABAAAAAAAAoADAAAAAQACAAKAAAAMAAAAAQAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAD/////AAAAAP////+IAAAAFAAAAAAAAAAMABYABgAFAAgADAAMAAAAAAMEABgAAAAQAAAAAAAAAAAACgAYAAwABAAIAAoAAAA8AAAAEAAAAAEAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAABAAAAAQAAAAAAAAAAAAAAAAAAAJABAAAAAAAAAAAAAAAAAAA='

        assert len(errors) == 0
        # Skip this assert for now, requires further investigation: https://github.com/Azure/azure-sdk-for-python/issues/24690
        # assert query_result == expected_result
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_input_in_arrow_format(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)

        # upload the json file
        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = [ArrowDialect(ArrowType.DECIMAL, name="abc", precision=4, scale=2)]

        with pytest.raises(ValueError):
            blob_client.query_blob(
                "SELECT * from BlobStorage",
                on_error=on_error,
                blob_format=input_format)

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_input_in_parquet_format(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)
        expression = "select * from blobstorage where id < 1;"
        expected_data = b"0,mdifjt55.ea3,mdifjt55.ea3\n"

        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        parquet_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./resources/parquet.parquet"))
        with open(parquet_path, "rb") as parquet_data:
            blob_client.upload_blob(parquet_data, overwrite=True)

        reader = blob_client.query_blob(expression, blob_format=QuickQueryDialect.Parquet)
        real_data = reader.readall()

        assert real_data == expected_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_quick_query_output_in_parquet_format(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key)
        self._setup(bsc)
        expression = "SELECT * from BlobStorage"

        blob_name = self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        parquet_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./resources/parquet.parquet"))
        with open(parquet_path, "rb") as parquet_data:
            blob_client.upload_blob(parquet_data, overwrite=True)

        with pytest.raises(ValueError):
            blob_client.query_blob(
                expression, blob_format="ParquetDialect", output_format="ParquetDialect")

# ------------------------------------------------------------------------------
