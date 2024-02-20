# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import tempfile

from io import BytesIO
from os import path, remove, urandom
import uuid

import pytest
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'largeblob'
LARGE_BLOB_SIZE = 12 * 1024 * 1024
LARGE_BLOCK_SIZE = 6 * 1024 * 1024
# ------------------------------------------------------------------------------


class TestStorageLargeBlockBlobAsync(AsyncStorageRecordedTestCase):
    async def _setup(self, storage_account_name, key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key,
            max_single_put_size=32 * 1024,
            max_block_size=2 * 1024 * 1024,
            min_large_block_upload_threshold=1 * 1024 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    async def _create_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b'')
        return blob

    async def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = await blob.download_blob()
        actual_bytes = b""
        async for data in actual_data.chunks():
            actual_bytes += data
        assert actual_bytes == expected_data
    # --------------------------------------------------------------------------

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_put_block_bytes_large(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = await self._create_blob()

        # Act
        futures = []
        for i in range(5):
            futures.append(blob.stage_block(
                'block {0}'.format(i).encode('utf-8'), urandom(LARGE_BLOCK_SIZE)))

        await asyncio.gather(*futures)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_put_block_bytes_large_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = await self._create_blob()

        # Act
        for i in range(5):
            resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                urandom(LARGE_BLOCK_SIZE),
                validate_content=True)
            assert resp is not None
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_put_block_stream_large(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = await self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE)
            assert resp is not None
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_put_block_stream_large_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = await self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE,
                validate_content=True)
            assert resp is not None
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

        # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_large_blob_from_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, max_concurrency=2, overwrite=True)

        block_list = await blob.get_block_list()

        # Assert
        assert len(block_list) != 0
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_large_blob_from_path_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, validate_content=True, max_concurrency=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)


    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_large_blob_from_path_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(self.get_random_bytes(100))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, max_concurrency=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)


    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_large_blob_from_path_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, max_concurrency=2, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)


    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_large_blob_from_path_with_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, content_settings=content_settings, max_concurrency=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_creat_lrg_blob_frm_stream_chnkd_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, max_concurrency=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_creat_lrgblob_frm_strm_w_prgrss_chnkduplod(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, max_concurrency=2, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_creat_lrgblob_frm_strm_chnkd_uplod_w_cnt(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        blob_size = len(data) - 301
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, length=blob_size, max_concurrency=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_creat_lrg_frm_stream_chnk_upload_w_cntnprops(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, length=blob_size, content_settings=content_settings, max_concurrency=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = await blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_large_from_stream_chunk_upld_with_props(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await blob.upload_blob(temp_file, content_settings=content_settings, max_concurrency=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language

# ------------------------------------------------------------------------------
