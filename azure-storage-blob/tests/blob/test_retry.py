# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    #BlobBlock,  # TODO
)
from azure.storage.common import ExponentialRetry
from tests.testcase import (
    StorageTestCase,
    ResponseCallback,
    record,
    TestMode
)

# test constants
PUT_BLOCK_SIZE = 4 * 1024


class StorageBlobRetryTest(StorageTestCase):

    def setUp(self):
        super(StorageBlobRetryTest, self).setUp()

        self.bs = self._create_storage_service(BlockBlobService, self.settings)

        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

    def tearDown(self):
        if not self.is_playback():
            self.bs.delete_container(self.container_name)

        return super(StorageBlobRetryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    class NonSeekableStream(object):
        def __init__(self, wrapped_stream):
            self.wrapped_stream = wrapped_stream

        def write(self, data):
            self.wrapped_stream.write(data)

        def read(self, count):
            return self.wrapped_stream.read(count)

        def tell(self):
            return self.wrapped_stream.tell()

    @record
    def test_retry_put_block_with_seekable_stream(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = BytesIO(data)

        # rig the response so that it fails for a single time
        self.bs.response_callback = ResponseCallback(status=201, new_status=408).override_first_status
        self.bs.retry = ExponentialRetry(initial_backoff=1, increment_base=2, max_attempts=3).retry

        # Act
        self.bs.put_block(self.container_name, blob_name, data_stream, 1)

        # Assert
        block_list = self.bs.get_block_list(self.container_name, blob_name, block_list_type="uncommitted")
        self.assertEqual(len(block_list.uncommitted_blocks), 1)
        self.assertEqual(block_list.uncommitted_blocks[0].size, PUT_BLOCK_SIZE)

        # Commit block and verify content
        block_list = [BlobBlock(id='1')]
        self.bs.put_block_list(self.container_name, blob_name, block_list)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(blob.content, data)

    @record
    def test_retry_put_block_with_non_seekable_stream(self):
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = self.NonSeekableStream(BytesIO(data))

        # rig the response so that it fails for a single time
        self.bs.response_callback = ResponseCallback(status=201, new_status=408).override_first_status
        self.bs.retry = ExponentialRetry(initial_backoff=1, increment_base=2, max_attempts=3).retry

        # Act
        # Note: put_block transforms non-seekable streams into byte arrays before handing it off to the executor
        self.bs.put_block(self.container_name, blob_name, data_stream, 1)

        # Assert
        block_list = self.bs.get_block_list(self.container_name, blob_name, block_list_type="uncommitted")
        self.assertEqual(len(block_list.uncommitted_blocks), 1)
        self.assertEqual(block_list.uncommitted_blocks[0].size, PUT_BLOCK_SIZE)

        # Commit block and verify content
        block_list = [BlobBlock(id='1')]
        self.bs.put_block_list(self.container_name, blob_name, block_list)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name)
        self.assertEqual(blob.content, data)
