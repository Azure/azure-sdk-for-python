# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from os import path, remove, sys, urandom
import platform
import unittest
import uuid
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobBlock,
    ContentSettings
)

if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'largestblob'
LARGEST_BLOCK_SIZE = 4000 * 1024 * 1024

# ------------------------------------------------------------------------------
if platform.python_implementation() == 'PyPy':
    pytest.skip("Skip tests for Pypy", allow_module_level=True)

class StorageLargestBlockBlobTest(StorageTestCase):
    def _setup(self, storage_account, key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=key,
            max_single_put_size=32 * 1024,
            max_block_size=LARGEST_BLOCK_SIZE,
            min_large_block_upload_threshold=1 * 1024 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.container_name = self.container_name + str(uuid.uuid4())

        if self.is_live:
            self.bsc.create_container(self.container_name)

    def _teardown(self, file_name):
        if path.isfile(file_name):
            try:
                remove(file_name)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'')
        return blob

    # --Test cases for block blobs --------------------------------------------
    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_put_block_bytes_largest(self, resource_group, location, storage_account, storage_account_key):

        self._setup(storage_account, storage_account_key)
        blob = self._create_blob()

        # Act
        data = urandom(LARGEST_BLOCK_SIZE)
        blockId = str(uuid.uuid4()).encode('utf-8')
        resp = blob.stage_block(
            blockId,
            data,
            length=LARGEST_BLOCK_SIZE)
        blob.commit_block_list([BlobBlock(blockId)])
        block_list = blob.get_block_list()

        # Assert
        self.assertIsNotNone(resp)
        assert 'content_md5' in resp
        assert 'content_crc64' in resp
        assert 'request_id' in resp
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 1)
        self.assertEqual(block_list[0][0].size, LARGEST_BLOCK_SIZE)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_put_block_stream_largest(self, resource_group, location, storage_account, storage_account_key):

        self._setup(storage_account, storage_account_key)
        blob = self._create_blob()

        # Act
        stream = LargeStream(LARGEST_BLOCK_SIZE)
        blockId = str(uuid.uuid4())
        requestId = str(uuid.uuid4())
        resp = blob.stage_block(
            blockId,
            stream,
            length=LARGEST_BLOCK_SIZE,
            client_request_id=requestId)
        blob.commit_block_list([BlobBlock(blockId)])
        block_list = blob.get_block_list()

        # Assert
        self.assertIsNotNone(resp)
        assert 'content_md5' in resp
        assert 'content_crc64' in resp
        assert 'request_id' in resp
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 1)
        self.assertEqual(block_list[0][0].size, LARGEST_BLOCK_SIZE)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_largest_blob_from_path(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        FILE_PATH = 'largest_blob_from_path.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            largeStream = LargeStream(LARGEST_BLOCK_SIZE, 100 * 1024 * 1024)
            chunk = largeStream.read()
            while chunk:
                stream.write(chunk)
                chunk = largeStream.read()

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2)
        block_list = blob.get_block_list()

        # Assert
        self._teardown(FILE_PATH)
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 1)
        self.assertEqual(block_list[0][0].size, LARGEST_BLOCK_SIZE)

class LargeStream:
    def __init__(self, length, initial_buffer_length=1024*1024):
        self._base_data = urandom(initial_buffer_length)
        self._base_data_length = initial_buffer_length
        self._position = 0
        self._remaining = length

    def read(self, size=None):
        if self._remaining == 0:
            return None

        if size is None:
            e = self._base_data_length
        else:
            e = size
        e = min(e, self._remaining)
        if e > self._base_data_length:
            self._base_data = urandom(e)
            self._base_data_length = e
        self._remaining = self._remaining - e
        return self._base_data[:e]

    def remaining(self):
        return self._remaining

# ------------------------------------------------------------------------------
