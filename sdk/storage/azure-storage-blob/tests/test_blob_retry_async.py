# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio

from io import BytesIO, IOBase, UnsupportedOperation
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    ExponentialRetry
)
from azure.core.exceptions import ResourceExistsError, HttpResponseError
from testcase import (
    StorageTestCase,
    ResponseCallback,
    record,
    TestMode
)

# test constants
PUT_BLOCK_SIZE = 4 * 1024


class StorageBlobRetryTestAsync(StorageTestCase):

    def setUp(self):
        super(StorageBlobRetryTestAsync, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()
        retry = ExponentialRetry(initial_backoff=1, increment_base=2, retry_total=3)

        self.bs = BlobServiceClient(url, credential=credential, retry_policy=retry)
        self.container_name = self.get_resource_name('utcontainer')

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.bs.delete_container(self.container_name))
            except:
                pass

        return super(StorageBlobRetryTestAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    async def _setup(self):
        if not self.is_playback():
            try:
                await self.bs.create_container(self.container_name)
            except ResourceExistsError:
                pass

    class NonSeekableStream(IOBase):
        def __init__(self, wrapped_stream):
            self.wrapped_stream = wrapped_stream

        def write(self, data):
            self.wrapped_stream.write(data)

        def read(self, count):
            return self.wrapped_stream.read(count)

        def seek(self, *args, **kwargs):
            raise UnsupportedOperation("boom!")

        def tell(self):
            return self.wrapped_stream.tell()

    async def _test_retry_put_block_with_seekable_stream_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = BytesIO(data)

        # rig the response so that it fails for a single time
        responder = ResponseCallback(status=201, new_status=408)
        
        # Act
        blob = self.bs.get_blob_client(self.container_name, blob_name)
        await blob.stage_block(1, data_stream, raw_response_hook=responder.override_first_status)

        # Assert
        _, uncommitted_blocks = await blob.get_block_list(
            block_list_type="uncommitted",
            raw_response_hook=responder.override_first_status)
        self.assertEqual(len(uncommitted_blocks), 1)
        self.assertEqual(uncommitted_blocks[0].size, PUT_BLOCK_SIZE)

        # Commit block and verify content
        await blob.commit_block_list(['1'], raw_response_hook=responder.override_first_status)

        # Assert
        content = await (await blob.download_blob()).content_as_bytes()
        self.assertEqual(content, data)

    def test_retry_put_block_with_seekable_stream_async(self):
        pytest.skip("Aiohttp closes stream after request - cannot rewind.")
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_put_block_with_seekable_stream_async())

    async def _test_retry_put_block_with_non_seekable_stream_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = self.NonSeekableStream(BytesIO(data))

        # rig the response so that it fails for a single time
        responder = ResponseCallback(status=201, new_status=408)

        # Act
        blob = self.bs.get_blob_client(self.container_name, blob_name)
        # Note: put_block transforms non-seekable streams into byte arrays before handing it off to the executor
        await blob.stage_block(1, data_stream, raw_response_hook=responder.override_first_status)

        # Assert
        _, uncommitted_blocks = await blob.get_block_list(
            block_list_type="uncommitted",
            raw_response_hook=responder.override_first_status)
        self.assertEqual(len(uncommitted_blocks), 1)
        self.assertEqual(uncommitted_blocks[0].size, PUT_BLOCK_SIZE)

        # Commit block and verify content
        await blob.commit_block_list(['1'], raw_response_hook=responder.override_first_status)

        # Assert
        content = await (await blob.download_blob()).content_as_bytes()
        self.assertEqual(content, data)

    def test_retry_put_block_with_non_seekable_stream_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_put_block_with_non_seekable_stream_async())

    async def _test_retry_put_block_with_non_seekable_stream_fail_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = self.NonSeekableStream(BytesIO(data))

        # rig the response so that it fails for a single time
        responder = ResponseCallback(status=201, new_status=408)

        # Act
        blob = self.bs.get_blob_client(self.container_name, blob_name)
        
        with self.assertRaises(HttpResponseError) as error:
            await blob.stage_block(1, data_stream, length=PUT_BLOCK_SIZE, raw_response_hook=responder.override_first_status)
    
        # Assert
        self.assertEqual(error.exception.response.status_code, 408)

    def test_retry_put_block_with_non_seekable_stream_fail_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_put_block_with_non_seekable_stream_fail_async())
