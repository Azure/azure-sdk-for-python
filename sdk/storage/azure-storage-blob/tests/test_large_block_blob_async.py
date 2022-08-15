# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio

from os import path, remove, sys, urandom
import unittest
import uuid

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer

from azure.storage.blob import ContentSettings

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient
)

if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from settings.testcase import BlobPreparer
from devtools_testutils.storage.aio import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'largeblob'
LARGE_BLOB_SIZE = 12 * 1024 * 1024
LARGE_BLOCK_SIZE = 6 * 1024 * 1024

# ------------------------------------------------------------------------------

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageLargeBlockBlobTestAsync(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------

    async def _setup(self, storage_account_name, key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key,
            max_single_put_size=32 * 1024,
            max_block_size=2 * 1024 * 1024,
            min_large_block_upload_threshold=1 * 1024 * 1024,
            retry_total=0,
            transport=AiohttpTestTransport())
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except:
                pass

    def _teardown(self, file_name):
        if path.isfile(file_name):
            try:
                remove(file_name)
            except:
                pass

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
        self.assertEqual(actual_bytes, expected_data)

    # --Test cases for block blobs --------------------------------------------
    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_bytes_large_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = await self._create_blob()

        # Act
        futures = []
        for i in range(5):
            futures.append(blob.stage_block(
                'block {0}'.format(i).encode('utf-8'), urandom(LARGE_BLOCK_SIZE)))

        await asyncio.gather(*futures)

            # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_bytes_large_with_md5_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = await self._create_blob()

        # Act
        for i in range(5):
            resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                urandom(LARGE_BLOCK_SIZE),
                validate_content=True)
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_stream_large_async(self, storage_account_name, storage_account_key):
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
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

            # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_stream_large_with_md5_async(self, storage_account_name, storage_account_key):
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
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

        # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_blob_from_path_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'create_large_blob_from_path_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, max_concurrency=2, overwrite=True)

            block_list = await blob.get_block_list()

            # Assert
            self.assertIsNot(len(block_list), 0)
            await self.assertBlobEqual(self.container_name, blob_name, data)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_blob_from_path_with_md5_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'reate_large_blob_from_path_with_md5_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, validate_content=True, max_concurrency=2)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_blob_from_path_non_parallel_async(self, storage_account_name, storage_account_key):

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(self.get_random_bytes(100))
        FILE_PATH = 'large_blob_from_path_non_parallel_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, max_concurrency=1)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_blob_from_path_with_progress_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        FILE_PATH = 'large_blob_from_path_with_progress_asyn.temp.{}.dat'.format(str(uuid.uuid4()))
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            progress = []
            def callback(response):
                current = response.context['upload_stream_current']
                total = response.context['data_stream_total']
                if current is not None:
                    progress.append((current, total))

            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, max_concurrency=2, raw_response_hook=callback)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
            self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_blob_from_path_with_properties_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'large_blob_from_path_with_properties_asy.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            content_settings = ContentSettings(
                content_type='image/png',
                content_language='spanish')
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
            properties = await blob.get_blob_properties()
            self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
            self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_creat_lrg_blob_frm_stream_chnkd_upload_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'frm_stream_chnkd_upload_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, max_concurrency=2)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_creat_lrgblob_frm_strm_w_prgrss_chnkduplod_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'frm_strm_w_prgrss_chnkduplod_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            progress = []
            def callback(response):
                current = response.context['upload_stream_current']
                total = response.context['data_stream_total']
                if current is not None:
                    progress.append((current, total))

            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, max_concurrency=2, raw_response_hook=callback)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
            self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_creat_lrgblob_frm_strm_chnkd_uplod_w_cnt_async(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = '_lrgblob_frm_strm_chnkd_uplod_w_cnt_.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            blob_size = len(data) - 301
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, length=blob_size, max_concurrency=2)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_creat_lrg_frm_stream_chnk_upload_w_cntnprops(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'frm_stream_chnk_upload_w_cntnprops_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            content_settings = ContentSettings(
                content_type='image/png',
                content_language='spanish')
            blob_size = len(data) - 301
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(
                    stream, length=blob_size, content_settings=content_settings, max_concurrency=2)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
            properties = await blob.get_blob_properties()
            self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
            self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        finally:
            self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_from_stream_chunk_upld_with_props(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'from_stream_chunk_upld_with_props_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        try:
            content_settings = ContentSettings(
                content_type='image/png',
                content_language='spanish')
            with open(FILE_PATH, 'rb') as stream:
                await blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2)

            # Assert
            await self.assertBlobEqual(self.container_name, blob_name, data)
            properties = await blob.get_blob_properties()
            self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
            self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        finally:
            self._teardown(FILE_PATH)
# ------------------------------------------------------------------------------
