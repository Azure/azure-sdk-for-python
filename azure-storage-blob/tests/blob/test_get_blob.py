# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

pytestmark = pytest.mark.xfail
import base64
import os
import unittest

from azure.common import AzureHttpError

from azure.storage.blob import (
    #Blob,  # TODO
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_output.temp.dat'


# ------------------------------------------------------------------------------

class StorageGetBlobTest(StorageTestCase):
    def setUp(self):
        super(StorageGetBlobTest, self).setUp()

        self.bs = self._create_storage_service(BlockBlobService, self.settings)

        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

        self.byte_blob = self.get_resource_name('byteblob')
        self.byte_data = self.get_random_bytes(64 * 1024 + 5)

        if not self.is_playback():
            self.bs.create_blob_from_bytes(self.container_name, self.byte_blob, self.byte_data)

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bs.MAX_SINGLE_GET_SIZE = 32 * 1024
        self.bs.MAX_CHUNK_GET_SIZE = 4 * 1024

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

        return super(StorageGetBlobTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # -- Get test cases for blobs ----------------------------------------------

    @record
    def test_unicode_get_blob_unicode_data(self):
        # Arrange
        blob_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, blob_data)

    @record
    def test_unicode_get_blob_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, binary_data)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertIsInstance(blob, Blob)
        self.assertEqual(blob.content, binary_data)

    @record
    def test_get_blob_no_content(self):
        # Arrange
        blob_data = b''
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)

        # Assert
        self.assertEqual(blob_data, blob.content)
        self.assertEqual(0, blob.properties.content_length)

    def test_get_blob_to_bytes(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob)

        # Assert
        self.assertEqual(self.byte_data, blob.content)

    def test_ranged_get_blob_to_bytes_with_single_byte(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=0, end_range=0)

        # Assert
        self.assertEqual(1, len(blob.content))
        self.assertEqual(self.byte_data[0], blob.content[0])

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=5, end_range=5)

        # Assert
        self.assertEqual(1, len(blob.content))
        self.assertEqual(self.byte_data[5], blob.content[0])

    @record
    def test_ranged_get_blob_to_bytes_with_zero_byte(self):
        blob_data = b''
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        # Act
        # the get request should fail in this case since the blob is empty and yet there is a range specified
        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, blob_name, start_range=0, end_range=5)

        with self.assertRaises(AzureHttpError):
            self.bs.get_blob_to_bytes(self.container_name, blob_name, start_range=3, end_range=5)

    @record
    def test_ranged_get_blob_with_missing_start_range(self):
        blob_data = b'foobar'
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        # Act
        # the get request should fail fast in this case since start_range is missing while end_range is specified
        with self.assertRaises(ValueError):
            self.bs.get_blob_to_bytes(self.container_name, blob_name, end_range=3)

    def test_get_blob_to_bytes_snapshot(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        snapshot = self.bs.snapshot_blob(self.container_name, self.byte_blob)
        self.bs.create_blob_from_bytes(self.container_name, self.byte_blob, self.byte_data) # Modify the blob so the Etag no longer matches

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, snapshot.snapshot)

        # Assert
        self.assertEqual(self.byte_data, blob.content)

    def test_get_blob_to_bytes_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, progress_callback=callback)

        # Assert
        self.assertEqual(self.byte_data, blob.content)
        self.assert_download_progress(len(self.byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_bytes_non_parallel(self):
        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, max_connections=1,
                                         progress_callback=callback)

        # Assert
        self.assertEqual(self.byte_data, blob.content)
        self.assert_download_progress(len(self.byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_bytes_small(self):
        # Arrange
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(blob_data, blob.content)
        self.assert_download_progress(len(blob_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_blob_to_stream(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        with open(FILE_PATH, 'wb') as stream:
            blob = self.bs.get_blob_to_stream(self.container_name, self.byte_blob, stream)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_blob_to_stream_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            blob = self.bs.get_blob_to_stream(
                self.container_name, self.byte_blob, stream, progress_callback=callback)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_stream_non_parallel(self):
        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            blob = self.bs.get_blob_to_stream(
                self.container_name, self.byte_blob, stream, max_connections=1, progress_callback=callback)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_stream_small(self):
        # Arrange
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            blob = self.bs.get_blob_to_stream(self.container_name, blob_name, stream,
                                              progress_callback=callback)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(blob_data, actual)
        self.assert_download_progress(len(blob_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_blob_to_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        blob = self.bs.get_blob_to_path(self.container_name, self.byte_blob, FILE_PATH)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_blob_to_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_path(
            self.container_name, self.byte_blob, FILE_PATH, progress_callback=callback)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_path_non_parallel(self):
        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_path(
            self.container_name, self.byte_blob, FILE_PATH,
            progress_callback=callback, max_connections=1)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_path_small(self):
        # Arrange
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_path(self.container_name, blob_name, FILE_PATH,
                                        progress_callback=callback)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(blob_data, actual)
        self.assert_download_progress(len(blob_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    def test_ranged_get_blob_to_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        end_range = self.bs.MAX_SINGLE_GET_SIZE + 1024
        blob = self.bs.get_blob_to_path(self.container_name, self.byte_blob, FILE_PATH,
                                        start_range=1, end_range=end_range)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:end_range + 1], actual)

    def test_ranged_get_blob_to_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        start_range = 3
        end_range = self.bs.MAX_SINGLE_GET_SIZE + 1024
        blob = self.bs.get_blob_to_path(self.container_name, self.byte_blob, FILE_PATH,
                                        start_range=start_range, end_range=end_range,
                                        progress_callback=callback)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[start_range:end_range + 1], actual)
        self.assert_download_progress(end_range - start_range + 1, self.bs.MAX_CHUNK_GET_SIZE,
                                      self.bs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_ranged_get_blob_to_path_small(self):
        # Arrange

        # Act
        blob = self.bs.get_blob_to_path(self.container_name, self.byte_blob, FILE_PATH,
                                        start_range=1, end_range=4)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:5], actual)

    @record
    def test_ranged_get_blob_to_path_non_parallel(self):
        # Arrange

        # Act
        blob = self.bs.get_blob_to_path(self.container_name, self.byte_blob, FILE_PATH,
                                        start_range=1, end_range=3, max_connections=1)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:4], actual)

    @record
    def test_ranged_get_blob_to_path_invalid_range_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_size = self.bs.MAX_SINGLE_GET_SIZE + 1
        blob_data = self.get_random_bytes(blob_size)
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        # Act
        end_range = 2 * self.bs.MAX_SINGLE_GET_SIZE
        blob = self.bs.get_blob_to_path(self.container_name, blob_name, FILE_PATH,
                                        start_range=1, end_range=end_range)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(blob_data[1:blob_size], actual)

    @record
    def test_ranged_get_blob_to_path_invalid_range_non_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_size = 1024
        blob_data = self.get_random_bytes(blob_size)
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, blob_data)

        # Act
        end_range = 2 * self.bs.MAX_SINGLE_GET_SIZE
        blob = self.bs.get_blob_to_path(self.container_name, blob_name, FILE_PATH,
                                        start_range=1, end_range=end_range)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(blob_data[1:blob_size], actual)

            # Assert

    def test_get_blob_to_path_with_mode(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        with open(FILE_PATH, 'wb') as stream:
            stream.write(b'abcdef')

        # Act

        # Assert
        with self.assertRaises(BaseException):
            blob = self.bs.get_blob_to_path(self.container_name, self.byte_blob, FILE_PATH, 'a+b')

    def test_get_blob_to_path_with_mode_non_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        with open(FILE_PATH, 'wb') as stream:
            stream.write(b'abcdef')

        # Act
        blob = self.bs.get_blob_to_path(
            self.container_name, self.byte_blob, FILE_PATH, 'a+b', max_connections=1)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(b'abcdef' + self.byte_data, actual)

    def test_get_blob_to_text(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        text_blob = self.get_resource_name('textblob')
        text_data = self.get_random_text_data(self.bs.MAX_SINGLE_GET_SIZE + 1)
        self.bs.create_blob_from_text(self.container_name, text_blob, text_data)

        # Act
        blob = self.bs.get_blob_to_text(self.container_name, text_blob)

        # Assert
        self.assertEqual(text_data, blob.content)

    def test_get_blob_to_text_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        text_blob = self.get_resource_name('textblob')
        text_data = self.get_random_text_data(self.bs.MAX_SINGLE_GET_SIZE + 1)
        self.bs.create_blob_from_text(self.container_name, text_blob, text_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_text(self.container_name, text_blob, progress_callback=callback)

        # Assert
        self.assertEqual(text_data, blob.content)
        self.assert_download_progress(len(text_data.encode('utf-8')), self.bs.MAX_CHUNK_GET_SIZE,
                                      self.bs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_get_blob_to_text_non_parallel(self):
        # Arrange
        text_blob = self._get_blob_reference()
        text_data = self.get_random_text_data(self.bs.MAX_SINGLE_GET_SIZE + 1)
        self.bs.create_blob_from_text(self.container_name, text_blob, text_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_text(self.container_name, text_blob, max_connections=1, progress_callback=callback)

        # Assert
        self.assertEqual(text_data, blob.content)
        self.assert_download_progress(len(text_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_blob_to_text_small(self):
        # Arrange
        blob_data = self.get_random_text_data(1024)
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_text(self.container_name, blob_name, blob_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_text(self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(blob_data, blob.content)
        self.assert_download_progress(len(blob_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_get_blob_to_text_with_encoding(self):
        # Arrange
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data)

        # Act
        blob = self.bs.get_blob_to_text(self.container_name, blob_name, 'utf-16')

        # Assert
        self.assertEqual(text, blob.content)

    @record
    def test_get_blob_to_text_with_encoding_and_progress(self):
        # Arrange
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        blob = self.bs.get_blob_to_text(
            self.container_name, blob_name, 'utf-16', progress_callback=callback)

        # Assert
        self.assertEqual(text, blob.content)
        self.assert_download_progress(len(data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_get_blob_non_seekable(self):
        # Arrange

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetBlobTest.NonSeekableFile(stream)
            blob = self.bs.get_blob_to_stream(self.container_name, self.byte_blob, non_seekable_stream,
                                              max_connections=1)

        # Assert
        self.assertIsInstance(blob, Blob)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_blob_non_seekable_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetBlobTest.NonSeekableFile(stream)

            with self.assertRaises(BaseException):
                blob = self.bs.get_blob_to_stream(
                    self.container_name, self.byte_blob, non_seekable_stream)

                # Assert

    @record
    def test_get_blob_exact_get_size(self):
        # Arrange
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(self.bs.MAX_SINGLE_GET_SIZE)
        self.bs.create_blob_from_bytes(self.container_name, blob_name, byte_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(byte_data, blob.content)
        self.assert_download_progress(len(byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_blob_exact_chunk_size(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(self.bs.MAX_SINGLE_GET_SIZE + self.bs.MAX_CHUNK_GET_SIZE)
        self.bs.create_blob_from_bytes(self.container_name, blob_name, byte_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, progress_callback=callback)

        # Assert
        self.assertEqual(byte_data, blob.content)
        self.assert_download_progress(len(byte_data), self.bs.MAX_CHUNK_GET_SIZE, self.bs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_blob_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, validate_content=True)

        # Assert
        self.assertEqual(self.byte_data, blob.content)

    def test_get_blob_range_with_overall_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=0,
                                         end_range=1024, validate_content=True)

        # Arrange
        props = self.bs.get_blob_properties(self.container_name, self.byte_blob)
        props.properties.content_settings.content_md5 = 'MDAwMDAwMDA='
        self.bs.set_blob_properties(self.container_name, self.byte_blob, props.properties.content_settings)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=0,
                                         end_range=1024, validate_content=True)

        # Assert
        self.assertEqual('MDAwMDAwMDA=', blob.properties.content_settings.content_md5)

    def test_get_blob_range_with_range_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=0,
                                         end_range=1024, validate_content=True)

        # Arrange
        props = self.bs.get_blob_properties(self.container_name, self.byte_blob)
        props.properties.content_settings.content_md5 = None;
        self.bs.set_blob_properties(self.container_name, self.byte_blob, props.properties.content_settings)

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=0,
                                         end_range=1024, validate_content=True)

        # Assert
        self.assertTrue(hasattr(blob.properties.content_settings, "content_type"));
        self.assertFalse(hasattr(blob.properties.content_settings, "content_md5"));

        # Act
        blob = self.bs.get_blob_to_bytes(self.container_name, self.byte_blob, start_range=0,
                                         end_range=1024, validate_content=True)

        # Assert
        self.assertTrue(hasattr(blob.properties.content_settings, "content_type"));
        self.assertFalse(hasattr(blob.properties.content_settings, "content_md5"));


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
