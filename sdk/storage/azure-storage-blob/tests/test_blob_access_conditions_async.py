# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import asyncio

import datetime
import os
import unittest

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceModifiedError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    LeaseClient,
    StorageErrorCode,
    BlobBlock,
    BlobType,
    ContentSettings,
    BlobProperties
)
from testcase import (
    StorageTestCase,
    record,
    TestMode
)

# ------------------------------------------------------------------------------
LARGE_APPEND_BLOB_SIZE = 64 * 1024
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


class StorageBlobAccessConditionsTestAsync(StorageTestCase):

    def setUp(self):
        super(StorageBlobAccessConditionsTestAsync, self).setUp()

        url = self._get_account_url()
        self.bsc = BlobServiceClient(
            url,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            connection_data_block_size = 4 * 1024,
            transport=AiohttpTestTransport()
        )
        self.container_name = self.get_resource_name('utcontainer')

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.bsc.delete_container(self.container_name))
            except:
                pass

        return super(StorageBlobAccessConditionsTestAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    async def _create_container(self, container_name):
        container = self.bsc.get_container_client(container_name)
        await container.create_container()
        return container

    async def _create_container_and_block_blob(self, container_name, blob_name, blob_data):
        container = await self._create_container(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        resp = await blob.upload_blob(blob_data, length=len(blob_data))
        self.assertIsNotNone(resp.get('etag'))
        return container, blob

    async def _create_container_and_page_blob(self, container_name, blob_name, content_length):
        container = await self._create_container(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        resp = await blob.create_page_blob(str(content_length))
        return container, blob

    async def _create_container_and_append_blob(self, container_name, blob_name):
        container = await self._create_container(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        resp = await blob.create_append_blob()
        return container, blob

    # --Test cases for blob service --------------------------------------------

    async def _test_set_container_metadata_with_if_modified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '43'}
        await container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = (await container.get_container_properties()).metadata
        self.assertDictEqual(metadata, md)

    @record
    def test_set_container_metadata_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_container_metadata_with_if_modified_async())

    async def _test_set_container_metadata_with_if_modified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '43'}
            await container.set_container_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_container_metadata_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_container_metadata_with_if_modified_fail_async())

    async def _test_set_container_acl_with_if_modified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        await container.set_container_access_policy(if_modified_since=test_datetime)

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)

    @record
    def test_set_container_acl_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_container_acl_with_if_modified_async())

    async def _test_set_container_acl_with_if_modified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await container.set_container_access_policy(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_container_acl_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_container_acl_with_if_modified_fail_async())

    async def _test_set_container_acl_with_if_unmodified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        await container.set_container_access_policy(if_unmodified_since=test_datetime)

        # Assert
        acl = await container.get_container_access_policy()
        self.assertIsNotNone(acl)

    @record
    def test_set_container_acl_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_container_acl_with_if_unmodified_async())

    async def _test_set_container_acl_with_if_unmodified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await container.set_container_access_policy(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_container_acl_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_container_acl_with_if_unmodified_fail_async())

    async def _test_lease_container_acquire_with_if_modified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        lease = await container.acquire_lease(if_modified_since=test_datetime)
        await lease.break_lease()

        # Assert

    @record
    def test_lease_container_acquire_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_container_acquire_with_if_modified_async())

    async def _test_lease_container_acquire_with_if_modified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await container.acquire_lease(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_lease_container_acquire_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_container_acquire_with_if_modified_fail_async())

    async def _test_lease_container_acquire_with_if_unmodified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        lease = await container.acquire_lease(if_unmodified_since=test_datetime)
        await lease.break_lease()

        # Assert

    @record
    def test_lease_container_acquire_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_container_acquire_with_if_unmodified_async())

    async def _test_lease_container_acquire_with_if_unmodified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await container.acquire_lease(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_lease_container_acquire_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_container_acquire_with_if_unmodified_fail_async())

    async def _test_delete_container_with_if_modified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        deleted = await container.delete_container(if_modified_since=test_datetime)

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            await container.get_container_properties()

    @record
    def test_delete_container_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_container_with_if_modified_async())

    async def _test_delete_container_with_if_modified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await container.delete_container(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_delete_container_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_container_with_if_modified_fail_async())

    async def _test_delete_container_with_if_unmodified_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        await container.delete_container(if_unmodified_since=test_datetime)

        # Assert
        with self.assertRaises(ResourceNotFoundError):
            await container.get_container_properties()

    @record
    def test_delete_container_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_container_with_if_unmodified_async())

    async def _test_delete_container_with_if_unmodified_fail_async(self):
        # Arrange
        container = await self._create_container(self.container_name)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await container.delete_container(if_unmodified_since=test_datetime)

        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_delete_container_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_container_with_if_unmodified_fail_async())

    async def _test_put_blob_with_if_modified_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        resp = await blob.upload_blob(data, length=len(data), if_modified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp.get('etag'))

    @record
    def test_put_blob_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_modified_async())

    async def _test_put_blob_with_if_modified_fail_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), if_modified_since=test_datetime, overwrite=True)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_blob_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_modified_fail_async())

    async def _test_put_blob_with_if_unmodified_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        resp = await blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp.get('etag'))

    @record
    def test_put_blob_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_unmodified_async())

    async def _test_put_blob_with_if_unmodified_fail_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), if_unmodified_since=test_datetime, overwrite=True)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_blob_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_unmodified_fail_async())

    async def _test_put_blob_with_if_match_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        etag = (await blob.get_blob_properties()).etag

        # Act
        resp = await blob.upload_blob(data, length=len(data), if_match=etag)

        # Assert
        self.assertIsNotNone(resp.get('etag'))

    @record
    def test_put_blob_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_match_async())

    async def _test_put_blob_with_if_match_fail_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), if_match='0x111111111111111', overwrite=True)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_blob_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_match_fail_async())

    async def _test_put_blob_with_if_none_match_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)

        # Act
        resp = await blob.upload_blob(data, length=len(data), if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(resp.get('etag'))

    @record
    def test_put_blob_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_none_match_async())

    async def _test_put_blob_with_if_none_match_fail_async(self):
        # Arrange
        data = b'hello world'
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', data)
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_blob(data, length=len(data), if_none_match=etag, overwrite=True)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_blob_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_blob_with_if_none_match_fail_async())

    async def _test_get_blob_with_if_modified_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        content = await blob.download_blob(if_modified_since=test_datetime)
        content = await content.content_as_bytes()

        # Assert
        self.assertEqual(content, b'hello world')

    @record
    def test_get_blob_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_modified_async())

    async def _test_get_blob_with_if_modified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.download_blob(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_modified_fail_async())

    async def _test_get_blob_with_if_unmodified_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        content = await blob.download_blob(if_unmodified_since=test_datetime)
        content = await content.content_as_bytes()

        # Assert
        self.assertEqual(content, b'hello world')

    @record
    def test_get_blob_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_unmodified_async())

    async def _test_get_blob_with_if_unmodified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.download_blob(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_unmodified_fail_async())

    async def _test_get_blob_with_if_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        etag = (await blob.get_blob_properties()).etag

        # Act
        content = await blob.download_blob(if_match=etag)
        content = await content.content_as_bytes()

        # Assert
        self.assertEqual(content, b'hello world')

    @record
    def test_get_blob_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_match_async())

    async def _test_get_blob_with_if_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.download_blob(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_match_fail_async())

    async def _test_get_blob_with_if_none_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        content = await blob.download_blob(if_none_match='0x111111111111111')
        content = await content.content_as_bytes()

        # Assert
        self.assertEqual(content, b'hello world')

    @record
    def test_get_blob_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_none_match_async())

    async def _test_get_blob_with_if_none_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.download_blob(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_with_if_none_match_fail_async())

    async def _test_set_blob_properties_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_http_headers(content_settings, if_modified_since=test_datetime)

        # Assert
        properties = await blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_modified_async())

    async def _test_set_blob_properties_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_http_headers(content_settings, if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_properties_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_modified_fail_async())

    async def _test_set_blob_properties_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_http_headers(content_settings, if_unmodified_since=test_datetime)

        # Assert
        properties = await blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_unmodified_async())

    async def _test_set_blob_properties_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_http_headers(content_settings, if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_properties_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_unmodified_fail_async())

    async def _test_set_blob_properties_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        await blob.set_http_headers(content_settings, if_match=etag)

        # Assert
        properties = await blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_match_async())

    async def _test_set_blob_properties_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_http_headers(content_settings, if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_properties_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_match_fail_async())

    async def _test_set_blob_properties_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_http_headers(content_settings, if_none_match='0x111111111111111')

        # Assert
        properties = await blob.get_blob_properties()
        self.assertEqual(content_settings.content_language, properties.content_settings.content_language)
        self.assertEqual(content_settings.content_disposition, properties.content_settings.content_disposition)

    @record
    def test_set_blob_properties_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_none_match_async())

    async def _test_set_blob_properties_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            content_settings = ContentSettings(
                content_language='spanish',
                content_disposition='inline')
            await blob.set_http_headers(content_settings, if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_properties_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_properties_with_if_none_match_fail_async())

    async def _test_get_blob_properties_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        properties = await blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        self.assertIsInstance(properties, BlobProperties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.size, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_modified_async())

    async def _test_get_blob_properties_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_properties_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_modified_fail_async())

    async def _test_get_blob_properties_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        properties = await blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.size, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_unmodified_async())

    async def _test_get_blob_properties_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_properties_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_unmodified_fail_async())

    async def _test_get_blob_properties_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        properties = await blob.get_blob_properties(if_match=etag)

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.size, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_match_async())

    async def _test_get_blob_properties_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_properties_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_match_fail_async())

    async def _test_get_blob_properties_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        properties = await blob.get_blob_properties(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(properties)
        self.assertEqual(properties.blob_type.value, 'BlockBlob')
        self.assertEqual(properties.size, 11)
        self.assertEqual(properties.lease.status, 'unlocked')

    @record
    def test_get_blob_properties_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_none_match_async())

    async def _test_get_blob_properties_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.get_blob_properties(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_properties_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_properties_with_if_none_match_fail_async())

    async def _test_get_blob_metadata_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        md = (await blob.get_blob_properties(if_modified_since=test_datetime)).metadata

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_modified_async())

    async def _test_get_blob_metadata_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_metadata_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_modified_fail_async())

    async def _test_get_blob_metadata_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        md = (await blob.get_blob_properties(if_unmodified_since=test_datetime)).metadata

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_unmodified_async())

    async def _test_get_blob_metadata_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_metadata_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_unmodified_fail_async())

    async def _test_get_blob_metadata_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        md = (await blob.get_blob_properties(if_match=etag)).metadata

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_match_async())

    async def _test_get_blob_metadata_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.get_blob_properties(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_metadata_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_match_fail_async())

    async def _test_get_blob_metadata_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        md = (await blob.get_blob_properties(if_none_match='0x111111111111111')).metadata

        # Assert
        self.assertIsNotNone(md)

    @record
    def test_get_blob_metadata_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_none_match_async())

    async def _test_get_blob_metadata_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.get_blob_properties(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_blob_metadata_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_blob_metadata_with_if_none_match_fail_async())

    async def _test_set_blob_metadata_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_modified_async())

    async def _test_set_blob_metadata_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_blob_metadata(metadata, if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_metadata_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_modified_fail_async())

    async def _test_set_blob_metadata_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_unmodified_async())

    async def _test_set_blob_metadata_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_blob_metadata(metadata, if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_metadata_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_unmodified_fail_async())

    async def _test_set_blob_metadata_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        await blob.set_blob_metadata(metadata, if_match=etag)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_match_async())

    async def _test_set_blob_metadata_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.set_blob_metadata(metadata, if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_metadata_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_match_fail_async())

    async def _test_set_blob_metadata_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        metadata = {'hello': 'world', 'number': '42'}
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.set_blob_metadata(metadata, if_none_match='0x111111111111111')

        # Assert
        md = (await blob.get_blob_properties()).metadata
        self.assertDictEqual(metadata, md)

    @record
    def test_set_blob_metadata_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_none_match_async())

    async def _test_set_blob_metadata_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            metadata = {'hello': 'world', 'number': '42'}
            await blob.set_blob_metadata(metadata, if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_set_blob_metadata_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_blob_metadata_with_if_none_match_fail_async())

    async def _test_delete_blob_with_if_modified_async(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_modified_async())

    async def _test_delete_blob_with_if_modified_fail_async(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.delete_blob(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_delete_blob_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_modified_fail_async())

    async def _test_delete_blob_with_if_unmodified_async(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_unmodified_async())

    async def _test_delete_blob_with_if_unmodified_fail_async(self):
        # Arrange
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.delete_blob(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_delete_blob_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_unmodified_fail_async())

    async def _test_delete_blob_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act

        resp = await blob.delete_blob(if_match=etag)

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_match_async())

    async def _test_delete_blob_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.delete_blob(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_delete_blob_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_match_fail_async())

    async def _test_delete_blob_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.delete_blob(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNone(resp)

    @record
    def test_delete_blob_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_none_match_async())

    async def _test_delete_blob_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.delete_blob(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_delete_blob_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_blob_with_if_none_match_fail_async())

    async def _test_snapshot_blob_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])

    @record
    def test_snapshot_blob_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_modified_async())

    async def _test_snapshot_blob_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.create_snapshot(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_snapshot_blob_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_modified_fail_async())

    async def _test_snapshot_blob_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])

    @record
    def test_snapshot_blob_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_unmodified_async())

    async def _test_snapshot_blob_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.create_snapshot(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_snapshot_blob_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_unmodified_fail_async())

    async def _test_snapshot_blob_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        resp = await blob.create_snapshot(if_match=etag)

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])

    @record
    def test_snapshot_blob_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_match_async())

    async def _test_snapshot_blob_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.create_snapshot(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_snapshot_blob_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_match_fail_async())

    async def _test_snapshot_blob_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        resp = await blob.create_snapshot(if_none_match='0x111111111111111')

        # Assert
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['snapshot'])

    @record
    def test_snapshot_blob_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_none_match_async())

    async def _test_snapshot_blob_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.create_snapshot(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_snapshot_blob_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_snapshot_blob_with_if_none_match_fail_async())

    async def _test_lease_blob_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        lease = await blob.acquire_lease(
            if_modified_since=test_datetime,
            lease_id=test_lease_id)

        await lease.break_lease()

        # Assert
        self.assertIsInstance(lease, LeaseClient)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_modified_async())

    async def _test_lease_blob_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            blob = self.bsc.get_blob_client(self.container_name, 'blob1')
            await blob.acquire_lease(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_lease_blob_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_modified_fail_async())

    async def _test_lease_blob_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_lease_id = '00000000-1111-2222-3333-444444444444'
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        lease = await blob.acquire_lease(
            if_unmodified_since=test_datetime,
            lease_id=test_lease_id)

        await lease.break_lease()

        # Assert
        self.assertIsInstance(lease, LeaseClient)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_unmodified_async())

    async def _test_lease_blob_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.acquire_lease(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_lease_blob_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_unmodified_fail_async())

    async def _test_lease_blob_with_if_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        lease = await blob.acquire_lease(
            lease_id=test_lease_id,
            if_match=etag)

        await lease.break_lease()

        # Assert
        self.assertIsInstance(lease, LeaseClient)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_match_async())

    async def _test_lease_blob_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.acquire_lease(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_lease_blob_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_match_fail_async())

    async def _test_lease_blob_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        test_lease_id = '00000000-1111-2222-3333-444444444444'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        lease = await blob.acquire_lease(
            lease_id=test_lease_id,
            if_none_match='0x111111111111111')

        await lease.break_lease()

        # Assert
        self.assertIsInstance(lease, LeaseClient)
        self.assertIsNotNone(lease.id)

    @record
    def test_lease_blob_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_none_match_async())

    async def _test_lease_blob_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'hello world')
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.acquire_lease(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_lease_blob_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_lease_blob_with_if_none_match_fail_async())

    async def _test_put_block_list_with_if_modified_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, if_modified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_modified_async())

    async def _test_put_block_list_with_if_modified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_block_list_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_modified_fail_async())

    async def _test_put_block_list_with_if_unmodified_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, if_unmodified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_unmodified_async())

    async def _test_put_block_list_with_if_unmodified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_block_list_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_unmodified_fail_async())

    async def _test_put_block_list_with_if_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        etag = (await blob.get_blob_properties()).etag

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, if_match=etag)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_match_async())

    async def _test_put_block_list_with_if_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.commit_block_list(
                [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')],
                if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_block_list_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_match_fail_async())

    async def _test_put_block_list_with_if_none_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, if_none_match='0x111111111111111')

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(content, b'AAABBBCCC')

    @record
    def test_put_block_list_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_none_match_async())

    async def _test_put_block_list_with_if_none_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_block_blob(
            self.container_name, 'blob1', b'')
        await asyncio.gather(*[
            blob.stage_block('1', b'AAA'),
            blob.stage_block('2', b'BBB'),
            blob.stage_block('3', b'CCC')])
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
            await blob.commit_block_list(block_list, if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_put_block_list_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_if_none_match_fail_async())

    async def _test_update_page_with_if_modified_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.upload_page(data, offset=0, length=512, if_modified_since=test_datetime)

        # Assert

    @record
    def test_update_page_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_modified_async())

    async def _test_update_page_with_if_modified_fail_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_update_page_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_modified_fail_async())

    async def _test_update_page_with_if_unmodified_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.upload_page(data, offset=0, length=512, if_unmodified_since=test_datetime)

        # Assert

    @record
    def test_update_page_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_unmodified_async())

    async def _test_update_page_with_if_unmodified_fail_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_update_page_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_unmodified_fail_async())

    async def _test_update_page_with_if_match_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        await blob.upload_page(data, offset=0, length=512, if_match=etag)

        # Assert

    @record
    def test_update_page_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_match_async())

    async def _test_update_page_with_if_match_fail_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_update_page_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_match_fail_async())

    async def _test_update_page_with_if_none_match_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32

        # Act
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        await blob.upload_page(data, offset=0, length=512, if_none_match='0x111111111111111')

        # Assert

    @record
    def test_update_page_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_none_match_async())

    async def _test_update_page_with_if_none_match_fail_async(self):
        # Arrange
        await self._create_container_and_page_blob(
            self.container_name, 'blob1', 1024)
        data = b'abcdefghijklmnop' * 32
        blob = self.bsc.get_blob_client(self.container_name, 'blob1')
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.upload_page(data, offset=0, length=512, if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_update_page_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_update_page_with_if_none_match_fail_async())

    async def _test_get_page_ranges_iter_with_if_modified_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        ranges = await blob.get_page_ranges(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(len(ranges[0]), 2)
        self.assertEqual(ranges[0][0], {'start': 0, 'end': 511})
        self.assertEqual(ranges[0][1], {'start': 1024, 'end': 1535})

    @record
    def test_get_page_ranges_iter_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_modified_async())

    async def _test_get_page_ranges_iter_with_if_modified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.get_page_ranges(if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_page_ranges_iter_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_modified_fail_async())

    async def _test_get_page_ranges_iter_with_if_unmodified_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        ranges = await blob.get_page_ranges(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(len(ranges[0]), 2)
        self.assertEqual(ranges[0][0], {'start': 0, 'end': 511})
        self.assertEqual(ranges[0][1], {'start': 1024, 'end': 1535})

    @record
    def test_get_page_ranges_iter_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_unmodified_async())

    async def _test_get_page_ranges_iter_with_if_unmodified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.get_page_ranges(if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_page_ranges_iter_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_unmodified_fail_async())

    async def _test_get_page_ranges_iter_with_if_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))
        etag = (await blob.get_blob_properties()).etag

        # Act
        ranges = await blob.get_page_ranges(if_match=etag)

        # Assert
        self.assertEqual(len(ranges[0]), 2)
        self.assertEqual(ranges[0][0], {'start': 0, 'end': 511})
        self.assertEqual(ranges[0][1], {'start': 1024, 'end': 1535})

    @record
    def test_get_page_ranges_iter_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_match_async())

    async def _test_get_page_ranges_iter_with_if_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.get_page_ranges(if_match='0x111111111111111')

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_page_ranges_iter_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_match_fail_async())

    async def _test_get_page_ranges_iter_with_if_none_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32
        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))

        # Act
        ranges = await blob.get_page_ranges(if_none_match='0x111111111111111')

        # Assert
        self.assertEqual(len(ranges[0]), 2)
        self.assertEqual(ranges[0][0], {'start': 0, 'end': 511})
        self.assertEqual(ranges[0][1], {'start': 1024, 'end': 1535})

    @record
    def test_get_page_ranges_iter_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_none_match_async())

    async def _test_get_page_ranges_iter_with_if_none_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_page_blob(
            self.container_name, 'blob1', 2048)
        data = b'abcdefghijklmnop' * 32

        await asyncio.gather(blob.upload_page(data, offset=0, length=512), blob.upload_page(data, offset=1024, length=512))
        etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            await blob.get_page_ranges(if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_get_page_ranges_iter_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_page_ranges_iter_with_if_none_match_fail_async())

    async def _test_append_block_with_if_modified_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i), if_modified_since=test_datetime)
            self.assertIsNotNone(resp)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(b'block 0block 1block 2block 3block 4', content)

    @record
    def test_append_block_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_modified_async())

    async def _test_append_block_with_if_modified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            for i in range(5):
                resp = await blob.append_block(u'block {0}'.format(i), if_modified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_block_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_modified_fail_async())

    async def _test_append_block_with_if_unmodified_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() +
                         datetime.timedelta(minutes=15))
        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i), if_unmodified_since=test_datetime)
            self.assertIsNotNone(resp)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(b'block 0block 1block 2block 3block 4', content)

    @record
    def test_append_block_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_unmodified_async())

    async def _test_append_block_with_if_unmodified_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')
        test_datetime = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=15))
        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            for i in range(5):
                resp = await blob.append_block(u'block {0}'.format(i), if_unmodified_since=test_datetime)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_block_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_unmodified_fail_async())

    async def _test_append_block_with_if_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        for i in range(5):
            etag = (await blob.get_blob_properties()).etag
            resp = await blob.append_block(u'block {0}'.format(i), if_match=etag)
            self.assertIsNotNone(resp)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(b'block 0block 1block 2block 3block 4', content)

    @record
    def test_append_block_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_match_async())

    async def _test_append_block_with_if_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        with self.assertRaises(HttpResponseError) as e:
            for i in range(5):
                resp = await blob.append_block(u'block {0}'.format(i), if_match='0x111111111111111')

        # Assert
        #self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_block_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_match_fail_async())

    async def _test_append_block_with_if_none_match_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i), if_none_match='0x8D2C9167D53FC2C')
            self.assertIsNotNone(resp)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(b'block 0block 1block 2block 3block 4', content)

    @record
    def test_append_block_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_none_match_async())

    async def _test_append_block_with_if_none_match_fail_async(self):
        # Arrange
        container, blob = await self._create_container_and_append_blob(self.container_name, 'blob1')

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            for i in range(5):
                etag = (await blob.get_blob_properties()).etag
                resp = await blob.append_block(u'block {0}'.format(i), if_none_match=etag)

        # Assert
        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_block_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_if_none_match_fail_async())

    async def _test_append_blob_from_bytes_with_if_modified_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (datetime.datetime.utcnow() - datetime.timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_modified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(data, content)

    @record
    def test_append_blob_from_bytes_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_modified_async())

    async def _test_append_blob_from_bytes_with_if_modified_fail_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (datetime.datetime.utcnow() + datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_modified_since=test_datetime)

        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_blob_from_bytes_with_if_modified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_modified_fail_async())

    async def _test_append_blob_from_bytes_with_if_unmodified_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (datetime.datetime.utcnow() + datetime.timedelta(minutes=15))

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_unmodified_since=test_datetime)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(data, content)

    @record
    def test_append_blob_from_bytes_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_unmodified_async())

    async def _test_append_blob_from_bytes_with_if_unmodified_fail_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_datetime = (datetime.datetime.utcnow() - datetime.timedelta(minutes=15))

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_unmodified_since=test_datetime)

        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_blob_from_bytes_with_if_unmodified_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_unmodified_fail_async())

    async def _test_append_blob_from_bytes_with_if_match_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = (await blob.get_blob_properties()).etag

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_match=test_etag)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(data, content)

    @record
    def test_append_blob_from_bytes_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_match_async())

    async def _test_append_blob_from_bytes_with_if_match_fail_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_match=test_etag)

        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_blob_from_bytes_with_if_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_match_fail_async())

    async def _test_append_blob_from_bytes_with_if_none_match_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = '0x8D2C9167D53FC2C'

        # Act
        data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_none_match=test_etag)

        # Assert
        content = await blob.download_blob()
        content = await content.content_as_bytes()
        self.assertEqual(data, content)

    @record
    def test_append_blob_from_bytes_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_none_match_async())

    async def _test_append_blob_from_bytes_with_if_none_match_fail_async(self):
        # Arrange
        blob_name = self.get_resource_name("blob")
        container, blob = await self._create_container_and_append_blob(self.container_name, blob_name)
        test_etag = (await blob.get_blob_properties()).etag

        # Act
        with self.assertRaises(ResourceModifiedError) as e:
            data = self.get_random_bytes(LARGE_APPEND_BLOB_SIZE)
            await blob.upload_blob(data, blob_type=BlobType.AppendBlob, if_none_match=test_etag)

        self.assertEqual(StorageErrorCode.condition_not_met, e.exception.error_code)

    @record
    def test_append_blob_from_bytes_with_if_none_match_fail_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_if_none_match_fail_async())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
