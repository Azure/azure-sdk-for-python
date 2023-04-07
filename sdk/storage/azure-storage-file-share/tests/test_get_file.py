# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import os
import tempfile
import uuid
from io import BytesIO

import pytest
from azure.core.exceptions import HttpResponseError, ResourceModifiedError
from azure.storage.fileshare import ShareFileClient, ShareServiceClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import FileSharePreparer
from test_helpers import ProgressTracker

# ------------------------------------------------------------------------------
TEST_FILE_PREFIX = 'file'
# ------------------------------------------------------------------------------


class TestStorageGetFile(StorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.MAX_SINGLE_GET_SIZE = 32 * 1024
        self.MAX_CHUNK_GET_SIZE = 4 * 1024

        url = self.account_url(storage_account_name, "file")
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
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=byte_file,
                credential=credential
            )
            file_client.upload_file(self.byte_data)

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

    @FileSharePreparer()
    @recorded_by_proxy
    def test_unicode_get_file_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=storage_account_key,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        file_content = file_client.download_file().readall()

        # Assert
        assert file_content == file_data

    @FileSharePreparer()
    @recorded_by_proxy
    def test_unicode_get_file_binary_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=storage_account_key,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(binary_data)

        # Act
        file_content = file_client.download_file().readall()

        # Assert
        assert file_content == binary_data

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_no_content(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = b''
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=self.directory_name + '/' + file_name,
                credential=storage_account_key,
                max_single_get_size=self.MAX_SINGLE_GET_SIZE,
                max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        file_output = file_client.download_file()

        # Assert
        assert file_data == file_output.readall()
        assert 0 == file_output.properties.size

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_bytes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = file_client.download_file(max_concurrency=2).readall()

        # Assert
        assert self.byte_data == file_content

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_bytes_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert self.byte_data == file_content
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_bytes_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert self.byte_data == file_content
        self.assert_download_progress(
            len(self.byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_bytes_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert file_data == file_content
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_download_file_modified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=38,
            max_chunk_get_size=38)
        data = b'hello world python storage test chunks' * 5
        file_client.upload_file(data)
        resp = file_client.download_file()
        chunks = resp.chunks()
        i = 0
        while i < 4:
            data += next(chunks)
            i += 1
        file_client.upload_file(data=data)
        with pytest.raises(ResourceModifiedError):
            data += next(chunks)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_with_iter(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        chunk_size_list = list()
        for i in range(0, len(chunk_size_list) - 1):
            assert chunk_size_list[i] == self.MAX_CHUNK_GET_SIZE

        with tempfile.TemporaryFile() as temp_file:
            for data in file_client.download_file().chunks():
                chunk_size_list.append(len(data))
                temp_file.write(data)

            # Assert
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_stream(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_stream_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(raw_response_hook=callback, max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual
        self.assert_download_progress(len(self.byte_data), self.MAX_CHUNK_GET_SIZE, self.MAX_SINGLE_GET_SIZE, progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_stream_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual
        self.assert_download_progress(len(self.byte_data), self.MAX_CHUNK_GET_SIZE, self.MAX_SINGLE_GET_SIZE, progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_stream_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert file_data == actual
        self.assert_download_progress(len(file_data), self.MAX_CHUNK_GET_SIZE, self.MAX_SINGLE_GET_SIZE, progress)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_stream_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = snapshot_client.download_file(max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_stream_with_progress_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = snapshot_client.download_file(raw_response_hook=callback, max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual
        self.assert_download_progress(len(self.byte_data), self.MAX_CHUNK_GET_SIZE, self.MAX_SINGLE_GET_SIZE, progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_stream_non_parallel_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = snapshot_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual
        self.assert_download_progress(len(self.byte_data), self.MAX_CHUNK_GET_SIZE, self.MAX_SINGLE_GET_SIZE, progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_stream_small_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key)
        file_client.upload_file(file_data)

        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = snapshot_client.download_file(raw_response_hook=callback, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert file_data == actual
        self.assert_download_progress(len(file_data), self.MAX_CHUNK_GET_SIZE, self.MAX_SINGLE_GET_SIZE, progress)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_ranged_get_file_to_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(offset=1, length=end_range, max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[1:end_range + 1] == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_ranged_get_file_to_path_with_single_byte(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        end_range = self.MAX_SINGLE_GET_SIZE + 1024
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(offset=0, length=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert 1 == len(actual)
            assert self.byte_data[0] == actual[0]

    @FileSharePreparer()
    @recorded_by_proxy
    def test_ranged_get_file_to_bytes_with_zero_byte(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = b''
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        # the get request should fail in this case since the blob is empty and yet there is a range specified
        with pytest.raises(HttpResponseError):
            file_client.download_file(offset=0, length=5).readall()

        with pytest.raises(HttpResponseError):
            file_client.download_file(offset=3, length=5).readall()

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_ranged_get_file_to_path_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        with tempfile.TemporaryFile() as temp_file:
            length = end_range - start_range + 1
            bytes_read = file_client.download_file(
                offset=start_range,
                length=length,
                raw_response_hook=callback,
                max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[start_range:end_range + 1] == actual
        self.assert_download_progress(
            end_range - start_range + 1,
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_ranged_get_file_to_path_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(offset=1, length=4, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[1:5] == actual

    @FileSharePreparer()
    @recorded_by_proxy
    def test_ranged_get_file_to_path_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            bytes_read = file_client.download_file(offset=1, length=3, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[1:4] == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_ranged_get_file_to_path_invalid_range_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_size = self.MAX_SINGLE_GET_SIZE + 1
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        start = 3
        end_range = 2 * self.MAX_SINGLE_GET_SIZE
        with tempfile.TemporaryFile() as temp_file:
            length = end_range - start + 1
            bytes_read = file_client.download_file(offset=start, length=length, max_concurrency=2).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert file_data[start:file_size] == actual

    @FileSharePreparer()
    @recorded_by_proxy
    def test_ranged_get_file_to_path_invalid_range_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        self._setup(storage_account_name, storage_account_key)
        file_size = 1024
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(file_data)

        # Act
        start = 3
        end_range = 2 * self.MAX_SINGLE_GET_SIZE
        with tempfile.TemporaryFile() as temp_file:
            length = end_range - start + 1
            bytes_read = file_client.download_file(offset=start, length=length, max_concurrency=1).readinto(temp_file)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert file_data[start:file_size] == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_text(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + text_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(text_data)

        # Act
        file_content = file_client.download_file(max_concurrency=2, encoding='utf-8').readall()

        # Assert
        assert text_data == file_content

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_to_text_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert text_data == file_content
        self.assert_download_progress(
            len(text_data.encode('utf-8')),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_text_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        text_file = self._get_file_reference()
        text_data = self.get_random_text_data(self.MAX_SINGLE_GET_SIZE + 1)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert text_data == file_content
        self.assert_download_progress(
            len(text_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_text_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = self.get_random_text_data(1024)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert file_data == file_content
        self.assert_download_progress(
            len(file_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_text_with_encoding(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)
        file_client.upload_file(data)

        # Act
        file_content = file_client.download_file(encoding='UTF-16').readall()

        # Assert
        assert text == file_content

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_to_text_with_encoding_and_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert text == file_content
        self.assert_download_progress(
            len(data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_non_seekable(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            non_seekable_stream = TestStorageGetFile.NonSeekableFile(temp_file)
            bytes_read = file_client.download_file(max_concurrency=1).readinto(non_seekable_stream)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_non_seekable_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            non_seekable_stream = TestStorageGetFile.NonSeekableFile(temp_file)
            # Assert
            with pytest.raises(ValueError):
                file_client.download_file(max_concurrency=2).readinto(non_seekable_stream)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_non_seekable_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            non_seekable_stream = TestStorageGetFile.NonSeekableFile(temp_file)
            bytes_read = snapshot_client.download_file(max_concurrency=1).readinto(non_seekable_stream)
            # Assert
            assert isinstance(bytes_read, int)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_non_seekable_parallel_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        # Create a snapshot of the share and delete the file
        share_client = self.fsc.get_share_client(self.share_name)
        share_snapshot = share_client.create_snapshot()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key)
        file_client.delete_file()

        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            snapshot=share_snapshot,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            non_seekable_stream = TestStorageGetFile.NonSeekableFile(temp_file)
            # Assert
            with pytest.raises(ValueError):
                snapshot_client.download_file(max_concurrency=2).readinto(non_seekable_stream)

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_exact_get_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.MAX_SINGLE_GET_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert byte_data == file_content.readall()
        self.assert_download_progress(
            len(byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_exact_chunk_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.MAX_SINGLE_GET_SIZE + self.MAX_CHUNK_GET_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
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
        assert byte_data == file_content.readall()
        self.assert_download_progress(
            len(byte_data),
            self.MAX_CHUNK_GET_SIZE,
            self.MAX_SINGLE_GET_SIZE,
            progress)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = file_client.download_file(validate_content=True)

        # Assert
        assert self.byte_data == file_content.readall()

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_range_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        file_content = file_client.download_file(offset=0, length=1024, validate_content=True)

        # Assert
        assert file_content.properties.content_settings.content_md5 is None

        props = file_client.get_file_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        file_client.set_http_headers(props.content_settings)

        # Act
        file_content = file_client.download_file(offset=0, length=1024, validate_content=True)

        # Assert
        assert b'MDAwMDAwMDA=' == file_content.properties.content_settings.content_md5

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        file_content = file_client.download_file(offset=0, length=1024, validate_content=True)
    
        # Assert
        assert file_content.properties.server_encrypted

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_properties_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        self._setup(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + self.byte_file,
            credential=storage_account_key,
            max_single_get_size=self.MAX_SINGLE_GET_SIZE,
            max_chunk_get_size=self.MAX_CHUNK_GET_SIZE)

        # Act
        props = file_client.get_file_properties()

        # Assert
        assert props.server_encrypted

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_progress_single_get(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key)

        data = b'a' * 512
        file.upload_file(data)

        progress = ProgressTracker(len(data), len(data))

        # Act
        file.download_file(progress_hook=progress.assert_progress).readall()

        # Assert
        progress.assert_complete()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_file_progress_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        data = b'a' * 5120
        file.upload_file(data)

        progress = ProgressTracker(len(data), 1024)

        # Act
        file.download_file(progress_hook=progress.assert_progress).readall()

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_progress_chunked_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        self._setup(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        data = b'a' * 5120
        file.upload_file(data)

        progress = ProgressTracker(len(data), 1024)

        # Act
        file.download_file(max_concurrency=3, progress_hook=progress.assert_progress).readall()

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_get_file_progress_range_readinto(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        self._setup(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=self.directory_name + '/' + file_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        data = b'a' * 5120
        file.upload_file(data)

        length = 4096
        progress = ProgressTracker(length, 1024)
        result = BytesIO()

        # Act
        stream = file.download_file(
            offset=512,
            length=length,
            max_concurrency=3,
            progress_hook=progress.assert_progress
        )
        read = stream.readinto(result)

        # Assert
        progress.assert_complete()
        assert length == read

# ------------------------------------------------------------------------------
