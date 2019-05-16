# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

pytestmark = pytest.mark.skip

import os
import unittest

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    #ContentSettings,  # TODO
)

if os.sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tests.testcase import (
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


class StorageLargeBlockBlobTest(StorageTestCase):
    def setUp(self):
        super(StorageLargeBlockBlobTest, self).setUp()

        self.bs = self._create_storage_service(BlockBlobService, self.settings)

        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bs.MAX_BLOCK_SIZE = 2 * 1024 * 1024
        self.bs.MIN_LARGE_BLOCK_UPLOAD_THRESHOLD = 1 * 1024 * 1024
        self.bs.MAX_SINGLE_PUT_SIZE = 32 * 1024

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bs.delete_container(self.container_name)
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
        self.bs.create_blob_from_bytes(self.container_name, blob_name, b'')
        return blob_name

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        actual_data = self.bs.get_blob_to_bytes(container_name, blob_name)
        self.assertEqual(actual_data.content, expected_data)

    # --Test cases for block blobs --------------------------------------------

    def test_put_block_bytes_large(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_blob()

        # Act
        for i in range(5):
            resp = self.bs.put_block(self.container_name,
                                     blob_name,
                                     os.urandom(LARGE_BLOCK_SIZE),
                                     'block {0}'.format(i).encode('utf-8'),)
            self.assertIsNone(resp)

            # Assert

    def test_put_block_bytes_large_with_md5(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_blob()

        # Act
        for i in range(5):
            resp = self.bs.put_block(self.container_name,
                                     blob_name,
                                     os.urandom(LARGE_BLOCK_SIZE),
                                     'block {0}'.format(i).encode('utf-8'),
                                     validate_content=True)
            self.assertIsNone(resp)

    def test_put_block_stream_large(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = self.bs.put_block(self.container_name,
                                     blob_name,
                                     stream,
                                     'block {0}'.format(i).encode('utf-8'),)
            self.assertIsNone(resp)

            # Assert

    def test_put_block_stream_large_with_md5(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = self.bs.put_block(self.container_name,
                                     blob_name,
                                     stream,
                                     'block {0}'.format(i).encode('utf-8'),
                                     validate_content=True)
            self.assertIsNone(resp)

        # Assert

    def test_create_large_blob_from_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_path_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH, validate_content=True)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_path_non_parallel(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(self.get_random_bytes(100))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH, max_connections=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH,
                                      progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_BLOCK_SIZE, progress)

    def test_create_large_blob_from_path_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_large_blob_from_stream_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_large_blob_from_stream_with_progress_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream, progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_BLOCK_SIZE, progress, unknown_size=True)

    def test_create_large_blob_from_stream_chunked_upload_with_count(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            resp = self.bs.create_blob_from_stream(self.container_name, blob_name, stream, blob_size)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_create_large_blob_from_stream_chunked_upload_with_count_and_properties(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream,
                                            blob_size, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_large_blob_from_stream_chunked_upload_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream,
                                            content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

# ------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
