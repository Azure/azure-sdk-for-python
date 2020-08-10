# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.storage.filedatalake import (
    DelimitedTextDialect,
    DelimitedJsonDialect,
    DataLakeFileQueryError
)

from testcase import (
    StorageTestCase,
    record,
    TestMode
)
# ------------------------------------------------------------------------------
from azure.storage.filedatalake import DataLakeServiceClient

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

DATALAKE_CSV_DATA = b'DataLakeStorage,Package,Version,RepoPath,MissingDocs\r\nApp Configuration,' \
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


class StorageQuickQueryTest(StorageTestCase):
    def setUp(self):
        super(StorageQuickQueryTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY, logging_enable=True)
        self.config = self.dsc._config
        self.filesystem_name = self.get_resource_name('utqqcontainer')

        if not self.is_playback():
            try:
                self.dsc.create_file_system(self.filesystem_name)
            except:
                pass

    def tearDown(self):
        if not self.is_playback():
            try:
                self.dsc.delete_file_system(self.filesystem_name)
            except:
                pass

        return super(StorageQuickQueryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_file_reference(self):
        return self.get_resource_name("csvfile")

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @record
    def test_quick_query_readall(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        reader = file_client.query_file("SELECT * from BlobStorage", on_error=on_error)
        data = reader.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(data, CSV_DATA.replace(b'\r\n', b'\n'))

    @record
    def test_quick_query_datalake_expression(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(DATALAKE_CSV_DATA, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        input_format = DelimitedTextDialect(has_header=True)
        reader = file_client.query_file("SELECT DataLakeStorage from DataLakeStorage", on_error=on_error,
                                        file_format=input_format)
        reader.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(reader), len(DATALAKE_CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)

    @record
    def test_quick_query_iter_records(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

        reader = file_client.query_file("SELECT * from BlobStorage")
        read_records = reader.records()

        # Assert first line has header
        data = next(read_records)
        self.assertEqual(data, b'Service,Package,Version,RepoPath,MissingDocs')

        for record in read_records:
            data += record

        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(data, CSV_DATA.replace(b'\r\n', b''))

    @record
    def test_quick_query_readall_with_encoding(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

        errors = []

        def on_error(error):
            errors.append(error)

        reader = file_client.query_file("SELECT * from BlobStorage", on_error=on_error, encoding='utf-8')
        data = reader.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(data, CSV_DATA.replace(b'\r\n', b'\n').decode('utf-8'))

    @record
    def test_quick_query_iter_records_with_encoding(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

        reader = file_client.query_file("SELECT * from BlobStorage", encoding='utf-8')
        data = ''
        for record in reader.records():
            data += record

        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(data, CSV_DATA.replace(b'\r\n', b'').decode('utf-8'))

    @record
    def test_quick_query_iter_records_with_headers(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

        input_format = DelimitedTextDialect(has_header=True)
        reader = file_client.query_file("SELECT * from BlobStorage", file_format=input_format)
        read_records = reader.records()

        # Assert first line does not include header
        data = next(read_records)
        self.assertEqual(data, b'App Configuration,azure-data-appconfiguration,1,appconfiguration,FALSE')

        for record in read_records:
            data += record

        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(data, CSV_DATA.replace(b'\r\n', b'')[44:])

    @record
    def test_quick_query_iter_records_with_progress(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

        reader = file_client.query_file("SELECT * from BlobStorage")
        data = b''
        progress = 0
        for record in reader.records():
            if record:
                data += record
                progress += len(record) + 2
        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(data, CSV_DATA.replace(b'\r\n', b''))
        self.assertEqual(progress, len(reader))

    @record
    def test_quick_query_readall_with_serialization_setting(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(resp), len(CSV_DATA))
        self.assertEqual(query_result, CONVERTED_CSV_DATA)

    @record
    def test_quick_query_iter_records_with_serialization_setting(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

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

        reader = file_client.query_file(
            "SELECT * from BlobStorage",
            file_format=input_format,
            output_format=output_format)
        data = []
        for record in reader.records():
            if record:
                data.append(record)

        self.assertEqual(len(reader), len(CSV_DATA))
        self.assertEqual(len(reader), reader._blob_query_reader._bytes_processed)
        self.assertEqual(len(data), 33)

    @record
    def test_quick_query_readall_with_fatal_error_handler(self):
        # Arrange
        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        self.assertEqual(len(errors), 1)
        self.assertEqual(len(resp), 43)
        self.assertEqual(query_result, b'')

    @record
    def test_quick_query_iter_records_with_fatal_error_handler(self):
        # Arrange
        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        data = []
        for record in resp.records():
            data.append(record)
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(resp), 43)
        self.assertEqual(data, [b''])

    @record
    def test_quick_query_readall_with_fatal_error_handler_raise(self):
        # Arrange
        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        with pytest.raises(Exception):
            query_result = resp.readall()

    @record
    def test_quick_query_iter_records_with_fatal_error_handler_raise(self):
        # Arrange
        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)

        with pytest.raises(Exception):
            for record in resp.records():
                print(record)

    @record
    def test_quick_query_readall_with_fatal_error_ignore(self):
        # Arrange
        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            file_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

    @record
    def test_quick_query_iter_records_with_fatal_error_ignore(self):
        # Arrange
        data1 = b'{name: owner}'
        data2 = b'{name2: owner2}'
        data3 = b'{version:0,begin:1601-01-01T00:00:00.000Z,intervalSecs:3600,status:Finalized,config:' \
                b'{version:0,configVersionEtag:0x8d75ef460eb1a12,numShards:1,recordsFormat:avro,formatSchemaVersion:3,' \
                b'shardDistFnVersion:1},chunkFilePaths:[$blobchangefeed/log/00/1601/01/01/0000/],storageDiagnostics:' \
                b'{version:0,lastModifiedTime:2019-11-01T17:53:18.861Z,' \
                b'data:{aid:d305317d-a006-0042-00dd-902bbb06fc56}}}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

        input_format = DelimitedJsonDialect()
        output_format = DelimitedTextDialect(
            delimiter=';',
            quotechar="'",
            lineterminator='.',
            escapechar='\\'
        )
        resp = file_client.query_file(
            "SELECT * from BlobStorage",
            file_format=input_format,
            output_format=output_format)

        for record in resp.records():
            print(record)

    @record
    def test_quick_query_readall_with_nonfatal_error_handler(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT RepoPath from BlobStorage",
            file_format=input_format,
            output_format=output_format,
            on_error=on_error)
        query_result = resp.readall()

        # the error is because that line only has one column
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(resp), len(CSV_DATA))
        self.assertTrue(len(query_result) > 0)

    @record
    def test_quick_query_iter_records_with_nonfatal_error_handler(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT RepoPath from BlobStorage",
            file_format=input_format,
            output_format=output_format,
            on_error=on_error)
        data = list(resp.records())

        # the error is because that line only has one column
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(resp), len(CSV_DATA))
        self.assertEqual(len(data), 32)

    @record
    def test_quick_query_readall_with_nonfatal_error_ignore(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT RepoPath from BlobStorage",
            file_format=input_format,
            output_format=output_format)
        query_result = resp.readall()
        self.assertEqual(len(resp), len(CSV_DATA))
        self.assertTrue(len(query_result) > 0)

    @record
    def test_quick_query_iter_records_with_nonfatal_error_ignore(self):
        # Arrange
        # upload the csv file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(CSV_DATA, overwrite=True)

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
        resp = file_client.query_file(
            "SELECT RepoPath from BlobStorage",
            file_format=input_format,
            output_format=output_format)
        data = list(resp.records())
        self.assertEqual(len(resp), len(CSV_DATA))
        self.assertEqual(len(data), 32)

    @record
    def test_quick_query_readall_with_json_serialization_setting(self):
        # Arrange
        data1 = b'{\"name\": \"owner\", \"id\": 1}'
        data2 = b'{\"name2\": \"owner2\"}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect(delimiter='\n')
        output_format = DelimitedJsonDialect(delimiter=';')

        resp = file_client.query_file(
            "SELECT name from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(resp), len(data))
        self.assertEqual(query_result, b'{"name":"owner"};{};{"name":"owner"};')

    @record
    def test_quick_query_iter_records_with_json_serialization_setting(self):
        # Arrange
        data1 = b'{\"name\": \"owner\", \"id\": 1}'
        data2 = b'{\"name2\": \"owner2\"}'
        data = data1 + b'\n' + data2 + b'\n' + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect(delimiter='\n')
        output_format = DelimitedJsonDialect(delimiter=';')

        resp = file_client.query_file(
            "SELECT name from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        listdata = list(resp.records())

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(resp), len(data))
        self.assertEqual(listdata, [b'{"name":"owner"}',b'{}',b'{"name":"owner"}', b''])

    @record
    def test_quick_query_with_only_input_json_serialization_setting(self):
        # Arrange
        data1 = b'{\"name\": \"owner\", \"id\": 1}'
        data2 = b'{\"name2\": \"owner2\"}'
        data = data1 + data2 + data1

        # upload the json file
        file_name = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.filesystem_name, file_name)
        file_client.upload_data(data, overwrite=True)

        errors = []
        def on_error(error):
            errors.append(error)

        input_format = DelimitedJsonDialect(delimiter='\n')
        output_format = None

        resp = file_client.query_file(
            "SELECT name from BlobStorage",
            on_error=on_error,
            file_format=input_format,
            output_format=output_format)
        query_result = resp.readall()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(resp), len(data))
        self.assertEqual(query_result, b'{"name":"owner"}\n{}\n{"name":"owner"}\n')

# ------------------------------------------------------------------------------
