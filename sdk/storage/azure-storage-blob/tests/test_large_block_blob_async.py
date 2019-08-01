# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio

import os
import unittest

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
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

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageLargeBlockBlobTestAsync(StorageTestCase):
    def setUp(self):
        super(StorageLargeBlockBlobTestAsync, self).setUp()

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
            min_large_block_upload_threshold=1 * 1024 * 1024,
            transport=AiohttpTestTransport())
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.bsc.delete_container(self.container_name))
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageLargeBlockBlobTestAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    
    async def _setup(self):
        if not self.is_playback():
            try:
                await self.bsc.create_container(self.container_name)
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
        async for data in actual_data:
            actual_bytes += data
        self.assertEqual(actual_bytes, expected_data)

    # --Test cases for block blobs --------------------------------------------

    async def _test_put_block_bytes_large_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        futures = []
        for i in range(5):
            futures.append(blob.stage_block(
                'block {0}'.format(i).encode('utf-8'), os.urandom(LARGE_BLOCK_SIZE)))
        
        await asyncio.gather(*futures)

            # Assert

    @record
    def test_put_block_bytes_large_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_bytes_large_async())

    async def _test_put_block_bytes_large_with_md5_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        for i in range(5):
            resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                os.urandom(LARGE_BLOCK_SIZE),
                validate_content=True)
            self.assertIsNone(resp)

    @record
    def test_put_block_bytes_large_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_bytes_large_with_md5_async())

    async def _test_put_block_stream_large_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE)
            self.assertIsNone(resp)

            # Assert

    @record
    def test_put_block_stream_large_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_stream_large_async())

    async def _test_put_block_stream_large_with_md5_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = resp = await blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE,
                validate_content=True)
            self.assertIsNone(resp)

        # Assert

    @record
    def test_put_block_stream_large_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_stream_large_with_md5_async())

    async def _test_create_large_blob_from_path_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_large_blob_from_path_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_path_async())

    async def _test_create_large_blob_from_path_with_md5_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, validate_content=True, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_large_blob_from_path_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_path_with_md5_async())

    async def _test_create_large_blob_from_path_non_parallel_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(self.get_random_bytes(100))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, max_connections=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_large_blob_from_path_non_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_path_non_parallel_async())

    async def _test_create_large_blob_from_path_with_progress_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
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
            await blob.upload_blob(stream, max_connections=2, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_create_large_blob_from_path_with_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_path_with_progress_async())

    async def _test_create_large_blob_from_path_with_properties_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
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
            await blob.upload_blob(stream, content_settings=content_settings, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_large_blob_from_path_with_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_path_with_properties_async())

    async def _test_create_large_blob_from_stream_chunked_upload_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_large_blob_from_stream_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_stream_chunked_upload_async())

    async def _test_create_large_blob_from_stream_with_progress_chunked_upload_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
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
            await blob.upload_blob(stream, max_connections=2, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_create_large_blob_from_stream_with_progress_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_stream_with_progress_chunked_upload_async())

    async def _test_create_large_blob_from_stream_chunked_upload_with_count_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(os.urandom(LARGE_BLOB_SIZE))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, length=blob_size, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    @record
    def test_create_large_blob_from_stream_chunked_upload_with_count_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_stream_chunked_upload_with_count_async())

    async def _test_create_large_blob_from_stream_chunked_upload_with_count_and_properties_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
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
            await blob.upload_blob(
                stream, length=blob_size, content_settings=content_settings, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_large_blob_from_stream_chunked_upload_with_count_and_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_stream_chunked_upload_with_count_and_properties_async())

    async def _test_create_large_blob_from_stream_chunked_upload_with_properties_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
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
            await blob.upload_blob(stream, content_settings=content_settings, max_connections=2)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_large_blob_from_stream_chunked_upload_with_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_blob_from_stream_chunked_upload_with_properties_async())

# ------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
