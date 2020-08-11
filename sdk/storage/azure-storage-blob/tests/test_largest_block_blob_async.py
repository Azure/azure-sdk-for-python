# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import BytesIO

import pytest

from os import path, remove, urandom
import platform
import uuid

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient
)
from azure.storage.blob import (
    BlobBlock
)
from azure.storage.blob._shared.base_client import _format_shared_key_credential
from azure.storage.blob._shared.constants import CONNECTION_TIMEOUT, READ_TIMEOUT

from _shared.asynctestcase import AsyncStorageTestCase
from _shared.testcase import GlobalStorageAccountPreparer

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'largestblob'
LARGEST_BLOCK_SIZE = 4000 * 1024 * 1024
LARGEST_SINGLE_UPLOAD_SIZE = 5000 * 1024 * 1024

# ------------------------------------------------------------------------------
if platform.python_implementation() == 'PyPy':
    pytest.skip("Skip tests for Pypy", allow_module_level=True)


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageLargestBlockBlobTestAsync(AsyncStorageTestCase):
    async def _setup(self, storage_account, key, additional_policies=None, min_large_block_upload_threshold=1 * 1024 * 1024,
               max_single_put_size=32 * 1024):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=key,
            max_single_put_size=max_single_put_size,
            max_block_size=LARGEST_BLOCK_SIZE,
            min_large_block_upload_threshold=min_large_block_upload_threshold,
            _additional_pipeline_policies=additional_policies,
            transport=AiohttpTestTransport(
                connection_timeout=CONNECTION_TIMEOUT,
                read_timeout=READ_TIMEOUT
            ))
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.container_name = self.container_name + str(uuid.uuid4())

        if self.is_live:
            await self.bsc.create_container(self.container_name)

    def _teardown(self, file_name):
        if path.isfile(file_name):
            try:
                remove(file_name)
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

    # --Test cases for block blobs --------------------------------------------
    @pytest.mark.live_test_only
    @pytest.mark.skip(reason="This takes really long time")
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_bytes_largest(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob = await self._create_blob()

        # Act
        data = urandom(LARGEST_BLOCK_SIZE)
        blockId = str(uuid.uuid4()).encode('utf-8')
        resp = await blob.stage_block(
            blockId,
            data,
            length=LARGEST_BLOCK_SIZE)
        await blob.commit_block_list([BlobBlock(blockId)])
        block_list = await blob.get_block_list()

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_bytes_largest_without_network(self, resource_group, location, storage_account, storage_account_key):
        payload_dropping_policy = PayloadDroppingPolicy()
        credential_policy = _format_shared_key_credential(storage_account.name, storage_account_key)
        await self._setup(storage_account, storage_account_key, [payload_dropping_policy, credential_policy])
        blob = await self._create_blob()

        # Act
        data = urandom(LARGEST_BLOCK_SIZE)
        blockId = str(uuid.uuid4()).encode('utf-8')
        resp = await blob.stage_block(
            blockId,
            data,
            length=LARGEST_BLOCK_SIZE)
        await blob.commit_block_list([BlobBlock(blockId)])
        block_list = await blob.get_block_list()

        # Assert
        self.assertIsNotNone(resp)
        assert 'content_md5' in resp
        assert 'content_crc64' in resp
        assert 'request_id' in resp
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 1)
        self.assertEqual(payload_dropping_policy.put_block_counter, 1)
        self.assertEqual(payload_dropping_policy.put_block_sizes[0], LARGEST_BLOCK_SIZE)

    @pytest.mark.live_test_only
    @pytest.mark.skip(reason="This takes really long time")
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_stream_largest(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob = await self._create_blob()

        # Act
        stream = LargeStream(LARGEST_BLOCK_SIZE)
        blockId = str(uuid.uuid4())
        requestId = str(uuid.uuid4())
        resp = await blob.stage_block(
            blockId,
            stream,
            length=LARGEST_BLOCK_SIZE,
            client_request_id=requestId)
        await blob.commit_block_list([BlobBlock(blockId)])
        block_list = await blob.get_block_list()

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_stream_largest_without_network(self, resource_group, location, storage_account, storage_account_key):
        payload_dropping_policy = PayloadDroppingPolicy()
        credential_policy = _format_shared_key_credential(storage_account.name, storage_account_key)
        await self._setup(storage_account, storage_account_key, [payload_dropping_policy, credential_policy])
        blob = await self._create_blob()

        # Act
        stream = LargeStream(LARGEST_BLOCK_SIZE)
        blockId = str(uuid.uuid4())
        requestId = str(uuid.uuid4())
        resp = await blob.stage_block(
            blockId,
            stream,
            length=LARGEST_BLOCK_SIZE,
            client_request_id=requestId)
        await blob.commit_block_list([BlobBlock(blockId)])
        block_list = await blob.get_block_list()

        # Assert
        self.assertIsNotNone(resp)
        assert 'content_md5' in resp
        assert 'content_crc64' in resp
        assert 'request_id' in resp
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 1)
        self.assertEqual(payload_dropping_policy.put_block_counter, 1)
        self.assertEqual(payload_dropping_policy.put_block_sizes[0], LARGEST_BLOCK_SIZE)

    @pytest.mark.live_test_only
    @pytest.mark.skip(reason="This takes really long time")
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_largest_blob_from_path(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
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
            await blob.upload_blob(stream, max_concurrency=2)

        # Assert
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_largest_blob_from_path_without_network(self, resource_group, location, storage_account, storage_account_key):
        payload_dropping_policy = PayloadDroppingPolicy()
        credential_policy = _format_shared_key_credential(storage_account.name, storage_account_key)
        await self._setup(storage_account, storage_account_key, [payload_dropping_policy, credential_policy])
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
            await blob.upload_blob(stream, max_concurrency=2)

        # Assert
        self._teardown(FILE_PATH)
        self.assertEqual(payload_dropping_policy.put_block_counter, 1)
        self.assertEqual(payload_dropping_policy.put_block_sizes[0], LARGEST_BLOCK_SIZE)

    @pytest.mark.skip(reason="This takes really long time")
    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_largest_blob_from_stream_without_network(self, resource_group, location, storage_account, storage_account_key):
        payload_dropping_policy = PayloadDroppingPolicy()
        credential_policy = _format_shared_key_credential(storage_account.name, storage_account_key)
        await self._setup(storage_account, storage_account_key, [payload_dropping_policy, credential_policy])
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        number_of_blocks = 50000

        stream = LargeStream(LARGEST_BLOCK_SIZE*number_of_blocks)

        # Act
        await blob.upload_blob(stream, max_concurrency=1)

        # Assert
        self.assertEqual(payload_dropping_policy.put_block_counter, number_of_blocks)
        self.assertEqual(payload_dropping_policy.put_block_sizes[0], LARGEST_BLOCK_SIZE)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_largest_blob_from_stream_single_upload_without_network(self, resource_group, location, storage_account, storage_account_key):
        payload_dropping_policy = PayloadDroppingPolicy()
        credential_policy = _format_shared_key_credential(storage_account.name, storage_account_key)
        await self._setup(storage_account, storage_account_key, [payload_dropping_policy, credential_policy],
                    max_single_put_size=LARGEST_SINGLE_UPLOAD_SIZE)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        stream = LargeStream(LARGEST_SINGLE_UPLOAD_SIZE)

        # Act
        await blob.upload_blob(stream, length=LARGEST_SINGLE_UPLOAD_SIZE, max_concurrency=1)

        # Assert
        self.assertEqual(payload_dropping_policy.put_block_counter, 0)
        self.assertEqual(payload_dropping_policy.put_blob_counter, 1)


class LargeStream(BytesIO):
    def __init__(self, length, initial_buffer_length=1024 * 1024):
        self._base_data = urandom(initial_buffer_length)
        self._base_data_length = initial_buffer_length
        self._position = 0
        self._remaining = length
        self._closed = False

    def read(self, size=None):
        if self._remaining == 0:
            return b""

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

    def close(self):
        self._closed = True


class PayloadDroppingPolicy(SansIOHTTPPolicy):
    def __init__(self):
        self.put_block_counter = 0
        self.put_block_sizes = []
        self.put_blob_counter = 0
        self.put_blob_sizes = []

    def on_request(self, request):  # type: (PipelineRequest) -> Union[None, Awaitable[None]]
        if _is_put_block_request(request):
            if request.http_request.body:
                self.put_block_counter = self.put_block_counter + 1
                self.put_block_sizes.append(_get_body_length(request))
                replacement = "dummy_body"
                request.http_request.body = replacement
                request.http_request.headers["Content-Length"] = str(len(replacement))
        elif _is_put_blob_request(request):
            if request.http_request.body:
                self.put_blob_counter = self.put_blob_counter + 1
                self.put_blob_sizes.append(_get_body_length(request))
                replacement = "dummy_body"
                request.http_request.body = replacement
                request.http_request.headers["Content-Length"] = str(len(replacement))


def _is_put_block_request(request):
    query = request.http_request.query
    return query and "comp" in query and query["comp"] == "block"

def _is_put_blob_request(request):
    query = request.http_request.query
    return request.http_request.method == "PUT" and not query

def _get_body_length(request):
    body = request.http_request.body
    length = 0
    if hasattr(body, "read"):
        chunk = body.read(10*1024*1024)
        while chunk:
            length = length + len(chunk)
            chunk = body.read(10 * 1024 * 1024)
    else:
        length = len(body)
    return length

# ------------------------------------------------------------------------------
