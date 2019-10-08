# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import base64
import os
import unittest

from azure.core.exceptions import HttpResponseError

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    StorageErrorCode,
    BlobProperties
)
from testcase import (
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

        url = self._get_account_url()
        credential = self._get_shared_key_credential()

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            url,
            credential=credential,
            max_single_get_size=32 * 1024,
            max_chunk_get_size=4 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            container = self.bsc.get_container_client(self.container_name)
            container.create_container()

        self.byte_blob = self.get_resource_name('byteblob')
        self.byte_data = self.get_random_bytes(64 * 1024 + 5)

        if not self.is_playback():
            blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
            blob.upload_blob(self.byte_data)

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

        def seekable(self):
            return False

    # -- Get test cases for blobs ----------------------------------------------

    @record
    def test_unicode_get_blob_unicode_data(self):
        # Arrange
        blob_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Act
        content = blob.download_blob()

        # Assert
        self.assertIsInstance(content.properties, BlobProperties)
        self.assertEqual(content.content_as_bytes(), blob_data)

    @record
    def test_unicode_get_blob_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(binary_data)

        # Act
        content = blob.download_blob()

        # Assert
        self.assertIsInstance(content.properties, BlobProperties)
        self.assertEqual(content.content_as_bytes(), binary_data)

    @record
    def test_get_blob_no_content(self):
        # Arrange
        blob_data = b''
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Act
        content = blob.download_blob()

        # Assert
        self.assertEqual(blob_data, content.content_as_bytes())
        self.assertEqual(0, content.properties.size)

    def test_get_blob_to_bytes(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        content = blob.download_blob().content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(self.byte_data, content)

    def test_ranged_get_blob_to_bytes_with_single_byte(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        content = blob.download_blob(offset=0, length=1).content_as_bytes()

        # Assert
        self.assertEqual(1, len(content))
        self.assertEqual(self.byte_data[0], content[0])

        # Act
        content = blob.download_blob(offset=5, length=1).content_as_bytes()

        # Assert
        self.assertEqual(1, len(content))
        self.assertEqual(self.byte_data[5], content[0])

    @record
    def test_ranged_get_blob_to_bytes_with_zero_byte(self):
        blob_data = b''
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Act
        # the get request should fail in this case since the blob is empty and yet there is a range specified
        with self.assertRaises(HttpResponseError) as e:
            blob.download_blob(offset=0, length=5)
        self.assertEqual(StorageErrorCode.invalid_range, e.exception.error_code)

        with self.assertRaises(HttpResponseError) as e:
            blob.download_blob(offset=3, length=5)
        self.assertEqual(StorageErrorCode.invalid_range, e.exception.error_code)

    @record
    def test_ranged_get_blob_with_missing_start_range(self):
        blob_data = b'foobar'
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Act
        # the get request should fail fast in this case since start_range is missing while end_range is specified
        with self.assertRaises(ValueError):
            blob.download_blob(length=3)

    def test_get_blob_to_bytes_snapshot(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        snapshot_ref = blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(self.container_name, self.byte_blob, snapshot=snapshot_ref)
        
        blob.upload_blob(self.byte_data, overwrite=True) # Modify the blob so the Etag no longer matches

        # Act
        content = snapshot.download_blob().content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(self.byte_data, content)

    def test_get_blob_to_bytes_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(self.byte_data, content)
        self.assert_download_progress(
            len(self.byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_bytes_non_parallel(self):
        # Arrange
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_bytes(max_concurrency=1)

        # Assert
        self.assertEqual(self.byte_data, content)
        self.assert_download_progress(
            len(self.byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_bytes_small(self):
        # Arrange
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_bytes()

        # Assert
        self.assertEqual(blob_data, content)
        self.assert_download_progress(
            len(blob_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    def test_get_blob_to_stream(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob()
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_blob_to_stream_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(raw_response_hook=callback)
            properties = downloader.download_to_stream(stream, max_concurrency=2)
        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_stream_non_parallel(self):
        # Arrange
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(raw_response_hook=callback)
            properties = downloader.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_stream_small(self):
        # Arrange
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))


        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(raw_response_hook=callback)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(blob_data, actual)
        self.assert_download_progress(
            len(blob_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    def test_ranged_get_blob_to_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        end_range = self.config.max_single_get_size
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=1, length=end_range - 1)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:end_range], actual)

    def test_ranged_get_blob_to_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        start_range = 3
        end_range = self.config.max_single_get_size + 1024
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=start_range, length=end_range, raw_response_hook=callback)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[start_range:end_range + start_range], actual)
        self.assert_download_progress(
            end_range,
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_ranged_get_blob_to_path_small(self):
        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=1, length=4)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:5], actual)

    @record
    def test_ranged_get_blob_to_path_non_parallel(self):
        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=1, length=3)
            properties = downloader.download_to_stream(stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:4], actual)

    @record
    def test_ranged_get_blob_to_path_invalid_range_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_size = self.config.max_single_get_size + 1
        blob_data = self.get_random_bytes(blob_size)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Act
        end_range = 2 * self.config.max_single_get_size
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=1, length=end_range)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
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
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        # Act
        end_range = 2 * self.config.max_single_get_size
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=1, length=end_range)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(blob_data[1:blob_size], actual)

            # Assert

    def test_get_blob_to_text(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        text_blob = self.get_resource_name('textblob')
        text_data = self.get_random_text_data(self.config.max_single_get_size + 1)
        blob = self.bsc.get_blob_client(self.container_name, text_blob)
        blob.upload_blob(text_data)

        # Act
        content = blob.download_blob().content_as_text(max_concurrency=2)

        # Assert
        self.assertEqual(text_data, content)

    def test_get_blob_to_text_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        text_blob = self.get_resource_name('textblob')
        text_data = self.get_random_text_data(self.config.max_single_get_size + 1)
        blob = self.bsc.get_blob_client(self.container_name, text_blob)
        blob.upload_blob(text_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_text(max_concurrency=2)

        # Assert
        self.assertEqual(text_data, content)
        self.assert_download_progress(
            len(text_data.encode('utf-8')),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_text_non_parallel(self):
        # Arrange
        text_blob = self._get_blob_reference()
        text_data = self.get_random_text_data(self.config.max_single_get_size + 1)
        blob = self.bsc.get_blob_client(self.container_name, text_blob)
        blob.upload_blob(text_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_text(max_concurrency=1)

        # Assert
        self.assertEqual(text_data, content)
        self.assert_download_progress(
            len(text_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_text_small(self):
        # Arrange
        blob_data = self.get_random_text_data(1024)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(blob_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_text()

        # Assert
        self.assertEqual(blob_data, content)
        self.assert_download_progress(
            len(blob_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_to_text_with_encoding(self):
        # Arrange
        text = u'hello 啊齄丂狛狜 world'
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(text, encoding='utf-16')

        # Act
        content = blob.download_blob().content_as_text(encoding='utf-16')

        # Assert
        self.assertEqual(text, content)

    @record
    def test_get_blob_to_text_with_encoding_and_progress(self):
        # Arrange
        text = u'hello 啊齄丂狛狜 world'
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(text, encoding='utf-16')

        # Act
        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        content = blob.download_blob(raw_response_hook=callback).content_as_text(encoding='utf-16')

        # Assert
        self.assertEqual(text, content)
        self.assert_download_progress(
            len(text.encode('utf-8')),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_non_seekable(self):
        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetBlobTest.NonSeekableFile(stream)
            downloader = blob.download_blob()
            properties = downloader.download_to_stream(non_seekable_stream, max_concurrency=1)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_blob_non_seekable_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetBlobTest.NonSeekableFile(stream)

            with self.assertRaises(ValueError):
                downloader = blob.download_blob()
                properties = downloader.download_to_stream(non_seekable_stream, max_concurrency=2)

    @record
    def test_get_blob_to_stream_exact_get_size(self):
        # Arrange
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(self.config.max_single_get_size)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(byte_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(raw_response_hook=callback)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(byte_data, actual)
        self.assert_download_progress(
            len(byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @record
    def test_get_blob_exact_get_size(self):
        # Arrange
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(self.config.max_single_get_size)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(byte_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_bytes()

        # Assert
        self.assertEqual(byte_data, content)
        self.assert_download_progress(
            len(byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    def test_get_blob_exact_chunk_size(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(
            self.config.max_single_get_size + 
            self.config.max_chunk_get_size)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(byte_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = blob.download_blob(raw_response_hook=callback).content_as_bytes()

        # Assert
        self.assertEqual(byte_data, content)
        self.assert_download_progress(
            len(byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    def test_get_blob_to_stream_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(validate_content=True)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_blob_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        content = blob.download_blob(validate_content=True).content_as_bytes(max_concurrency=2)

        # Assert
        self.assertEqual(self.byte_data, content)

    def test_get_blob_range_to_stream_with_overall_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        props = blob.get_blob_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        blob.set_http_headers(props.content_settings)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            downloader = blob.download_blob(offset=0, length=1024, validate_content=True)
            properties = downloader.download_to_stream(stream, max_concurrency=2)

        # Assert
        self.assertEqual(len(downloader), 1024)
        self.assertIsInstance(properties, BlobProperties)
        self.assertEqual(b'MDAwMDAwMDA=', properties.content_settings.content_md5)

    def test_get_blob_range_with_overall_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        content = blob.download_blob(offset=0, length=1024, validate_content=True)

        # Arrange
        props = blob.get_blob_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        blob.set_http_headers(props.content_settings)

        # Act
        content = blob.download_blob(offset=0, length=1024, validate_content=True)

        # Assert
        self.assertEqual(content.properties.size, 1024)
        self.assertEqual(b'MDAwMDAwMDA=', content.properties.content_settings.content_md5)

    def test_get_blob_range_with_range_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        content = blob.download_blob(offset=0, length=1024, validate_content=True)

        # Arrange
        props = blob.get_blob_properties()
        props.content_settings.content_md5 = None
        blob.set_http_headers(props.content_settings)

        # Act
        content = blob.download_blob(offset=0, length=1024, validate_content=True)

        # Assert
        self.assertIsNotNone(content.properties.content_settings.content_type)
        self.assertIsNone(content.properties.content_settings.content_md5)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
