# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import os
import unittest
import uuid

import pytest
from azure.core.exceptions import HttpResponseError

from azure.storage.fileshare import (
    ShareFileClient,
    ShareServiceClient,
    FileProperties
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import (
    StorageTestCase,
    LogCaptured,
    GlobalStorageAccountPreparer
)

# ------------------------------------------------------------------------------
TEST_FILE_PREFIX = 'file'
FILE_PATH = 'file_output.temp.{}.dat'.format(str(uuid.uuid4()))

# ------------------------------------------------------------------------------

class StorageGetFileTest(StorageTestCase):
    def _setup(self, storage_account, storage_account_key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.MAX_SINGLE_GET_SIZE = 32 * 1024
        self.MAX_CHUNK_GET_SIZE = 4 * 1024

        url = self.account_url(storage_account, "file")
        credential = storage_account_key

        self.fsc = ShareServiceClient(
            url, credential=credential,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        self.share_name = self.get_resource_name('utshare')
        self.directory_name = self.get_resource_name('utdir')

        if not self.is_playback():
            share = self.fsc.create_share(self.share_name)
            share.create_directory(self.directory_name)

        self.byte_file = self.get_resource_name('bytefile')
        self.byte_data = self.get_random_bytes(64 * 1024 + 5)

        if not self.is_playback():
            byte_file = self.directory_name + '/' + self.byte_file
            file_client = ShareFileClient(
                self.account_url(storage_account, "file"),
                share_name=self.share_name,
                file_path=byte_file,
                credential=credential
            )
            file_client.upload_file(self.byte_data)

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------

    def _get_file_reference(self):
        return self.get_resource_name(TEST_FILE_PREFIX)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)
    
        def seekable(self):
            return False

    # -- Get test cases for files ----------------------------------------------

    @GlobalStorageAccountPreparer()
    def test_unicode_get_file_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account, "file"),
                share_name=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=storage_account_key,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        file_content = file_client.download_file().readall()

        # Assert
        self.assertEqual(file_content, file_data)

    @GlobalStorageAccountPreparer()
    def test_unicode_get_file_binary_data(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account, "file"),
                share_name=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=storage_account_key,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(binary_data)

        # Act
        file_content = file_client.download_file().readall()

        # Assert
        self.assertEqual(file_content, binary_data)

    @GlobalStorageAccountPreparer()
    def test_get_file_no_content(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = b''
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account, "file"),
                share_name=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=storage_account_key,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        file_output = file_client.download_file()

        # Assert
        self.assertEqual(file_data, file_output.readall())
        self.assertEqual(0, file_output.properties.size)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_bytes(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = file_client.download_file(max_concurrency=2).readall()

        # Assert
        self.assertEqual(self.byte_data, file_content)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_bytes_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(raw_response_hook=callback, max_concurrency=2).readall()

        # Assert
        self.assertEqual(self.byte_data, file_content)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_bytes_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(raw_response_hook=callback).readall()

        # Assert
        self.assertEqual(self.byte_data, file_content)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_bytes_small(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(raw_response_hook=callback).readall()

        # Assert
        self.assertEqual(file_data, file_content)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_with_iter(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        chunk_size_list = list()
        with open(FILE_PATH, 'wb') as stream:
            for data in file_client.download_file().chunks():
                chunk_size_list.append(len(data))
                stream.write(data)

        for i in range(0, len(chunk_size_list) - 1):
            self.assertEqual(chunk_size_list[i], self.MAX_CHUNK_GET_SIZE)
        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(raw_response_hook=callback, max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_small(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = snapshot_client.download_file(max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_with_progress_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = snapshot_client.download_file(raw_response_hook=callback, max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_non_parallel_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = snapshot_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_stream_small_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key)
        file_client.upload_file(file_data)

        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = snapshot_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(offset=1, length=end_range, max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:end_range + 1], actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path_with_single_byte(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(offset=0, length=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(1, len(actual))
            self.assertEqual(self.byte_data[0], actual[0])
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_bytes_with_zero_byte(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = b''
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        # the get request should fail in this case since the blob is empty and yet there is a range specified
        with self.assertRaises(HttpResponseError):
            file_client.download_file(offset=0, length=5).readall()

        with self.assertRaises(HttpResponseError):
            file_client.download_file(offset=3, length=5).readall()

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        start_range = 3
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with open(FILE_PATH, 'wb') as stream:
            length = end_range - start_range + 1
            bytes_read = file_client.download_file(
                offset=start_range,
                length=length,
                raw_response_hook=callback,
                max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[start_range:end_range + 1], actual)
        self.assert_download_progress(
            end_range - start_range + 1,
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path_small(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(offset=1, length=4, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:5], actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            bytes_read = file_client.download_file(offset=1, length=3, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:4], actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path_invalid_range_parallel(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_size = self.MAX_SINGLE_GET_SIZE + 1
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        start = 3
        end_range = 2 * self.MAX_SINGLE_GET_SIZE
        with open(FILE_PATH, 'wb') as stream:
            length = end_range - start + 1
            bytes_read = file_client.download_file(offset=start, length=length, max_concurrency=2).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data[start:file_size], actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_ranged_get_file_to_path_invalid_range_non_parallel(self, resource_group, location, storage_account, storage_account_key):

        self._setup(storage_account, storage_account_key)
        file_size = 1024
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        start = 3
        end_range = 2 * self.MAX_SINGLE_GET_SIZE
        with open(FILE_PATH, 'wb') as stream:
            length = end_range - start + 1
            bytes_read = file_client.download_file(offset=start, length=length, max_concurrency=1).readinto(stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data[start:file_size], actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_text(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(text_data)

        # Act
        file_content = file_client.download_file(max_concurrency=2, encoding='utf-8').readall()

        # Assert
        self.assertEqual(text_data, file_content)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_text_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(text_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(
            raw_response_hook=callback, max_concurrency=2, encoding='utf-8').readall()

        # Assert
        self.assertEqual(text_data, file_content)
        self.assert_download_progress(
            len(text_data.encode('utf-8')),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_text_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        text_file = self._get_file_reference()
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(text_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(
            raw_response_hook=callback, max_concurrency=1, encoding='utf-8').readall()

        # Assert
        self.assertEqual(text_data, file_content)
        self.assert_download_progress(
            len(text_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_text_small(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_data = self.get_random_text_data(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(raw_response_hook=callback, encoding='utf-8').readall()

        # Assert
        self.assertEqual(file_data, file_content)
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_text_with_encoding(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(data)

        # Act
        file_content = file_client.download_file(encoding='UTF-16').readall()

        # Assert
        self.assertEqual(text, file_content)

    @GlobalStorageAccountPreparer()
    def test_get_file_to_text_with_encoding_and_progress(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        file_content = file_client.download_file(raw_response_hook=callback, encoding='UTF-16').readall()

        # Assert
        self.assertEqual(text, file_content)
        self.assert_download_progress(
            len(data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_non_seekable(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)
            bytes_read = file_client.download_file(max_concurrency=1).readinto(non_seekable_stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_non_seekable_parallel(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)

            with self.assertRaises(ValueError):
                file_client.download_file(max_concurrency=2).readinto(non_seekable_stream)

                # Assert
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_non_seekable_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)
            bytes_read = snapshot_client.download_file(max_concurrency=1).readinto(non_seekable_stream)

        # Assert
        self.assertIsInstance(bytes_read, int)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_non_seekable_parallel_from_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)

            with self.assertRaises(ValueError):
                snapshot_client.download_file(max_concurrency=2).readinto(non_seekable_stream)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_get_file_exact_get_size(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.MAX_SINGLE_GET_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(byte_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(raw_response_hook=callback)

        # Assert
        self.assertEqual(byte_data, file_content.readall())
        self.assert_download_progress(
            len(byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_exact_chunk_size(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.MAX_SINGLE_GET_SIZE + self.MAX_CHUNK_GET_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(byte_data)

        progress = []
        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        # Act
        file_content = file_client.download_file(raw_response_hook=callback, max_concurrency=2)

        # Assert
        self.assertEqual(byte_data, file_content.readall())
        self.assert_download_progress(
            len(byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @GlobalStorageAccountPreparer()
    def test_get_file_with_md5(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = file_client.download_file(validate_content=True)

        # Assert
        self.assertEqual(self.byte_data, file_content.readall())

    @GlobalStorageAccountPreparer()
    def test_get_file_range_with_md5(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        if not self.is_live:
            return
        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        file_content = file_client.download_file(offset=0, length=1024, validate_content=True)

        # Assert
        self.assertIsNone(file_content.properties.content_settings.content_md5)

        props = file_client.get_file_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        file_client.set_http_headers(props.content_settings)

        # Act
        file_content = file_client.download_file(offset=0, length=1024, validate_content=True)

        # Assert
        self.assertEqual(b'MDAwMDAwMDA=', file_content.properties.content_settings.content_md5)

    @GlobalStorageAccountPreparer()
    def test_get_file_server_encryption(self, resource_group, location, storage_account, storage_account_key):

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = file_client.download_file(offset=0, length=1024, validate_content=True)
    
        # Assert
        self.assertTrue(file_content.properties.server_encrypted)

    @GlobalStorageAccountPreparer()
    def test_get_file_properties_server_encryption(self, resource_group, location, storage_account, storage_account_key):

        self._setup(storage_account, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        props = file_client.get_file_properties()

        # Assert
        self.assertTrue(props.server_encrypted)


# ------------------------------------------------------------------------------
