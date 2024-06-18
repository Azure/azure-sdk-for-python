# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
import random
import tempfile
import uuid
from io import BytesIO
from math import ceil

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobProperties, StorageErrorCode
from azure.storage.blob.aio import BlobClient, BlobServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers_async import ProgressTracker, NonSeekableStream

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
# ------------------------------------------------------------------------------


class TestStorageGetBlobTest(AsyncStorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    async def _setup(self, storage_account_name, key, upload_blob=True):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key,
            max_single_get_size=32 * 1024,
            max_chunk_get_size=4 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.byte_blob = self.get_resource_name('byteblob')
        self.byte_data = self.get_random_bytes(64 * 1024 + 5)
        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                await container.create_container()
            except:
                pass

            if upload_blob:
                blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
                await blob.upload_blob(self.byte_data, overwrite=True)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    # -- Get test cases for blobs ----------------------------------------------
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_blob_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Act
        content = await blob.download_blob()

        # Assert
        assert isinstance(content.properties, BlobProperties)
        assert await content.readall() == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_blob_binary_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(binary_data)

        # Act
        content = await blob.download_blob()

        # Assert
        assert isinstance(content.properties, BlobProperties)
        assert await content.readall() == binary_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_no_content(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_data = b''
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Act
        content = await blob.download_blob()

        # Assert
        assert blob_data == await content.readall()
        assert 0 == content.properties.size

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_bytes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        content = await (await blob.download_blob(max_concurrency=2)).readall()

        # Assert
        assert self.byte_data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ranged_get_blob_to_bytes_with_single_byte(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        content = await (await blob.download_blob(offset=0, length=1)).readall()

        # Assert
        assert 1 == len(content)
        assert self.byte_data[0] == content[0]

        # Act
        content = await (await blob.download_blob(offset=5, length=1)).readall()

        # Assert
        assert 1 == len(content)
        assert self.byte_data[5] == content[0]

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ranged_get_blob_to_bytes_with_zero_byte(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_data = b''
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Act
        # the get request should fail in this case since the blob is empty and yet there is a range specified
        with pytest.raises(HttpResponseError) as e:
            await blob.download_blob(offset=0, length=5)
        assert StorageErrorCode.invalid_range == e.value.error_code

        with pytest.raises(HttpResponseError) as e:
            await blob.download_blob(offset=3, length=5)
        assert StorageErrorCode.invalid_range == e.value.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ranged_get_blob_with_missing_start_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_data = b'foobar'
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Act
        # the get request should fail fast in this case since start_range is missing while end_range is specified
        with pytest.raises(ValueError):
            await blob.download_blob(length=3)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_bytes_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        snapshot_ref = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(self.container_name, self.byte_blob, snapshot=snapshot_ref)

        await blob.upload_blob(self.byte_data, overwrite=True) # Modify the blob so the Etag no longer matches

        # Act
        content = await (await snapshot.download_blob(max_concurrency=2)).readall()

        # Assert
        assert self.byte_data == content

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_bytes_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = await (await blob.download_blob(raw_response_hook=callback, max_concurrency=2)).readall()

        # Assert
        assert self.byte_data == content
        self.assert_download_progress(
            len(self.byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_bytes_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = await (await blob.download_blob(raw_response_hook=callback, max_concurrency=1)).readall()

        # Assert
        assert self.byte_data == content
        self.assert_download_progress(
            len(self.byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_bytes_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = await (await blob.download_blob(raw_response_hook=callback)).readall()

        # Assert
        assert blob_data == content
        self.assert_download_progress(
            len(blob_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_stream(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == len(self.byte_data)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_readinto_raises_exceptions(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        callback_counter = {'value': 0}

        def callback(response):
            callback_counter['value'] += 1
            if callback_counter['value'] > 3:
                raise ValueError()

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(max_concurrency=2, raw_response_hook=callback)
            with pytest.raises(ValueError):
                await downloader.readinto(temp_file)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_stream_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(raw_response_hook=callback, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)
            # Assert
            assert read_bytes == len(self.byte_data)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual
        self.assert_download_progress(len(self.byte_data), self.config.max_chunk_get_size, self.config.max_single_get_size, progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_stream_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(raw_response_hook=callback, max_concurrency=1)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == len(self.byte_data)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual
        self.assert_download_progress(len(self.byte_data), self.config.max_chunk_get_size, self.config.max_single_get_size, progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_stream_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_data = self.get_random_bytes(1024)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))


        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(raw_response_hook=callback, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == 1024
            temp_file.seek(0)
            actual = temp_file.read()
            assert blob_data == actual
        self.assert_download_progress(len(blob_data), self.config.max_chunk_get_size, self.config.max_single_get_size, progress)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_ranged_get_blob_to_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        end_range = self.config.max_single_get_size
        FILE_PATH = 'ranged_get_blob_to_path_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(offset=1, length=end_range-1, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == end_range - 1
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[1:end_range] == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_ranged_get_blob_to_path_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        progress = []
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        start_range = 3
        end_range = self.config.max_single_get_size + 1024
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(
                offset=start_range,
                length=end_range,
                raw_response_hook=callback,
                max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == self.config.max_single_get_size + 1024
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[start_range:end_range + start_range] == actual
        self.assert_download_progress(end_range, self.config.max_chunk_get_size, self.config.max_single_get_size, progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ranged_get_blob_to_path_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(offset=1, length=4, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == 4
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[1:5] == actual

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_ranged_get_blob_to_path_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(offset=1, length=3, max_concurrency=1)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == 3
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data[1:4] == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_ranged_get_blob_to_path_invalid_range_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_size = self.config.max_single_get_size + 1
        blob_data = self.get_random_bytes(blob_size)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Act
        FILE_PATH = 'path_invalid_range_parallel_async.temp.{}.dat'.format(str(uuid.uuid4()))
        end_range = 2 * self.config.max_single_get_size
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(offset=1, length=end_range, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == blob_size - 1
            temp_file.seek(0)
            actual = temp_file.read()
            assert blob_data[1:blob_size] == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_ranged_get_blob_to_path_invalid_range_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_size = 1024
        blob_data = self.get_random_bytes(blob_size)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Act
        end_range = 2 * self.config.max_single_get_size
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(offset=1, length=end_range, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == blob_size - 1
            temp_file.seek(0)
            actual = temp_file.read()
            assert blob_data[1:blob_size] == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_text(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        text_blob = self.get_resource_name('textblob')
        text_data = self.get_random_text_data(self.config.max_single_get_size + 1)
        blob = self.bsc.get_blob_client(self.container_name, text_blob)
        await blob.upload_blob(text_data)

        # Act
        stream = await blob.download_blob(max_concurrency=2, encoding='UTF-8')
        content = await stream.readall()

        # Assert
        assert text_data == content

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_text_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        text_blob = self.get_resource_name('textblob')
        text_data = self.get_random_text_data(self.config.max_single_get_size + 1)
        blob = self.bsc.get_blob_client(self.container_name, text_blob)
        await blob.upload_blob(text_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        stream = await blob.download_blob(
            raw_response_hook=callback,
            max_concurrency=2,
            encoding='UTF-8')
        content = await stream.readall()

        # Assert
        assert text_data == content
        self.assert_download_progress(
            len(text_data.encode('utf-8')),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_text_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        text_blob = self._get_blob_reference()
        text_data = self.get_random_text_data(self.config.max_single_get_size + 1)
        blob = self.bsc.get_blob_client(self.container_name, text_blob)
        await blob.upload_blob(text_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        stream = await blob.download_blob(
            raw_response_hook=callback,
            max_concurrency=1,
            encoding='UTF-8')
        content = await stream.readall()

        # Assert
        assert text_data == content
        self.assert_download_progress(
            len(text_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_text_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_data = self.get_random_text_data(1024)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        stream = await blob.download_blob(raw_response_hook=callback, encoding='UTF-8')
        content = await stream.readall()

        # Assert
        assert blob_data == content
        self.assert_download_progress(
            len(blob_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_text_with_encoding(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(text, encoding='utf-16')

        # Act
        stream = await blob.download_blob(encoding='utf-16')
        content = await stream.readall()

        # Assert
        assert text == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_text_with_encoding_and_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(text, encoding='utf-16')

        # Act
        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        stream = await blob.download_blob(raw_response_hook=callback, encoding='utf-16')
        content = await stream.readall()

        # Assert
        assert text == content
        self.assert_download_progress(
            len(text.encode('utf-8')),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_non_seekable(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            non_seekable_stream = NonSeekableStream(temp_file)
            downloader = await blob.download_blob(max_concurrency=1)
            read_bytes = await downloader.readinto(non_seekable_stream)

            # Assert
            assert read_bytes == len(self.byte_data)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_non_seekable_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            non_seekable_stream = NonSeekableStream(temp_file)

            with pytest.raises(ValueError):
                downloader = await blob.download_blob(max_concurrency=2)
                properties = await downloader.readinto(non_seekable_stream)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_to_stream_exact_get_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(self.config.max_single_get_size)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(byte_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(raw_response_hook=callback, max_concurrency=2)
            properties = await downloader.readinto(temp_file)

            # Assert
            temp_file.seek(0)
            actual = temp_file.read()
            assert byte_data == actual
        self.assert_download_progress(len(byte_data), self.config.max_chunk_get_size, self.config.max_single_get_size, progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_exact_get_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(self.config.max_single_get_size)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(byte_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = await (await blob.download_blob(raw_response_hook=callback)).readall()

        # Assert
        assert byte_data == content
        self.assert_download_progress(
            len(byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_exact_chunk_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        byte_data = self.get_random_bytes(
            self.config.max_single_get_size +
            self.config.max_chunk_get_size)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(byte_data)

        progress = []

        def callback(response):
            current = response.context['download_stream_current']
            total = response.context['data_stream_total']
            progress.append((current, total))

        # Act
        content = await (await blob.download_blob(raw_response_hook=callback)).readall()

        # Assert
        assert byte_data == content
        self.assert_download_progress(
            len(byte_data),
            self.config.max_chunk_get_size,
            self.config.max_single_get_size,
            progress)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_to_stream_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(validate_content=True, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

            # Assert
            assert read_bytes == len(self.byte_data)
            temp_file.seek(0)
            actual = temp_file.read()
            assert self.byte_data == actual

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)

        # Act
        content = await (await blob.download_blob(validate_content=True, max_concurrency=2)).readall()

        # Assert
        assert self.byte_data == content

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_range_to_stream_with_overall_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        props = await blob.get_blob_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        await blob.set_http_headers(props.content_settings)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            downloader = await blob.download_blob(offset=0, length=1024, validate_content=True, max_concurrency=2)
            read_bytes = await downloader.readinto(temp_file)

        # Assert
        assert read_bytes == 1024
        assert b'MDAwMDAwMDA=' == downloader.properties.content_settings.content_md5
        assert downloader.size == 1024

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_range_with_overall_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        content = await blob.download_blob(offset=0, length=1024, validate_content=True)

        # Arrange
        props = await blob.get_blob_properties()
        props.content_settings.content_md5 = b'MDAwMDAwMDA='
        await blob.set_http_headers(props.content_settings)

        # Act
        content = await blob.download_blob(offset=0, length=1024, validate_content=True)

        # Assert
        assert b'MDAwMDAwMDA=' == content.properties.content_settings.content_md5

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_range_with_range_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, self.byte_blob)
        content = await blob.download_blob(offset=0, length=1024, validate_content=True)

        # Arrange
        props = await blob.get_blob_properties()
        props.content_settings.content_md5 = None
        await blob.set_http_headers(props.content_settings)

        # Act
        content = await blob.download_blob(offset=0, length=1024, validate_content=True)

        # Assert
        assert content.properties.content_settings.content_type is not None
        assert content.properties.content_settings.content_md5 is None
        assert content.properties.size == 1024

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_progress_single_get(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'a' * 512
        blob_name = self._get_blob_reference()
        blob = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name,
            blob_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        await blob.upload_blob(data, overwrite=True)

        progress = ProgressTracker(len(data), len(data))

        # Act
        stream = await blob.download_blob(progress_hook=progress.assert_progress)
        await stream.readall()

        # Assert
        progress.assert_complete()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_progress_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'a' * 5120
        blob_name = self._get_blob_reference()
        blob = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name,
            blob_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        await blob.upload_blob(data, overwrite=True)

        progress = ProgressTracker(len(data), 1024)

        # Act
        stream = await blob.download_blob(max_concurrency=1, progress_hook=progress.assert_progress)
        await stream.readall()

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_progress_chunked_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account_name, storage_account_key)
        data = b'a' * 5120
        blob_name = self._get_blob_reference()
        blob = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name,
            blob_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        await blob.upload_blob(data, overwrite=True)

        progress = ProgressTracker(len(data), 1024)

        # Act
        stream = await blob.download_blob(max_concurrency=3, progress_hook=progress.assert_progress)
        await stream.readall()

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_progress_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account_name, storage_account_key)
        data = b'a' * 5120
        blob_name = self._get_blob_reference()
        blob = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name,
            blob_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        await blob.upload_blob(data, overwrite=True)

        length = 4096
        progress = ProgressTracker(length, 1024)

        # Act
        stream = await blob.download_blob(
            offset=512,
            length=length,
            max_concurrency=3,
            progress_hook=progress.assert_progress)
        await stream.readall()

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_progress_readinto(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account_name, storage_account_key)
        data = b'a' * 5120
        blob_name = self._get_blob_reference()
        blob = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name,
            blob_name,
            credential=storage_account_key,
            max_single_get_size=1024,
            max_chunk_get_size=1024)

        await blob.upload_blob(data, overwrite=True)

        progress = ProgressTracker(len(data), 1024)
        result = BytesIO()

        # Act
        stream = await blob.download_blob(max_concurrency=3, progress_hook=progress.assert_progress)
        read = await stream.readinto(result)

        # Assert
        progress.assert_complete()
        assert len(data) == read

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_empty(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b''
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        # Act
        content = await (await blob.download_blob()).read()
        content2 = await (await blob.download_blob()).read(512)

        # Assert
        assert data == content
        assert data == content2

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_all(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        # Act
        content = await (await blob.download_blob()).read()

        # Assert
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_single(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 10 * 1024
        self.bsc._config.max_chunk_get_size = 10 * 1024

        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob()

        # Act
        result = bytearray()
        read_size = 512
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = await stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_small_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob()

        # Act
        result = bytearray()
        read_size = 512
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = await stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_large_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024
        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob()

        # Act
        result = bytearray()
        read_size = 1536
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = await stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_chunk_equal_download_chunk(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob()

        # Act
        result = bytearray()
        read_size = 1024
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = await stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_read_random_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Random chunk sizes, can only run live
        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 15  # 15375 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob()

        # Act
        result = bytearray()
        total = 0
        while total < len(data):
            read_size = random.randint(500, 2500)
            content = await stream.read(read_size)
            result.extend(content)
            total += len(content)

        # Assert
        assert result == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_blob_read_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 15  # 15375 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob(max_concurrency=3)

        # Act
        result = bytearray()
        read_size = 4096
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = await stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_into_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        data = b'12345' * 205 * 15  # 15375 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        stream = await blob.download_blob()

        # Act
        blob2 = self.bsc.get_blob_client(self.container_name, self._get_blob_reference() + '-copy')
        await blob2.upload_blob(stream, overwrite=True)
        result = await (await blob2.download_blob()).readall()

        # Assert
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_past(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'Hello World'
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        # Act
        stream = await blob.download_blob()
        result = await stream.read(25)

        # Assert
        assert result == data
        for _ in range(3):
            result = await stream.read(100)
            assert result == b''

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_ranged(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        # Act / Assert
        offset, length = 1024, 2048
        stream = await blob.download_blob(offset=offset, length=length)

        read_size = 1024
        data1 = await stream.read(read_size)
        data2 = await stream.read(read_size)

        assert data1 == data[offset:offset + read_size]
        assert data2 == data[offset + read_size:offset + length]

        offset, length = 501, 3000
        stream = await blob.download_blob(offset=offset, length=length)

        read_size = 1536
        data1 = await stream.read(read_size)
        data2 = await stream.read(read_size)

        assert data1 == data[offset:offset + read_size]
        assert data2 == data[offset + read_size:offset + length]

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_with_other_read_operations_single(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'Hello World'
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        # Act / Assert
        stream = await blob.download_blob()
        first = await stream.read(5)
        second = await stream.readall()

        assert first == data[:5]
        assert second == data[5:]

        stream = await blob.download_blob()
        first = await stream.read(5)
        second_stream = BytesIO()
        read_size = await stream.readinto(second_stream)
        second = second_stream.getvalue()

        assert first == data[:5]
        assert second == data[5:]
        assert read_size == len(second)

        # Test another read operation after reading all data
        stream = await blob.download_blob()
        first = await stream.read(25)
        second_stream = BytesIO()
        read_size = await stream.readinto(second_stream)
        second = second_stream.getvalue()

        assert first == data
        assert second == b''
        assert read_size == 0

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_with_other_read_operations_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 10  # 10250 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        # Act / Assert
        stream = await blob.download_blob()
        first = await stream.read(100)  # Read in first chunk
        second = await stream.readall()

        assert first == data[:100]
        assert second == data[100:]

        stream = await blob.download_blob()
        first = await stream.read(3000)  # Read past first chunk
        second = await stream.readall()

        assert first == data[:3000]
        assert second == data[3000:]

        stream = await blob.download_blob()
        first = await stream.read(3000)  # Read past first chunk
        second_stream = BytesIO()
        read_size = await stream.readinto(second_stream)
        second = second_stream.getvalue()

        assert first == data[:3000]
        assert second == data[3000:]
        assert read_size == len(second)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_with_other_read_operations_ranged(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 10  # 10250 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)
        offset, length = 1024, 2048

        # Act / Assert
        stream = await blob.download_blob(offset=offset, length=length)
        first = await stream.read(100)  # Read in first chunk
        second = await stream.readall()

        assert first == data[offset:offset + 100]
        assert second == data[offset + 100:offset + length]

        offset, length = 501, 5000
        stream = await blob.download_blob(offset=offset, length=length)
        first = await stream.read(3000)  # Read past first chunk
        second = await stream.readall()

        assert first == data[offset:offset + 3000]
        assert second == data[offset + 3000:offset + length]

        stream = await blob.download_blob(offset=offset, length=length)
        first = await stream.read(3000)  # Read past first chunk
        second_stream = BytesIO()
        read_size = await stream.readinto(second_stream)
        second = second_stream.getvalue()

        assert first == data[offset:offset + 3000]
        assert second == data[offset + 3000:offset + length]
        assert read_size == len(second)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = b'12345' * 205 * 5  # 5125 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        class CustomProgressTracker:
            def __init__(self):
                self.num_read = 0
                self.currents = [1024, 2048, 3072, 4096, 5120, 5125]
                self.totals = [5125] * len(self.currents)

            async def assert_progress(self, current, total):
                assert total == self.totals[self.num_read]
                assert current == self.currents[self.num_read]
                self.num_read += 1

        progress = CustomProgressTracker()
        stream = await blob.download_blob(progress_hook=progress.assert_progress)

        # Act / Assert
        for _ in range(4):
            await stream.read(500)
        await stream.readall()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_progress_chars(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = '你好世界' * 260  # 3120 bytes
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, overwrite=True)

        class CustomProgressTracker:
            def __init__(self):
                self.num_read = 0
                self.currents = [1024, 2048, 3072, 3120]
                self.totals = [3120] * len(self.currents)

            async def assert_progress(self, current, total):
                assert total == self.totals[self.num_read]
                assert current == self.currents[self.num_read]
                self.num_read += 1

        progress = CustomProgressTracker()
        stream = await blob.download_blob(encoding='utf-8', progress_hook=progress.assert_progress)

        # Act / Assert
        for _ in range(4):
            await stream.read(chars=50)
        await stream.readall()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_chars_single(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = '你好世界' * 5
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, encoding='utf-8', overwrite=True)

        stream = await blob.download_blob(encoding='utf-8')
        assert await stream.read() == data

        stream = await blob.download_blob(encoding='utf-8')
        assert await stream.read(chars=100000) == data

        result = ''
        stream = await blob.download_blob(encoding='utf-8')
        for _ in range(4):
            chunk = await stream.read(chars=5)
            result += chunk
            assert len(chunk) == 5

        result += await stream.readall()
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_chars_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = '你好世界' * 256  # 3 KiB
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, encoding='utf-8', overwrite=True)

        stream = await blob.download_blob(encoding='utf-8')
        assert await stream.read() == data

        stream = await blob.download_blob(encoding='utf-8')
        assert await stream.read(chars=100000) == data

        result = ''
        stream = await blob.download_blob(encoding='utf-8')
        for _ in range(4):
            chunk = await stream.read(chars=100)
            result += chunk
            assert len(chunk) == 100

        result += await stream.readall()
        assert result == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_chars_ranged(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = '你好世界' * 256  # 3 KiB
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, encoding='utf-8', overwrite=True)

        # Offset and length need to be multiple of 3 to meet unicode boundaries
        offset, length = 9, 1500
        expected = data[offset // 3: offset // 3 + length // 3]
        stream = await blob.download_blob(offset=offset, length=length, encoding='utf-8')
        assert await stream.read() == expected

        stream = await blob.download_blob(offset=offset, length=length, encoding='utf-8')
        assert await stream.read(chars=100000) == expected

        result = ''
        stream = await blob.download_blob(offset=offset, length=length, encoding='utf-8')
        for _ in range(4):
            chunk = await stream.read(chars=100)
            result += chunk
            assert len(chunk) == 100

        result += await stream.readall()
        assert result == expected

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_chars_mixed(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = '你好世界' * 2
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, encoding='utf-8', overwrite=True)

        stream = await blob.download_blob(encoding='utf-8')

        # Read some data as chars, this should prevent any reading as bytes
        assert await stream.read(chars=4) == '你好世界'

        # readinto, chunks, and read(size=x) should now be blocked
        with pytest.raises(ValueError) as e:
            await stream.readinto(BytesIO())
        assert 'Stream has been partially read in text mode.' in str(e.value)
        with pytest.raises(ValueError) as e:
            stream.chunks()
        assert 'Stream has been partially read in text mode.' in str(e.value)
        with pytest.raises(ValueError) as e:
            await stream.read(size=12)
        assert 'Stream has been partially read in text mode.' in str(e.value)

        # read() should still work to get remaining chars
        assert await stream.read() == '你好世界'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_read_chars_utf32(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key, upload_blob=False)
        self.bsc._config.max_single_get_size = 1024
        self.bsc._config.max_chunk_get_size = 1024

        data = '你好世界' * 256
        encoding = 'utf-32'
        blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        await blob.upload_blob(data, encoding=encoding, overwrite=True)

        stream = await blob.download_blob(encoding=encoding)
        assert await stream.read() == data

        result = ''
        stream = await blob.download_blob(encoding=encoding)
        for _ in range(4):
            chunk = await stream.read(chars=100)
            result += chunk
            assert len(chunk) == 100

        result += await stream.readall()
        assert result == data

# ------------------------------------------------------------------------------
