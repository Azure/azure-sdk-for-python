# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

import os
import platform
import unittest

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    ContentSettings
)

if os.sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from testcase import (
    StorageTestCase,
    TestMode,
    record,
)

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'largeblob'
FILE_PATH = 'blob_large_input.temp.dat'
LARGE_BLOB_SIZE = 12 * 1024 * 1024
LARGE_BLOCK_SIZE = 6 * 1024 * 1024

# ------------------------------------------------------------------------------
if platform.python_implementation() == 'PyPy':
    pytest.skip("Skip tests for Pypy", allow_module_level=True)

class StorageLargeBlockBlobTest(StorageTestCase):
    def setUp(self):
        super(StorageLargeBlockBlobTest, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            url,
            credential=credential,
            max_single_put_size=32 * 1024,
            max_block_size=2 * 1024 * 1024,
            min_large_block_upload_threshold=1 * 1024 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bsc.create_container(self.container_name)


    def tearDown(self):
        if not self.is_playback():
            try:
                self.bsc.delete_container(self.container_name)
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageLargeBlockBlobTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'')
        return blob

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), expected_data)

    # --Test cases for block blobs --------------------------------------------

    def test_put_block_bytes_large(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self._create_blob()

        # Act
        for i in range(5):
            resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'), os.urandom(LARGE_BLOCK_SIZE))
            self.assertIsNone(resp)

            # Assert

    def test_put_block_bytes_large_with_md5(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self._create_blob()

        # Act
        for i in range(5):
            resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                os.urandom(LARGE_BLOCK_SIZE),
                validate_content=True)
            self.assertIsNone(resp)

    def test_put_block_stream_large(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE)
            self.assertIsNone(resp)

            # Assert

    def test_put_block_stream_large_with_md5(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE,
                validate_content=True)
            self.assertIsNone(resp)

        # Assert

    def test_create_large_blob_from_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_path_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, validate_content=True, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_path_non_parallel(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(self.get_random_bytes(100))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    def test_create_large_blob_from_path_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_large_blob_from_stream_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_stream_with_progress_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    def test_create_large_blob_from_stream_chunked_upload_with_count(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_create_large_blob_from_stream_chunked_upload_with_count_and_properties(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(
                stream, length=blob_size, content_settings=content_settings, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_large_blob_from_stream_chunked_upload_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

# ------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
