# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

import os
import unittest

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType,
    SharedKeyCredentials,
)
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_input.temp.dat'
LARGE_BLOB_SIZE = 64 * 1024
#------------------------------------------------------------------------------

class StorageAppendBlobTest(StorageTestCase):

    def setUp(self):
        super(StorageAppendBlobTest, self).setUp()

        url = self._get_account_url()
        self.config = BlobServiceClient.create_configuration()
        self.config.blob_settings.max_block_size = 4 * 1024
        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())

        self.bsc = BlobServiceClient(url, credentials=credentials, configuration=self.config)
        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            container = self.bsc.get_container_client(self.container_name)
            container.create_container()


    def tearDown(self):
        if not self.is_playback():
            try:
                container = self.bsc.get_container_client(self.container_name)
                container.delete_container()
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageAppendBlobTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(
            self.container_name,
            blob_name,
            blob_type=BlobType.AppendBlob)
        blob.create_blob()
        return blob

    def assertBlobEqual(self, blob, expected_data):
        stream = blob.download_blob()
        actual_data = b"".join(list(stream))
        self.assertEqual(actual_data, expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for block blobs --------------------------------------------

    @record
    def test_create_blob(self):
        # Arrange
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, blob_type=BlobType.AppendBlob)
        create_resp = blob.create_blob()

        # Assert
        blob_properties = blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('ETag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('Last-Modified'))

    @record
    def test_create_blob_with_lease_id(self):
        # Arrange
        blob = self._create_blob()

        # Act
        lease = blob.acquire_lease()
        create_resp = blob.create_blob(lease=lease)

        # Assert
        blob_properties = blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('ETag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('Last-Modified'))

    @record
    def test_create_blob_with_metadata(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name, blob_type=BlobType.AppendBlob)

        # Act
        blob.create_blob(metadata=metadata)

        # Assert
        md = blob.get_blob_metadata()
        self.assertDictEqual(md, metadata)

    @record
    def test_append_block(self):
        # Arrange
        blob = self._create_blob()

        # Act
        for i in range(5):
            resp = blob.append_block(u'block {0}'.format(i).encode('utf-8'))
            self.assertEqual(int(resp['x-ms-blob-append-offset']), 7 * i)
            self.assertEqual(resp['x-ms-blob-committed-block-count'], i + 1)
            self.assertIsNotNone(resp['ETag'])
            self.assertIsNotNone(resp['Last-Modified'])

        # Assert
        self.assertBlobEqual(blob, b'block 0block 1block 2block 3block 4')

    @record
    def test_append_block_unicode(self):
        # Arrange
        blob = self._create_blob()

        # Act
        resp = blob.append_block(u'啊齄丂狛狜', encoding='utf-16')
        self.assertEqual(int(resp['x-ms-blob-append-offset']), 0)
        self.assertEqual(resp['x-ms-blob-committed-block-count'], 1)
        self.assertIsNotNone(resp['ETag'])
        self.assertIsNotNone(resp['Last-Modified'])

        # Assert

    @record
    def test_append_block_with_md5(self):
        # Arrange
        blob = self._create_blob()

        # Act
        resp = blob.append_block(b'block', validate_content=True)
        self.assertEqual(int(resp['x-ms-blob-append-offset']), 0)
        self.assertEqual(resp['x-ms-blob-committed-block-count'], 1)
        self.assertIsNotNone(resp['ETag'])
        self.assertIsNotNone(resp['Last-Modified'])

        # Assert

    @record
    def test_append_blob_from_bytes(self):
        # Arrange
        blob = self._create_blob()

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        append_resp = blob.upload_blob(data)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp['ETag'])
        self.assertEqual(blob_properties.last_modified, append_resp['Last-Modified'])

    @record
    def test_append_blob_from_0_bytes(self):
        # Arrange
        blob = self._create_blob()

        # Act
        data = b''
        append_resp = blob.upload_blob(data)

        # Assert
        self.assertBlobEqual(blob, data)
        # appending nothing should not make any network call
        self.assertIsNone(append_resp.get('ETag'))
        self.assertIsNone(append_resp.get('Last-Modified'))

    @record
    def test_append_blob_from_bytes_with_progress(self):
        # Arrange
        blob = self._create_blob()
        data = b'abcdefghijklmnopqrstuvwxyz'

        # Act
        progress = []

        def progress_gen(upload):
            progress.append((0, len(upload)))
            yield upload
    
        upload_data = progress_gen(data)
        blob.upload_blob(upload_data)

        # Assert
        self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.blob_settings.max_block_size, progress)

    @record
    def test_append_blob_from_bytes_with_index(self):
        # Arrange
        blob = self._create_blob()

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        blob.upload_blob(data[3:])

        # Assert
        self.assertBlobEqual(blob, data[3:])

    @record
    def test_append_blob_from_bytes_with_index_and_count(self):
        # Arrange
        blob = self._create_blob()

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        blob.upload_blob(data[3:], length=5)

        # Assert
        self.assertBlobEqual(blob, data[3:8])

    @record
    def test_append_blob_from_bytes_chunked_upload(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        append_resp = blob.upload_blob(data)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp['ETag'])
        self.assertEqual(blob_properties.last_modified, append_resp.get('Last-Modified'))

    @record
    def test_append_blob_from_bytes_with_progress_chunked_upload(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []

        def progress_gen(upload):
            n = self.config.blob_settings.max_block_size
            total = len(upload)
            current = 0
            while upload:
                progress.append((current, total))
                yield upload[:n]
                current += len(upload[:n])
                upload = upload[n:]

        upload_data = progress_gen(data)
        blob.upload_blob(upload_data)

        # Assert
        self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.blob_settings.max_block_size, progress)

    @record
    def test_append_blob_from_bytes_chunked_upload_with_index_and_count(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 33
        blob_size = len(data) - 66

        # Act
        blob.upload_blob(data[index:], length=blob_size)

        # Assert
        self.assertBlobEqual(blob, data[index:index + blob_size])

    @record
    def test_append_blob_from_path_chunked_upload(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            append_resp = blob.upload_blob(stream)

        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('ETag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('Last-Modified'))

    @record
    def test_append_blob_from_path_with_progress_chunked_upload(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def progress_gen(upload):
            n = self.config.blob_settings.max_block_size
            total = LARGE_BLOB_SIZE
            current = 0
            while upload:
                chunk = upload.read(n)
                if not chunk:
                    break
                progress.append((current, total))
                yield chunk
                current += len(chunk)

        with open(FILE_PATH, 'rb') as stream:
            upload_data = progress_gen(stream)
            blob.upload_blob(upload_data)

        # Assert
        self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.blob_settings.max_block_size, progress)

    @record
    def test_append_blob_from_stream_chunked_upload(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            append_resp = blob.upload_blob(stream)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('ETag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('Last-Modified'))

    @record
    def test_append_blob_from_stream_non_seekable_chunked_upload_known_size(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_size = len(data) - 66

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageAppendBlobTest.NonSeekableFile(stream)
            blob.upload_blob(non_seekable_file, length=blob_size)

        # Assert
        self.assertBlobEqual(blob, data[:blob_size])

    @record
    def test_append_blob_from_stream_non_seekable_chunked_upload_unknown_size(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageAppendBlobTest.NonSeekableFile(stream)
            blob.upload_blob(non_seekable_file)

        # Assert
        self.assertBlobEqual(blob, data)

    @record
    def test_append_blob_from_stream_with_multiple_appends(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream1:
            stream1.write(data)
        with open(FILE_PATH, 'wb') as stream2:
            stream2.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream1:
            blob.upload_blob(stream1)
        with open(FILE_PATH, 'rb') as stream2:
            blob.upload_blob(stream2)

        # Assert
        data = data * 2
        self.assertBlobEqual(blob, data)

    @record
    def test_append_blob_from_stream_chunked_upload_with_count(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, blob_size)

        # Assert
        self.assertBlobEqual(blob, data[:blob_size])

    def test_append_blob_from_stream_chunked_upload_with_count_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            append_resp = blob.upload_blob(stream, length=blob_size)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data[:blob_size])
        self.assertEqual(blob_properties.etag, append_resp.get('ETag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('Last-Modified'))

    @record
    def test_append_blob_from_text(self):
        # Arrange
        blob = self._create_blob()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        append_resp = blob.upload_blob(text)
        blob_properties = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('ETag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('Last-Modified'))

    @record
    def test_append_blob_from_text_with_encoding(self):
        # Arrange
        blob = self._create_blob()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        blob.upload_blob(text, encoding='utf-16')

        # Assert
        self.assertBlobEqual(blob, data)

    @record
    def test_append_blob_from_text_with_encoding_and_progress(self):
        # Arrange
        blob = self._create_blob()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []

        def progress_gen(upload):
            progress.append((0, len(data)))
            yield upload

        upload_data = progress_gen(text)
        blob.upload_blob(upload_data, encoding='utf-16')

        # Assert
        self.assert_upload_progress(len(data), self.config.blob_settings.max_block_size, progress)

    @record
    def test_append_blob_from_text_chunked_upload(self):
        # Arrange
        blob = self._create_blob()
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        blob.upload_blob(data)

        # Assert
        self.assertBlobEqual(blob, encoded_data)

    @record
    def test_append_blob_with_md5(self):
        # Arrange
        blob = self._create_blob()
        data = b'hello world'

        # Act
        blob.append_block(data, validate_content=True)

        # Assert

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
