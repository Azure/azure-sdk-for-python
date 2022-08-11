# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
import pytest
import aiohttp
import asyncio
import requests
import time
import unittest
import os
import uuid
from datetime import datetime, timedelta

from azure.mgmt.storage.aio import StorageManagementClient

from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError, ResourceModifiedError)
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    upload_blob_to_url,
    download_blob_from_url,
)

from azure.storage.blob import (
    generate_blob_sas,
    generate_account_sas,
    generate_container_sas,
    BlobType,
    StorageErrorCode,
    BlobSasPermissions,
    ContainerSasPermissions,
    ContentSettings,
    BlobProperties,
    RetentionPolicy,
    AccessPolicy,
    ResourceTypes,
    AccountSasPermissions,
    StandardBlobTier, RehydratePriority, BlobImmutabilityPolicyMode, ImmutabilityPolicy)

from settings.testcase import BlobPreparer
from devtools_testutils.storage.aio import AsyncStorageTestCase
from test_helpers_async import AsyncStream

# ------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
LARGE_BLOB_SIZE = 64 * 1024 + 5

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


class StorageCommonBlobAsyncTest(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------

    async def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key, transport=AiohttpTestTransport())
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        self.byte_data = self.get_random_bytes(1024)
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass
            try:
                await self.bsc.create_container(self.source_container_name)
            except ResourceExistsError:
                pass

    async def _create_source_blob(self, data):
        blob_client = self.bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX))
        await blob_client.upload_blob(data, overwrite=True)
        return blob_client

    async def _create_blob(self, tags=None, data=b'', **kwargs):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data, tags=tags, overwrite=True, **kwargs)
        return blob

    async def _setup_remote(self, storage_account_name, key):
        self.bsc2 = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
        self.remote_container_name = 'rmt'

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    async def _create_block_blob(self, overwrite=False, tags=None, standard_blob_tier=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(self.byte_data, length=len(self.byte_data), overwrite=overwrite, tags=tags,
                              standard_blob_tier=standard_blob_tier)
        return blob_name

    async def _create_empty_block_blob(self, overwrite=False, tags=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob("", length=0, overwrite=overwrite, tags=tags)
        return blob_name

    async def _create_remote_container(self):
        self.remote_container_name = self.get_resource_name('remotectnr')
        remote_container = self.bsc2.get_container_client(self.remote_container_name)
        try:
            await remote_container.create_container()
        except ResourceExistsError:
            pass

    async def _create_remote_block_blob(self, blob_data=None):
        if not blob_data:
            blob_data = b'12345678' * 1024 * 1024
        source_blob_name = self._get_blob_reference()
        source_blob = self.bsc2.get_blob_client(self.remote_container_name, source_blob_name)
        await source_blob.upload_blob(blob_data, overwrite=True)
        return source_blob

    async def _wait_for_async_copy(self, blob):
        count = 0
        props = await blob.get_blob_properties()
        while props.copy.status == 'pending':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            props = await blob.get_blob_properties()
        return props

    async def _enable_soft_delete(self):
        delete_retention_policy = RetentionPolicy(enabled=True, days=2)
        await self.bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # wait until the policy has gone into effect
        if self.is_live:
            time.sleep(40)

    async def _disable_soft_delete(self):
        delete_retention_policy = RetentionPolicy(enabled=False)
        await self.bsc.set_service_properties(delete_retention_policy=delete_retention_policy)

    def _assert_blob_is_soft_deleted(self, blob):
        self.assertTrue(blob.deleted)
        self.assertIsNotNone(blob.deleted_time)
        self.assertIsNotNone(blob.remaining_retention_days)

    def _assert_blob_not_soft_deleted(self, blob):
        self.assertFalse(blob.deleted)
        self.assertIsNone(blob.deleted_time)
        self.assertIsNone(blob.remaining_retention_days)

    # -- Common test cases for blobs ----------------------------------------------
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_start_copy_from_url_with_oauth(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        # Create source blob
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(data=source_blob_data)
        # Create destination blob
        destination_blob_client = await self._create_blob()
        access_token = await self.generate_oauth_token().get_token("https://storage.azure.com/.default")
        token = "Bearer {}".format(access_token.token)

        with self.assertRaises(HttpResponseError):
            await destination_blob_client.start_copy_from_url(source_blob_client.url, requires_sync=True)
        with self.assertRaises(ValueError):
            await destination_blob_client.start_copy_from_url(
                source_blob_client.url, source_authorization=token, requires_sync=False)

        await destination_blob_client.start_copy_from_url(
            source_blob_client.url, source_authorization=token, requires_sync=True)
        destination_blob = await destination_blob_client.download_blob()
        destination_blob_data = await destination_blob.readall()
        self.assertEqual(source_blob_data, destination_blob_data)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_exists(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        exists = await blob.get_blob_properties()

        # Assert
        self.assertTrue(exists)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_exists_with_if_tags(self, blob_storage_account_name, blob_storage_account_key):
        await self._setup(blob_storage_account_name, blob_storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = await self._create_block_blob(overwrite=True, tags=tags)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        with self.assertRaises(ResourceModifiedError):
            await blob.get_blob_properties(if_tags_match_condition="\"tag1\"='first tag'")
        await blob.get_blob_properties(if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_not_exists(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            await blob.get_blob_properties()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_snapshot_exists(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = await blob.create_snapshot()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=snapshot)
        prop = await blob.get_blob_properties()

        # Assert
        self.assertTrue(prop)
        self.assertEqual(snapshot['snapshot'], prop.snapshot)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_generator(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        # Act
        raw_data = self.get_random_bytes(3 * 1024 * 1024) + b"hello random text"

        def data_generator():
            for i in range(0, 2):
                yield raw_data

        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data=data_generator())
        dl_blob = await blob.download_blob()
        data = await dl_blob.readall()

        # Assert
        self.assertEqual(data, raw_data*2)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_pipe(self, storage_account_name, storage_account_key):
        # Different OSs have different behavior, so this can't be recorded.

        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b"Hello World"

        reader_fd, writer_fd = os.pipe()

        with os.fdopen(writer_fd, 'wb') as writer:
            writer.write(data)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with os.fdopen(reader_fd, mode='rb') as reader:
            await blob.upload_blob(data=reader, overwrite=True)

        blob_data = await (await blob.download_blob()).readall()

        # Assert
        self.assertEqual(data, blob_data)

    @BlobPreparer()
    async def test_upload_blob_from_async_stream_single_chunk(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        data = b"Hello Async World!"
        stream = AsyncStream(data)

        # Act
        await blob.upload_blob(stream, overwrite=True)
        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @BlobPreparer()
    async def test_upload_blob_from_async_stream_chunks(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        data = b"12345" * 1024
        stream = AsyncStream(data)

        # Act
        await blob.upload_blob(stream, overwrite=True)
        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_upload_blob_from_async_stream_chunks_parallel(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        data = b"12345" * 1024
        stream = AsyncStream(data)

        # Act
        await blob.upload_blob(stream, overwrite=True, max_concurrency=3)
        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_snapshot_not_exists(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot="1988-08-18T07:52:31.6690068Z")
        with self.assertRaises(ResourceNotFoundError):
            await blob.get_blob_properties()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_container_not_exists(self, storage_account_name, storage_account_key):
        # In this case both the blob and container do not exist
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self._get_container_reference(), blob_name)
        with self.assertRaises(ResourceNotFoundError):
            await blob.get_blob_properties()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_question_mark(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = '?ques?tion?'
        blob_data = u'???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Assert
        stream = await blob.download_blob()
        data = await stream.readall()
        self.assertIsNotNone(data)
        content = data.decode('utf-8')
        self.assertEqual(content, blob_data)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_equal_sign(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = '=ques=tion!'
        blob_data = u'???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Assert
        stream = await blob.download_blob()
        data = await stream.readall()
        self.assertIsNotNone(data)
        content = data.decode('utf-8')
        self.assertEqual(content, blob_data)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_special_chars(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            await blob.upload_blob(blob_data, length=len(blob_data))

            data = await (await blob.download_blob()).readall()
            content = data.decode('utf-8')
            self.assertEqual(content, blob_data)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_and_download_blob_with_vid(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            resp = await blob.upload_blob(blob_data, length=len(blob_data), overwrite=True)
            self.assertIsNotNone(resp.get('version_id'))

            data = await (await blob.download_blob(version_id=resp.get('version_id'))).readall()
            content = data.decode('utf-8')
            self.assertEqual(content, blob_data)

        # Assert
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_lease_id(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease()

        # Act
        data = b'hello world again'
        resp = await blob.upload_blob(data, length=len(data), lease=lease)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        stream = await blob.download_blob(lease=lease)
        content = await stream.readall()
        self.assertEqual(content, data)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_metadata(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        data = b'hello world'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        md = (await blob.get_blob_properties()).metadata
        self.assertDictEqual(md, metadata)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_with_dictionary_async(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        blob_name = 'test_blob'
        blob_data = {'hello': 'world'}

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with self.assertRaises(TypeError):
            await blob.upload_blob(blob_data)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_generator_async(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)

        # Act
        def gen():
            yield "hello"
            yield "world!"
            yield " eom"
        blob = self.bsc.get_blob_client(self.container_name, "gen_blob")
        resp = await blob.upload_blob(data=gen())

        # Assert
        self.assertIsNotNone(resp.get('etag'))
        content = await (await blob.download_blob()).readall()
        self.assertEqual(content, b"helloworld! eom")

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_requests_async(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        # Act
        uri = "https://en.wikipedia.org/wiki/Microsoft"
        data = requests.get(uri, stream=True)
        blob = self.bsc.get_blob_client(self.container_name, "msft")
        resp = await blob.upload_blob(data=data.raw, overwrite=True)

        self.assertIsNotNone(resp.get('etag'))

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_aiohttp_async(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client(self.container_name, "gutenberg_async")
        # Act
        uri = "https://www.gutenberg.org/files/59466/59466-0.txt"
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as data:
                async for text, _ in data.content.iter_chunks():
                    resp = await blob.upload_blob(data=text, overwrite=True)
                    self.assertIsNotNone(resp.get('etag'))

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_with_existing_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        stream = await blob.download_blob()
        content = await stream.readall()

        # Assert
        self.assertEqual(content, self.byte_data)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_with_snapshot(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snap = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=snap)

        # Act
        stream = await snapshot.download_blob()
        content = await stream.readall()

        # Assert
        self.assertEqual(content, self.byte_data)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_with_snapshot_previous(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snap = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=snap)

        upload_data = b'hello world again'
        await blob.upload_blob(upload_data, length=len(upload_data), overwrite=True)

        # Act
        blob_previous = await snapshot.download_blob()
        blob_previous_bytes = await blob_previous.readall()
        blob_latest = await blob.download_blob()
        blob_latest_bytes = await blob_latest.readall()

        # Assert
        self.assertEqual(blob_previous_bytes, self.byte_data)
        self.assertEqual(blob_latest_bytes, b'hello world again')


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_with_range(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        stream = await blob.download_blob(offset=0, length=5)
        content = await stream.readall()

        # Assert
        self.assertEqual(content, self.byte_data[:5])


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_with_lease(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease()

        # Act
        stream = await blob.download_blob(lease=lease)
        content = await stream.readall()
        await lease.release()

        # Assert
        self.assertEqual(content, self.byte_data)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_with_non_existing_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            await blob.download_blob()


        # Assert
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_properties_with_existing_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
        )

        # Assert
        props = await blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')

    @BlobPreparer()
    async def test_set_blob_properties_with_if_tags(self, blob_storage_account_name, blob_storage_account_key):
        await self._setup(blob_storage_account_name, blob_storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_name = await self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceModifiedError):
            await blob.set_http_headers(content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
                if_tags_match_condition="\"tag1\"='first tag'")
        await blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
            if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'"
        )

        # Assert
        props = await blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_properties_with_blob_settings_param(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = await blob.get_blob_properties()

        # Act
        props.content_settings.content_language = 'spanish'
        props.content_settings.content_disposition = 'inline'
        await blob.set_http_headers(content_settings=props.content_settings)

        # Assert
        props = await blob.get_blob_properties()
        self.assertEqual(props.content_settings.content_language, 'spanish')
        self.assertEqual(props.content_settings.content_disposition, 'inline')


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = await blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.lease.status, 'unlocked')
        self.assertIsNotNone(props.creation_time)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties_returns_rehydrate_priority(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob(standard_blob_tier=StandardBlobTier.Archive)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.set_standard_blob_tier(StandardBlobTier.Hot, rehydrate_priority=RehydratePriority.high)
        props = await blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.rehydrate_priority, 'High')

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties_fail(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)

        with self.assertRaises(HttpResponseError) as e:
            await blob.get_blob_properties()  # Invalid snapshot value of 1


        # Assert
        # TODO: No error code returned
        # self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_metadata_fail(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with self.assertRaises(HttpResponseError) as e:
            (await blob.get_blob_properties()).metadata  # Invalid snapshot value of 1


        # Assert
        # TODO: No error code returned
        # self.assertEqual(StorageErrorCode.invalid_query_parameter_value, e.exception.error_code)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_server_encryption(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = await blob.download_blob()

        # Assert
        self.assertTrue(data.properties.server_encrypted)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties_server_encryption(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = await blob.get_blob_properties()

        # Assert
        self.assertTrue(props.server_encrypted)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_server_encryption(self, storage_account_name, storage_account_key):
        # test can only run live
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        await self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = []
        async for b in container.list_blobs():
            blob_list.append(b)

        # Act

        # Assert
        for blob in blob_list:
            self.assertTrue(blob.server_encrypted)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_no_server_encryption_async(self, storage_account_name, storage_account_key):
        # Arrange
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        self.byte_data = self.get_random_bytes(1024)
        await self.bsc.create_container(self.container_name)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        def callback(response):
            response.http_response.headers['x-ms-server-encrypted'] = 'false'

        props = await blob.get_blob_properties(raw_response_hook=callback)

        # Assert
        self.assertFalse(props.server_encrypted)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties_with_snapshot(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        res = await blob.create_snapshot()
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)

        self.assertEqual(len(blobs), 2)

        # Act
        snapshot = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=res)
        props = await snapshot.get_blob_properties()

        # Assert
        self.assertIsNotNone(blob)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties_with_leased_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease()

        # Act
        props = await blob.get_blob_properties()

        # Assert
        self.assertIsInstance(props, BlobProperties)
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.size, len(self.byte_data))
        self.assertEqual(props.lease.status, 'locked')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.duration, 'infinite')


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_metadata(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = (await blob.get_blob_properties()).metadata

        # Assert
        self.assertIsNotNone(md)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_metadata_with_upper_case(self, storage_account_name, storage_account_key):
        # bug in devtools...converts upper case header to lowercase
        # passes live.
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.set_blob_metadata(metadata)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_set_blob_metadata_with_if_tags(self, blob_storage_account_name, blob_storage_account_key):
        # bug in devtools...converts upper case header to lowercase
        # passes live.
        await self._setup(blob_storage_account_name, blob_storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = await self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceModifiedError):
            await blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1\"='first tag'")
        await blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        md = (await blob.get_blob_properties()).metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @pytest.mark.playback_test_only
    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_metadata_returns_vid(self, storage_account_name, storage_account_key):
        # bug in devtools...converts upper case header to lowercase
        # passes live.
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.set_blob_metadata(metadata)

        # Assert
        self.assertIsNotNone(resp['version_id'])
        md = (await blob.get_blob_properties()).metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['UP'], 'UPval')
        self.assertFalse('up' in md)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blob_with_existing_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.delete_blob()

        # Assert
        self.assertIsNone(resp)

    @BlobPreparer()
    async def test_delete_blob_with_if_tags(self, blob_storage_account_name, blob_storage_account_key):
        await self._setup(blob_storage_account_name, blob_storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = await self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        prop = await blob.get_blob_properties()

        with self.assertRaises(ResourceModifiedError):
            await blob.delete_blob(if_tags_match_condition="\"tag1\"='first tag'")
        resp = await blob.delete_blob(etag=prop.etag, match_condition=MatchConditions.IfNotModified, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        self.assertIsNone(resp)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_specific_blob_version(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self.get_resource_name("blobtodelete")

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.upload_blob(b'abc', overwrite=True)

        # Assert
        self.assertIsNotNone(resp['version_id'])

        # upload to override the previous version
        await blob.upload_blob(b'abc', overwrite=True)

        # Act
        resp = await blob.delete_blob(version_id=resp['version_id'])
        blob_list = []
        async for blob in self.bsc.get_container_client(self.container_name).list_blobs(include="versions"):
            blob_list.append(blob)
        # Assert
        self.assertIsNone(resp)
        self.assertTrue(len(blob_list) > 0)

    @pytest.mark.playback_test_only
    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blob_version_with_blob_sas(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob_client.upload_blob(b'abcde', overwrite=True)

        version_id = resp['version_id']
        self.assertIsNotNone(version_id)
        await blob_client.upload_blob(b'abc', overwrite=True)

        token = generate_blob_sas(
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            version_id=version_id,
            account_key=storage_account_key,
            permission=BlobSasPermissions(delete=True, delete_previous_version=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob_client_using_sas = BlobClient.from_blob_url(blob_client.url, credential=token)
        resp = await blob_client_using_sas.delete_blob(version_id=version_id)

        # Assert
        self.assertIsNone(resp)
        async for blob in self.bsc.get_container_client(self.container_name).list_blobs(include="versions"):
            self.assertNotEqual(blob.version_id, version_id)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blob_with_non_existing_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with self.assertRaises(ResourceNotFoundError):
            await blob.delete_blob()


        # Assert

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blob_snapshot(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snap = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=snap)

        # Act
        await snapshot.delete_blob()

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)
        self.assertEqual(len(blobs), 1)
        self.assertEqual(blobs[0].name, blob_name)
        self.assertIsNone(blobs[0].snapshot)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blob_snapshots(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.create_snapshot()

        # Act
        await blob.delete_blob(delete_snapshots='only')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)
        self.assertEqual(len(blobs), 1)
        self.assertIsNone(blobs[0].snapshot)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_snapshot_returns_vid(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)

        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.create_snapshot()
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)

        # Assert
        self.assertIsNotNone(resp['version_id'])
        # Both create blob and create snapshot will create a new version
        self.assertTrue(len(blobs) >= 2)

        # Act
        await blob.delete_blob(delete_snapshots='only')

        # Assert
        blobs = []
        async for b in container.list_blobs(include=['snapshots', 'versions']):
            blobs.append(b)
        self.assertTrue(len(blobs) > 0)
        self.assertIsNone(blobs[0].snapshot)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_blob_with_snapshots(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.create_snapshot()

        # Act
        # with self.assertRaises(HttpResponseError):
        #    blob.delete_blob()

        await blob.delete_blob(delete_snapshots='include')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)
        self.assertEqual(len(blobs), 0)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_soft_delete_blob_without_snapshots(self, storage_account_name, storage_account_key):
        try:
            # Arrange
            await self._setup(storage_account_name, storage_account_key)
            await self._enable_soft_delete()
            blob_name = await self._create_block_blob()

            container = self.bsc.get_container_client(self.container_name)
            blob = container.get_blob_client(blob_name)

            # Soft delete the blob
            await blob.delete_blob()
            blob_list = []
            async for b in container.list_blobs(include='deleted'):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])


            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = []
            async for b in container.list_blobs():
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete
            await blob.undelete_blob()
            blob_list = []
            async for b in container.list_blobs(include='deleted'):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            await self._disable_soft_delete()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_soft_delete_single_blob_snapshot(self, storage_account_name, storage_account_key):
        try:
            # Arrange
            await self._setup(storage_account_name, storage_account_key)
            await self._enable_soft_delete()
            blob_name = await self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = await blob.create_snapshot()
            blob_snapshot_2 = await blob.create_snapshot()

            # Soft delete blob_snapshot_1
            snapshot_1 = self.bsc.get_blob_client(
                self.container_name, blob_name, snapshot=blob_snapshot_1)
            await snapshot_1.delete_blob()

            with self.assertRaises(ValueError):
                await snapshot_1.delete_blob(delete_snapshots='only')

            container = self.bsc.get_container_client(self.container_name)
            blob_list = []
            async for b in container.list_blobs(include=["snapshots", "deleted"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = []
            async for b in container.list_blobs(include='snapshots'):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 2)

            # Restore snapshot with undelete
            await blob.undelete_blob()
            blob_list = []
            async for b in container.list_blobs(include=["snapshots", "deleted"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)
        finally:
            await self._disable_soft_delete()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_soft_delete_only_snapshots_of_blob(self, storage_account_name, storage_account_key):
        try:
            # Arrange
            await self._setup(storage_account_name, storage_account_key)
            await self._enable_soft_delete()
            blob_name = await self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = await blob.create_snapshot()
            blob_snapshot_2 = await blob.create_snapshot()

            # Soft delete all snapshots
            await blob.delete_blob(delete_snapshots='only')
            container = self.bsc.get_container_client(self.container_name)
            blob_list = []
            async for b in container.list_blobs(include=["snapshots", "deleted"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                if listedblob.snapshot == blob_snapshot_1['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                elif listedblob.snapshot == blob_snapshot_2['snapshot']:
                    self._assert_blob_is_soft_deleted(listedblob)
                else:
                    self._assert_blob_not_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = []
            async for b in container.list_blobs(include="snapshots"):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 1)

            # Restore snapshots with undelete
            await blob.undelete_blob()
            blob_list = []
            async for b in container.list_blobs(include=["snapshots", "deleted"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)

        finally:
            await self._disable_soft_delete()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_soft_delete_blob_including_all_snapshots(self, storage_account_name, storage_account_key):
        try:
            # Arrange
            await self._setup(storage_account_name, storage_account_key)
            await self._enable_soft_delete()
            blob_name = await self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_snapshot_1 = await blob.create_snapshot()
            blob_snapshot_2 = await blob.create_snapshot()

            # Soft delete blob and all snapshots
            await blob.delete_blob(delete_snapshots='include')
            container = self.bsc.get_container_client(self.container_name)
            blob_list = []
            async for b in container.list_blobs(include=["snapshots", "deleted"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 3)
            for listedblob in blob_list:
                self._assert_blob_is_soft_deleted(listedblob)

            # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
            blob_list = []
            async for b in container.list_blobs(include=["snapshots"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob and snapshots with undelete
            await blob.undelete_blob()
            blob_list = []
            async for b in container.list_blobs(include=["snapshots", "deleted"]):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 3)
            for blob in blob_list:
                self._assert_blob_not_soft_deleted(blob)

        finally:
            await self._disable_soft_delete()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_soft_delete_with_leased_blob(self, storage_account_name, storage_account_key):
        try:
            # Arrange
            await self._setup(storage_account_name, storage_account_key)
            await self._enable_soft_delete()
            blob_name = await self._create_block_blob()
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            lease = await blob.acquire_lease()

            # Soft delete the blob without lease_id should fail
            with self.assertRaises(HttpResponseError):
                await blob.delete_blob()

            # Soft delete the blob
            await blob.delete_blob(lease=lease)
            container = self.bsc.get_container_client(self.container_name)
            blob_list = []
            async for b in container.list_blobs(include="deleted"):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_is_soft_deleted(blob_list[0])

            # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
            blob_list = []
            async for b in container.list_blobs():
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 0)

            # Restore blob with undelete, this also gets rid of the lease
            await blob.undelete_blob()
            blob_list = []
            async for b in container.list_blobs(include="deleted"):
                blob_list.append(b)

            # Assert
            self.assertEqual(len(blob_list), 1)
            self._assert_blob_not_soft_deleted(blob_list[0])

        finally:
            await self._disable_soft_delete()

    @BlobPreparer()
    async def test_async_copy_blob_with_if_tags(self, blob_storage_account_name, blob_storage_account_key):
        await self._setup(blob_storage_account_name, blob_storage_account_key)
        source_tags = {"source": "source tag"}
        blob_name = await self._create_block_blob(overwrite=True, tags=source_tags)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        tags1 = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(blob_storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        await copyblob.upload_blob("abc", overwrite=True)
        await copyblob.set_blob_tags(tags=tags1)

        tags = {"tag1": "first tag", "tag2": "secondtag", "tag3": "thirdtag"}
        with self.assertRaises(ResourceModifiedError):
            await copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1\"='first tag'")
        await copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        with self.assertRaises(ResourceModifiedError):
            await copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first taga'")
        dest_tags = await copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first tag'")

        self.assertEqual(len(dest_tags), len(tags))

        with self.assertRaises(ResourceModifiedError):
            await copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='sourcetag'")
        await copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='source tag'")

        with self.assertRaises(ResourceModifiedError):
            await copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='abc'")
        copy = await copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='first tag'")

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        with self.assertRaises(ResourceModifiedError):
            await (await copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc1'")).readall()
        copy_content = await (await copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc'")).readall()
        self.assertEqual(copy_content, self.byte_data)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_copy_blob_returns_vid(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = await copyblob.start_copy_from_url(sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy['version_id'])
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        copy_content = await (await copyblob.download_blob()).readall()
        self.assertEqual(copy_content, self.byte_data)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_copy_blob_with_existing_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = await copyblob.start_copy_from_url(sourceblob)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        copy_content = await (await copyblob.download_blob()).readall()
        self.assertEqual(copy_content, self.byte_data)

    @BlobPreparer()
    async def test_copy_blob_with_immutability_policy(self, versioned_storage_account_name, versioned_storage_account_key, storage_resource_group_name):
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = await self._create_block_blob()
        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(versioned_storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(container_name, 'blob1copy')

        immutability_policy = ImmutabilityPolicy(expiry_time=datetime.utcnow() + timedelta(seconds=5),
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)

        copy = await copyblob.start_copy_from_url(sourceblob, immutability_policy=immutability_policy,
                                                  legal_hold=True,
                                                  )

        download_resp = await copyblob.download_blob()
        self.assertEqual(await download_resp.readall(), self.byte_data)

        self.assertTrue(download_resp.properties['has_legal_hold'])
        self.assertIsNotNone(download_resp.properties['immutability_policy']['expiry_time'])
        self.assertIsNotNone(download_resp.properties['immutability_policy']['policy_mode'])
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))

        if self.is_live:
            await copyblob.delete_immutability_policy()
            await copyblob.set_legal_hold(False)
            await copyblob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    # @BlobPreparer()
    # @AsyncStorageTestCase.await_prepared_test
    # TODO: external copy was supported since 2019-02-02
    # async def test_copy_blob_with_external_blob_fails(self):
    #     # Arrange
    #     await self._setup()
    #     source_blob = "http://www.gutenberg.org/files/59466/59466-0.txt"
    #     copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')
    #
    #     # Act
    #     copy = await copied_blob.start_copy_from_url(source_blob)
    #     self.assertEqual(copy['copy_status'], 'pending')
    #     props = await self._wait_for_async_copy(copied_blob)
    #
    #     # Assert
    #     self.assertEqual(props.copy.status_description, '500 InternalServerError "Copy failed."')
    #     self.assertEqual(props.copy.status, 'failed')
    #     self.assertIsNotNone(props.copy.id)
    #
    # @record
    # def test_copy_blob_with_external_blob_fails(self):
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self._test_copy_blob_with_external_blob_fails())

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_copy_blob_async_private_blob_no_sas(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob()

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)

        # Assert
        with self.assertRaises(ClientAuthenticationError):
            await target_blob.start_copy_from_url(source_blob.url)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_copy_blob_async_private_blob_with_sas(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        sas_token = generate_blob_sas(
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = await target_blob.start_copy_from_url(blob.url)

        # Assert
        props = await self._wait_for_async_copy(target_blob)
        self.assertEqual(props.copy.status, 'success')
        actual_data = await (await target_blob.download_blob()).readall()
        self.assertEqual(actual_data, data)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_abort_copy_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        source_blob = "https://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')

        # Act
        copy = await copied_blob.start_copy_from_url(source_blob)
        self.assertEqual(copy['copy_status'], 'pending')

        await copied_blob.abort_copy(copy)
        props = await self._wait_for_async_copy(copied_blob)
        self.assertEqual(props.copy.status, 'aborted')

        # Assert
        actual_data = await copied_blob.download_blob()
        bytes_data = await (await copied_blob.download_blob()).readall()
        self.assertEqual(bytes_data, b"")
        self.assertEqual(actual_data.properties.copy.status, 'aborted')


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_abort_copy_blob_with_synchronous_copy_fails(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        source_blob_name = await self._create_block_blob()
        source_blob = self.bsc.get_blob_client(self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = await target_blob.start_copy_from_url(source_blob.url)

        with self.assertRaises(HttpResponseError):
            await target_blob.abort_copy(copy_resp)

        # Assert
        self.assertEqual(copy_resp['copy_status'], 'success')


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_snapshot_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.create_snapshot()

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_acquire_and_release(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease()
        await lease.release()
        lease2 = await blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease)
        self.assertIsNotNone(lease2)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_with_duration(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_duration=15)
        resp = await blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(17)

        # Assert
        with self.assertRaises(HttpResponseError):
            await blob.upload_blob(b'hello 3', length=7, lease=lease)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_with_proposed_lease_id(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = await blob.acquire_lease(lease_id=lease_id)

        # Assert
        self.assertEqual(lease.id, lease_id)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_change_lease_id(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = await blob.acquire_lease()
        first_lease_id = lease.id
        await lease.change(lease_id)
        await lease.renew()

        # Assert
        self.assertNotEqual(first_lease_id, lease.id)
        self.assertEqual(lease.id, lease_id)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_break_period(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_duration=15)
        lease_time = await lease.break_lease(lease_break_period=5)

        resp = await blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(5)

        with self.assertRaises(HttpResponseError):
            await blob.upload_blob(b'hello 3', length=7, lease=lease)

        # Assert
        self.assertIsNotNone(lease.id)
        self.assertIsNotNone(lease_time)
        self.assertIsNotNone(resp.get('etag'))


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_acquire_and_renew(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease()
        first_id = lease.id
        await lease.renew()

        # Assert
        self.assertEqual(first_id, lease.id)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_lease_blob_acquire_twice_fails(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease()

        # Act
        with self.assertRaises(HttpResponseError):
            await blob.acquire_lease()

        # Assert
        self.assertIsNotNone(lease.id)


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_unicode_get_blob_unicode_name(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b'hello world')

        # Act
        stream = await blob.download_blob()
        content = await stream.readall()

        # Assert
        self.assertEqual(content, b'hello world')


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_blob_unicode_data(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world啊齄丂狛狜'
        resp = await blob.upload_blob(data)

        # Assert
        self.assertIsNotNone(resp.get('etag'))


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_no_sas_private_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertFalse(response.ok)
        self.assertNotEqual(-1, response.text.find('ResourceNotFound'))

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_no_sas_public_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'a public blob can be read without a shared access signature'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        try:
            container = await self.bsc.create_container(container_name, public_access='blob')
        except ResourceExistsError:
            container = self.bsc.get_container_client(container_name)
        blob = await container.upload_blob(blob_name, data)

        # Act
        response = requests.get(blob.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_public_access_blob(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'public access blob'
        blob_name = 'blob1.txt'
        container_name = self._get_container_reference()
        try:
            container = await self.bsc.create_container(container_name, public_access='blob')
        except ResourceExistsError:
            container = self.bsc.get_container_client(container_name)
        blob = await container.upload_blob(blob_name, data)

        # Act
        service = BlobClient.from_blob_url(blob.url)
        # self._set_test_proxy(service, self.settings)
        content = await (await service.download_blob()).readall()

        # Assert
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_access_blob(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        permission = BlobSasPermissions(read=True, write=True, delete=True, delete_previous_version=True,
                                        permanent_delete=True, list=True, add=True, create=True, update=True)
        self.assertIn('y', str(permission))

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        # self._set_test_proxy(service, self.settings)
        content = await (await service.download_blob()).readall()

        # Assert
        self.assertEqual(self.byte_data, content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_signed_identifier(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = BlobSasPermissions(read=True)
        identifiers = {'testid': access_policy}

        resp = await container.set_container_access_policy(identifiers)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            policy_id='testid')

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        # self._set_test_proxy(service, self.settings)
        result = await (await service.download_blob()).readall()

        # Assert
        self.assertEqual(self.byte_data, result)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_account_sas(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        account_sas_permission = AccountSasPermissions(read=True, write=True, delete=True, add=True,
                                                       permanent_delete=True, list=True)
        self.assertIn('y', str(account_sas_permission))

        token = generate_account_sas(
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            account_sas_permission,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=token)
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=token)
        await container.get_container_properties()
        blob_response = requests.get(blob.url)
        container_response = requests.get(container.url, params={'restype': 'container'})

        # Assert
        self.assertTrue(blob_response.ok)
        self.assertEqual(self.byte_data, blob_response.content)
        self.assertTrue(container_response.ok)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_account_sas_credential(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        token = generate_account_sas(
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=AzureSasCredential(token))
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=AzureSasCredential(token))
        blob_properties = await blob.get_blob_properties()
        container_properties = await container.get_container_properties()

        # Assert
        self.assertEqual(blob_name, blob_properties.name)
        self.assertEqual(self.container_name, container_properties.name)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_azure_named_key_credential_access(self, storage_account_name, storage_account_key):
        named_key = AzureNamedKeyCredential(storage_account_name, storage_account_key)
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), named_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container()

        # Assert
        self.assertTrue(created)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_token_credential(self, storage_account_name, storage_account_key):

        await self._setup(storage_account_name, storage_account_key)
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential, transport=AiohttpTestTransport())
        result = await service.get_service_properties()
        self.assertIsNotNone(result)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=fake_credential, transport=AiohttpTestTransport())
        with self.assertRaises(ClientAuthenticationError):
            await service.get_service_properties()

        # Action 3: update token to make it working again
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential, transport=AiohttpTestTransport())
        result = await service.get_service_properties()
        self.assertIsNotNone(result)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_token_credential_blob(self, storage_account_name, storage_account_key):
        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        blob_data = b'Helloworld'
        token_credential = self.generate_oauth_token()

        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        container = service.get_container_client(container_name)

        # Act / Assert
        try:
            await container.create_container()
            blob = await container.upload_blob(blob_name, blob_data)

            data = await (await blob.download_blob()).readall()
            self.assertEqual(blob_data, data)

            await blob.delete_blob()
        finally:
            await container.delete_container()

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_token_credential_with_batch_operation(self, storage_account_name, storage_account_key):
        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        token_credential = self.generate_oauth_token()
        async with BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential) as service:
            container = service.get_container_client(container_name)
            try:
                await container.create_container()
                await container.upload_blob(blob_name + '1', b'HelloWorld')
                await container.upload_blob(blob_name + '2', b'HelloWorld')
                await container.upload_blob(blob_name + '3', b'HelloWorld')

                delete_batch = []
                blob_list = container.list_blobs(name_starts_with=blob_name)
                async for blob in blob_list:
                    delete_batch.append(blob.name)

                await container.delete_blobs(*delete_batch)
            finally:
                await container.delete_container()

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_shared_read_access_blob(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        await self._setup(storage_account_name, storage_account_key)
        # Arrange
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        self.assertEqual(self.byte_data, response.content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_shared_read_access_blob_with_content_query_params(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertEqual(self.byte_data, response.content)
        self.assertEqual(response.headers['cache-control'], 'no-cache')
        self.assertEqual(response.headers['content-disposition'], 'inline')
        self.assertEqual(response.headers['content-encoding'], 'utf-8')
        self.assertEqual(response.headers['content-language'], 'fr')
        self.assertEqual(response.headers['content-type'], 'text')

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_shared_write_access_blob(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        updated_data = b'updated blob data'
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        headers = {'x-ms-blob-type': 'BlockBlob'}
        response = requests.put(sas_blob.url, headers=headers, data=updated_data)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        data = await (await blob.download_blob()).readall()
        self.assertEqual(updated_data, data)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_shared_delete_access_blob(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.delete(sas_blob.url)

        # Assert
        response.raise_for_status()
        self.assertTrue(response.ok)
        with self.assertRaises(HttpResponseError):
            await sas_blob.download_blob()


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_account_information(self, storage_account_name, storage_account_key):
        # Act
        await self._setup(storage_account_name, storage_account_key)
        info = await self.bsc.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_account_information_with_container_name(self, storage_account_name, storage_account_key):
        # Act
        # Container name gets ignored
        await self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client("missing")
        info = await container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))


    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_account_information_with_blob_name(self, storage_account_name, storage_account_key):
        # Act
        # Both container and blob names get ignored
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client("missing", "missing")
        info = await blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_account_information_with_container_sas(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        permission = ContainerSasPermissions(read=True, write=True, delete=True, delete_previous_version=True,
                                             list=True, tag=True, set_immutability_policy=True,
                                             permanent_delete=True)
        self.assertIn('y', str(permission))
        token = generate_container_sas(
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_container = ContainerClient.from_container_url(container.url, credential=token)

        # Act
        info = await sas_container.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_account_information_with_blob_sas(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        info = await sas_blob.get_account_information()

        # Assert
        self.assertIsNotNone(info.get('sku_name'))
        self.assertIsNotNone(info.get('account_kind'))

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_download_to_file_with_sas(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        sas_token = generate_blob_sas(
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        FILE_PATH = '_to_file_with_sas.async.{}.dat'.format(str(uuid.uuid4()))
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)

        # Act
        await download_blob_from_url(blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_download_to_file_with_credential(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'to_file_with_credential.async.{}.dat'.format(str(uuid.uuid4()))
        # Act
        await download_blob_from_url(
            source_blob.url, FILE_PATH,
            max_concurrency=2,
            credential=secondary_storage_account_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_download_to_stream_with_credential(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'to_stream_with_credential.async.{}.dat'.format(str(uuid.uuid4()))
        # Act
        with open(FILE_PATH, 'wb') as stream:
            await download_blob_from_url(
                source_blob.url, stream,
                max_concurrency=2,
                credential=secondary_storage_account_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_download_to_file_with_existing_file(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'with_existing_file.async.{}.dat'.format(str(uuid.uuid4()))
        # Act
        await download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=secondary_storage_account_key)

        with self.assertRaises(ValueError):
            await download_blob_from_url(source_blob.url, FILE_PATH)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_download_to_file_with_existing_file_overwrite(self, storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        FILE_PATH = 'existing_file_overwrite.async.{}.dat'.format(str(uuid.uuid4()))
        # Act
        await download_blob_from_url(
            source_blob.url, FILE_PATH,
            credential=secondary_storage_account_key)

        data2 = b'ABCDEFGH' * 1024 * 1024
        source_blob = await self._create_remote_block_blob(blob_data=data2)
        await download_blob_from_url(
            source_blob.url, FILE_PATH, overwrite=True,
            credential=secondary_storage_account_key)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data2, actual)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_to_url_bytes_with_sas(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        uploaded = await upload_blob_to_url(sas_blob.url, data)

        # Assert
        self.assertIsNotNone(uploaded)
        content = await (await blob.download_blob()).readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_to_url_bytes_with_credential(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = await upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = await (await blob.download_blob()).readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_to_url_bytes_with_existing_blob(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b"existing_data")

        # Act
        with self.assertRaises(ResourceExistsError):
            await upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        content = await (await blob.download_blob()).readall()
        self.assertEqual(b"existing_data", content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_to_url_bytes_with_existing_blob_overwrite(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b"existing_data")

        # Act
        uploaded = await upload_blob_to_url(
            blob.url, data,
            overwrite=True,
            credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = await (await blob.download_blob()).readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_to_url_text_with_credential(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = '12345678' * 1024 * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = await upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        stream = await blob.download_blob(encoding='UTF-8')
        content = await stream.readall()
        self.assertEqual(data, content)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_to_url_file_with_credential(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        FILE_PATH = 'url_file_with_credential.async.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        with open(FILE_PATH, 'rb'):
            uploaded = await upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        self.assertIsNotNone(uploaded)
        content = await (await blob.download_blob()).readall()
        self.assertEqual(data, content)
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_transport_closed_only_once(self, storage_account_name, storage_account_key):
        container_name = self.get_resource_name('utcontainerasync')
        transport = AioHttpTransport()
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, transport=transport)
        blob_name = self._get_blob_reference()
        async with bsc:
            await bsc.get_service_properties()
            assert transport.session is not None
            async with bsc.get_blob_client(container_name, blob_name) as bc:
                assert transport.session is not None
            await bsc.get_service_properties()
            assert transport.session is not None

    @BlobPreparer()
    async def test_blob_immutability_policy(self, versioned_storage_account_name, versioned_storage_account_key, storage_resource_group_name):
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        await blob.upload_blob(b"abc", overwrite=True)

        immutability_policy = ImmutabilityPolicy(expiry_time=datetime.utcnow() + timedelta(seconds=5),
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp = await blob.set_immutability_policy(
            immutability_policy=immutability_policy)

        # Assert
        # check immutability policy after set_immutability_policy()
        props = await blob.get_blob_properties()
        self.assertIsNotNone(resp['immutability_policy_until_date'])
        self.assertIsNotNone(resp['immutability_policy_mode'])
        self.assertIsNotNone(props['immutability_policy']['expiry_time'])
        self.assertIsNotNone(props['immutability_policy']['policy_mode'])
        self.assertEqual(props['immutability_policy']['policy_mode'], "unlocked")

        # check immutability policy after delete_immutability_policy()
        await blob.delete_immutability_policy()
        props = await blob.get_blob_properties()
        self.assertIsNone(props['immutability_policy']['policy_mode'])
        self.assertIsNone(props['immutability_policy']['policy_mode'])

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @BlobPreparer()
    async def test_blob_legal_hold(self, versioned_storage_account_name, versioned_storage_account_key, storage_resource_group_name):
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        await blob.upload_blob(b"abc", overwrite=True)
        resp = await blob.set_legal_hold(True)
        props = await blob.get_blob_properties()

        with self.assertRaises(HttpResponseError):
            await blob.delete_blob()

        self.assertTrue(resp['legal_hold'])
        self.assertTrue(props['has_legal_hold'])

        resp2 = await blob.set_legal_hold(False)
        props2 = await blob.get_blob_properties()

        self.assertFalse(resp2['legal_hold'])
        self.assertFalse(props2['has_legal_hold'])

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @BlobPreparer()
    async def test_download_blob_with_immutability_policy(self, versioned_storage_account_name, versioned_storage_account_key, storage_resource_group_name):
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        content = b"abcedfg"

        immutability_policy = ImmutabilityPolicy(expiry_time=datetime.utcnow() + timedelta(seconds=5),
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        await blob.upload_blob(content,
                               immutability_policy=immutability_policy,
                               legal_hold=True,
                               overwrite=True)

        download_resp = await blob.download_blob()

        with self.assertRaises(HttpResponseError):
            await blob.delete_blob()

        self.assertTrue(download_resp.properties['has_legal_hold'])
        self.assertIsNotNone(download_resp.properties['immutability_policy']['expiry_time'])
        self.assertIsNotNone(download_resp.properties['immutability_policy']['policy_mode'])

        # Cleanup
        await blob.set_legal_hold(False)
        await blob.delete_immutability_policy()

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @BlobPreparer()
    async def test_list_blobs_with_immutability_policy(self, versioned_storage_account_name, versioned_storage_account_key, storage_resource_group_name):
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        container_client = self.bsc.get_container_client(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        content = b"abcedfg"

        immutability_policy = ImmutabilityPolicy(expiry_time=datetime.utcnow() + timedelta(seconds=5),
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        await blob.upload_blob(content,
                               immutability_policy=immutability_policy,
                               legal_hold=True,
                               overwrite=True)

        blob_list = list()
        async for blob_prop in container_client.list_blobs(include=['immutabilitypolicy', 'legalhold']):
            blob_list.append(blob_prop)

        self.assertTrue(blob_list[0]['has_legal_hold'])
        self.assertIsNotNone(blob_list[0]['immutability_policy']['expiry_time'])
        self.assertIsNotNone(blob_list[0]['immutability_policy']['policy_mode'])

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @BlobPreparer()
    async def test_validate_empty_blob(self, storage_account_name, storage_account_key):
        """Test that we can upload an empty blob with validate=True."""
        await self._setup(storage_account_name, storage_account_key)

        blob_name = self.get_resource_name("utcontainer")
        container_client = self.bsc.get_container_client(self.container_name)
        await container_client.upload_blob(blob_name, b"", validate_content=True)

        blob_client = container_client.get_blob_client(blob_name)

        assert await blob_client.exists()
        assert (await blob_client.get_blob_properties()).size == 0

# ------------------------------------------------------------------------------
