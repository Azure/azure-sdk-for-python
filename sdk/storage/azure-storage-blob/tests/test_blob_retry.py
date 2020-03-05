# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from io import BytesIO, UnsupportedOperation
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    ExponentialRetry
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.core.exceptions import ResourceExistsError, HttpResponseError
from _shared.testcase import (
    StorageTestCase,
    ResponseCallback,
    GlobalStorageAccountPreparer
)

# test constants
PUT_BLOCK_SIZE = 4 * 1024


class StorageBlobRetryTest(StorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def setUp(self):
        self.retry = ExponentialRetry(initial_backoff=1, increment_base=2, retry_total=3)

    def _setup(self, bsc):
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    class NonSeekableStream(object):
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_retry_put_block_with_seekable_stream(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key,
                                retry_policy=self.retry)
        self._setup(bsc)
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = BytesIO(data)

        # rig the response so that it fails for a single time
        responder = ResponseCallback(status=201, new_status=408)

        # Act
        blob = bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block(1, data_stream, raw_response_hook=responder.override_first_status)

        # Assert
        _, uncommitted_blocks = blob.get_block_list(
            block_list_type="uncommitted",
            raw_response_hook=responder.override_first_status)
        self.assertEqual(len(uncommitted_blocks), 1)
        self.assertEqual(uncommitted_blocks[0].size, PUT_BLOCK_SIZE)

        # Commit block and verify content
        blob.commit_block_list(['1'], raw_response_hook=responder.override_first_status)

        # Assert
        content = blob.download_blob().readall()
        self.assertEqual(content, data)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_retry_put_block_with_non_seekable_stream(self, resource_group, location, storage_account,
                                                      storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key,
                                retry_policy=self.retry)
        self._setup(bsc)
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = self.NonSeekableStream(BytesIO(data))

        # rig the response so that it fails for a single time
        responder = ResponseCallback(status=201, new_status=408)

        # Act
        blob = bsc.get_blob_client(self.container_name, blob_name)
        # Note: put_block transforms non-seekable streams into byte arrays before handing it off to the executor
        blob.stage_block(1, data_stream, raw_response_hook=responder.override_first_status)

        # Assert
        _, uncommitted_blocks = blob.get_block_list(
            block_list_type="uncommitted",
            raw_response_hook=responder.override_first_status)
        self.assertEqual(len(uncommitted_blocks), 1)
        self.assertEqual(uncommitted_blocks[0].size, PUT_BLOCK_SIZE)

        # Commit block and verify content
        blob.commit_block_list(['1'], raw_response_hook=responder.override_first_status)

        # Assert
        content = blob.download_blob().readall()
        self.assertEqual(content, data)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_retry_put_block_with_non_seekable_stream_fail(self, resource_group, location, storage_account,
                                                           storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=storage_account_key,
                                retry_policy=self.retry)
        self._setup(bsc)
        blob_name = self.get_resource_name('blob')
        data = self.get_random_bytes(PUT_BLOCK_SIZE)
        data_stream = self.NonSeekableStream(BytesIO(data))

        # rig the response so that it fails for a single time
        responder = ResponseCallback(status=201, new_status=408)

        # Act
        blob = bsc.get_blob_client(self.container_name, blob_name)

        with self.assertRaises(HttpResponseError) as error:
            blob.stage_block(1, data_stream, length=PUT_BLOCK_SIZE, raw_response_hook=responder.override_first_status)

        # Assert
        self.assertEqual(error.exception.response.status_code, 408)