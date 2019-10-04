# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta

import pytest
import asyncio

import os
import unittest

from azure.core import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError, ResourceModifiedError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob import BlobPermissions
from azure.storage.blob._shared.policies import StorageContentValidation
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType
)
from testcase import (
    StorageTestCase,
    TestMode,
    record,
)

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_input.temp.dat'
LARGE_BLOB_SIZE = 64 * 1024


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


class StorageAppendBlobTestAsync(StorageTestCase):

    def setUp(self):
        super(StorageAppendBlobTestAsync, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()

        self.bsc = BlobServiceClient(url, credential=credential, max_block_size=4 * 1024,
                                     transport=AiohttpTestTransport())
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.bsc.delete_container(self.container_name))
            except:
                pass
            try:
                loop.run_until_complete(self.bs.delete_container(self.source_container_name))
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageAppendBlobTestAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    async def _setup(self):
        if not self.is_playback():
            try:
                await self.bsc.create_container(self.container_name)
                await self.bsc.create_container(self.source_container_name)
            except:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    async def _create_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(
            self.container_name,
            blob_name)
        await blob.create_append_blob()
        return blob

    async def _create_source_blob(self, data):
        blob_client = self.bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX))
        await blob_client.create_append_blob()
        await blob_client.append_block(data)
        return blob_client

    async def assertBlobEqual(self, blob, expected_data):
        stream = await blob.download_blob()
        actual_data = await stream.content_as_bytes()
        self.assertEqual(actual_data, expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # --Test cases for append blobs --------------------------------------------

    async def _test_create_blob_async(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        create_resp = await blob.create_append_blob()

        # Assert
        blob_properties = await blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_async())

    async def _test_create_blob_with_lease_id_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        lease = await blob.acquire_lease()
        create_resp = await blob.create_append_blob(lease=lease)

        # Assert
        blob_properties = await blob.get_blob_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_with_lease_id_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_with_lease_id_async())

    async def _test_create_blob_with_metadata_async(self):
        # Arrange
        await self._setup()
        metadata = {'hello': 'world', 'number': '42'}
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        await blob.create_append_blob(metadata=metadata)

        # Assert
        md = await blob.get_blob_properties()
        self.assertDictEqual(md.metadata, metadata)

    @record
    def test_create_blob_with_metadata_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_with_metadata_async())

    async def _test_append_block_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        for i in range(5):
            resp = await blob.append_block(u'block {0}'.format(i).encode('utf-8'))
            self.assertEqual(int(resp['blob_append_offset']), 7 * i)
            self.assertEqual(resp['blob_committed_block_count'], i + 1)
            self.assertIsNotNone(resp['etag'])
            self.assertIsNotNone(resp['last_modified'])

        # Assert
        await self.assertBlobEqual(blob, b'block 0block 1block 2block 3block 4')

    @record
    def test_append_block_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_async())

    async def _test_append_block_unicode_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        resp = await blob.append_block(u'啊齄丂狛狜', encoding='utf-16')
        self.assertEqual(int(resp['blob_append_offset']), 0)
        self.assertEqual(resp['blob_committed_block_count'], 1)
        self.assertIsNotNone(resp['etag'])
        self.assertIsNotNone(resp['last_modified'])

        # Assert

    @record
    def test_append_block_unicode_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_unicode_async())

    async def _test_append_block_with_md5_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        resp = await blob.append_block(b'block', validate_content=True)
        self.assertEqual(int(resp['blob_append_offset']), 0)
        self.assertEqual(resp['blob_committed_block_count'], 1)
        self.assertIsNotNone(resp['etag'])
        self.assertIsNotNone(resp['last_modified'])

        # Assert

    @record
    def test_append_block_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_with_md5_async())

    async def _test_append_block_from_url(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act: make append block from url calls
        split = 4 * 1024
        resp = await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                   source_offset=0, source_length=split)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        resp = await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                   source_offset=split,
                                                                   source_length=LARGE_BLOB_SIZE - split)
        self.assertEqual(resp.get('blob_append_offset'), str(4 * 1024))
        self.assertEqual(resp.get('blob_committed_block_count'), 2)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        blob = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(blob.get('etag'), resp.get('etag'))
        self.assertEqual(blob.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(blob.get('size'), LARGE_BLOB_SIZE)

        # Missing start range shouldn't pass the validation
        with self.assertRaises(ValueError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_length=LARGE_BLOB_SIZE)

    @record
    def test_append_block_from_url_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url())

    async def _test_append_block_from_url_and_validate_content_md5(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        src_md5 = StorageContentValidation.get_content_md5(source_blob_data)
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls with correct md5
        resp = await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                   source_content_md5=src_md5)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with wrong md5
        with self.assertRaises(HttpResponseError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_content_md5=StorageContentValidation.get_content_md5(
                                                                    b"POTATO"))

    @record
    def test_append_block_from_url_and_validate_content_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_and_validate_content_md5())

    async def _test_append_block_from_url_with_source_if_modified(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        source_blob_properties = await source_blob_client.get_blob_properties()
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                   source_offset=0,
                                                                   source_length=LARGE_BLOB_SIZE,
                                                                   source_if_modified_since=source_blob_properties.get(
                                                                       'last_modified') - timedelta(hours=15))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceNotFoundError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                source_if_modified_since=source_blob_properties.get(
                                                                    'last_modified'))

    @record
    def test_append_block_from_url_with_source_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_source_if_modified())

    async def _test_append_block_from_url_with_source_if_unmodified(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        source_blob_properties = await source_blob_client.get_blob_properties()
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                   source_offset=0,
                                                                   source_length=LARGE_BLOB_SIZE,
                                                                   source_if_unmodified_since=source_blob_properties.get(
                                                                       'last_modified'))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            await destination_blob_client \
                .append_block_from_url(source_blob_client.url + '?' + sas,
                                       source_offset=0, source_length=LARGE_BLOB_SIZE,
                                       if_unmodified_since=source_blob_properties.get('last_modified') - timedelta(
                                           hours=15))

    @record
    def test_append_block_from_url_with_source_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_source_if_unmodified())

    async def _test_append_block_from_url_with_source_if_match(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        source_properties = await source_blob_client.get_blob_properties()
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  source_if_match=source_properties.get('etag'))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceNotFoundError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                source_if_match='0x111111111111111')

    @record
    def test_append_block_from_url_with_source_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_source_if_match())

    async def _test_append_block_from_url_with_source_if_none_match(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        source_properties = await source_blob_client.get_blob_properties()
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  source_if_none_match='0x111111111111111')
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceNotFoundError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                source_if_none_match=source_properties.get('etag'))

    @record
    def test_append_block_from_url_with_source_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_source_if_none_match())

    async def _test_append_block_from_url_with_if_match(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_name = self._get_blob_reference()
        destination_blob_client = self.bsc.get_blob_client(
            self.container_name,
            destination_blob_name)
        destination_blob_properties_on_creation = await destination_blob_client.create_append_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  if_match=destination_blob_properties_on_creation.get('etag'))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                if_match='0x111111111111111')

    @record
    def test_append_block_from_url_with_if_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_if_match())

    async def _test_append_block_from_url_with_if_none_match(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  if_none_match='0x111111111111111')
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                if_none_match=destination_blob_properties.get('etag'))

    @record
    def test_append_block_from_url_with_if_none_match_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_if_none_match())

    async def _test_append_block_from_url_with_maxsize_condition(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  maxsize_condition=LARGE_BLOB_SIZE + 1)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                maxsize_condition=LARGE_BLOB_SIZE + 1)

    @record
    def test_append_block_from_url_with_maxsize_condition_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_maxsize_condition())

    async def _test_append_block_from_url_with_appendpos_condition(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  appendpos_condition=0)
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                appendpos_condition=0)

    @record
    def test_append_block_from_url_with_appendpos_condition_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_appendpos_condition())

    async def _test_append_block_from_url_with_if_modified(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        source_properties = await source_blob_client.get_blob_properties()
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  if_modified_since=source_properties.get('last_modified') - timedelta(minutes=15))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(HttpResponseError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                if_modified_since=destination_blob_properties.get(
                                                                    'last_modified'))

    @record
    def test_append_block_from_url_with_if_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_if_modified())

    async def _test_append_block_from_url_with_if_unmodified(self):
        # Arrange
        await self._setup()
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(source_blob_data)
        source_properties = await source_blob_client.get_blob_properties()
        sas = source_blob_client.generate_shared_access_signature(
            permission=BlobPermissions.READ + BlobPermissions.DELETE,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob()

        # Act part 1: make append block from url calls
        resp = await destination_blob_client. \
            append_block_from_url(source_blob_client.url + '?' + sas,
                                  source_offset=0, source_length=LARGE_BLOB_SIZE,
                                  if_unmodified_since=source_properties.get('last_modified') + timedelta(minutes=15))
        self.assertEqual(resp.get('blob_append_offset'), '0')
        self.assertEqual(resp.get('blob_committed_block_count'), 1)
        self.assertIsNotNone(resp.get('etag'))
        self.assertIsNotNone(resp.get('last_modified'))

        # Assert the destination blob is constructed correctly
        destination_blob_properties = await destination_blob_client.get_blob_properties()
        self.assertBlobEqual(destination_blob_client, source_blob_data)
        self.assertEqual(destination_blob_properties.get('etag'), resp.get('etag'))
        self.assertEqual(destination_blob_properties.get('last_modified'), resp.get('last_modified'))
        self.assertEqual(destination_blob_properties.get('size'), LARGE_BLOB_SIZE)

        # Act part 2: put block from url with failing condition
        with self.assertRaises(ResourceModifiedError):
            await destination_blob_client.append_block_from_url(source_blob_client.url + '?' + sas,
                                                                source_offset=0,
                                                                source_length=LARGE_BLOB_SIZE,
                                                                if_unmodified_since=destination_blob_properties.get(
                                                                    'last_modified') - timedelta(minutes=15))

    @record
    def test_append_block_from_url_with_if_unmodified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_block_from_url_with_if_unmodified())

    async def _test_create_append_blob_with_no_overwrite_async(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(
            self.container_name,
            blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = await blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.AppendBlob,
            metadata={'BlobData': 'Data1'})

        update_resp = await blob.upload_blob(
            data2,
            overwrite=False,
            blob_type=BlobType.AppendBlob,
            metadata={'BlobData': 'Data2'})

        props = await blob.get_blob_properties()

        # Assert
        appended_data = data1 + data2
        await self.assertBlobEqual(blob, appended_data)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.blob_type, BlobType.AppendBlob)
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'BlobData': 'Data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + LARGE_BLOB_SIZE + 512)

    @record
    def test_create_append_blob_with_no_overwrite_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_append_blob_with_no_overwrite_async())

    async def _test_create_append_blob_with_overwrite_async(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(
            self.container_name,
            blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = await blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.AppendBlob,
            metadata={'BlobData': 'Data1'})
        update_resp = await blob.upload_blob(
            data2,
            overwrite=True,
            blob_type=BlobType.AppendBlob,
            metadata={'BlobData': 'Data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.metadata, {'BlobData': 'Data2'})
        self.assertEqual(props.blob_type, BlobType.AppendBlob)
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)

    @record
    def test_create_append_blob_with_overwrite_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_append_blob_with_overwrite_async())

    async def _test_append_blob_from_bytes_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        append_resp = await blob.upload_blob(data, blob_type=BlobType.AppendBlob)
        blob_properties = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp['etag'])
        self.assertEqual(blob_properties.last_modified, append_resp['last_modified'])

    @record
    def test_append_blob_from_bytes_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_async())

    async def _test_append_blob_from_0_bytes_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        data = b''
        append_resp = await blob.upload_blob(data, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data)
        # appending nothing should not make any network call
        self.assertIsNone(append_resp.get('etag'))
        self.assertIsNone(append_resp.get('last_modified'))

    @record
    def test_append_blob_from_0_bytes_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_0_bytes_async())

    async def _test_append_blob_from_bytes_with_progress_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = b'abcdefghijklmnopqrstuvwxyz'

        # Act
        progress = []

        def progress_gen(upload):
            progress.append((0, len(upload)))
            yield upload

        upload_data = progress_gen(data)
        await blob.upload_blob(upload_data, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_append_blob_from_bytes_with_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_progress_async())

    async def _test_append_blob_from_bytes_with_index_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        await blob.upload_blob(data[3:], blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data[3:])

    @record
    def test_append_blob_from_bytes_with_index_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_index_async())

    async def _test_append_blob_from_bytes_with_index_and_count_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        data = b'abcdefghijklmnopqrstuvwxyz'
        await blob.upload_blob(data[3:], length=5, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data[3:8])

    @record
    def test_append_blob_from_bytes_with_index_and_count_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_index_and_count_async())

    async def _test_append_blob_from_bytes_chunked_upload_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        append_resp = await blob.upload_blob(data, blob_type=BlobType.AppendBlob)
        blob_properties = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp['etag'])
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @record
    def test_append_blob_from_bytes_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_chunked_upload_async())

    async def _test_append_blob_from_bytes_with_progress_chunked_upload_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []

        def progress_gen(upload):
            n = self.config.max_block_size
            total = len(upload)
            current = 0
            while upload:
                progress.append((current, total))
                yield upload[:n]
                current += len(upload[:n])
                upload = upload[n:]

        upload_data = progress_gen(data)
        await blob.upload_blob(upload_data, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_append_blob_from_bytes_with_progress_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_with_progress_chunked_upload_async())

    async def _test_append_blob_from_bytes_chunked_upload_with_index_and_count_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 33
        blob_size = len(data) - 66

        # Act
        await blob.upload_blob(data[index:], length=blob_size, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data[index:index + blob_size])

    @record
    def test_append_blob_from_bytes_chunked_upload_with_index_and_count_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_bytes_chunked_upload_with_index_and_count_async())

    async def _test_append_blob_from_path_chunked_upload_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            append_resp = await blob.upload_blob(stream, blob_type=BlobType.AppendBlob)

        blob_properties = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @record
    def test_append_blob_from_path_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_path_chunked_upload_async())

    async def _test_append_blob_from_path_with_progress_chunked_upload_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def progress_gen(upload):
            n = self.config.max_block_size
            total = LARGE_BLOB_SIZE
            current = 0
            while upload:
                chunk = upload.read(n)
                if not chunk:
                    break
                progress.append((current, total))
                yield chunk
                current += len(chunk)

        with open(FILE_PATH, 'rb') as stream:
            upload_data = progress_gen(stream)
            await blob.upload_blob(upload_data, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_append_blob_from_path_with_progress_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_path_with_progress_chunked_upload_async())

    async def _test_append_blob_from_stream_chunked_upload_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            append_resp = await blob.upload_blob(stream, blob_type=BlobType.AppendBlob)
        blob_properties = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @record
    def test_append_blob_from_stream_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_stream_chunked_upload_async())

    async def _test_append_blob_from_stream_non_seekable_chunked_upload_known_size_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_size = len(data) - 66

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageAppendBlobTestAsync.NonSeekableFile(stream)
            await blob.upload_blob(non_seekable_file, length=blob_size, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data[:blob_size])

    @record
    def test_append_blob_from_stream_non_seekable_chunked_upload_known_size_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_stream_non_seekable_chunked_upload_known_size_async())

    async def _test_append_blob_from_stream_non_seekable_chunked_upload_unknown_size_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageAppendBlobTestAsync.NonSeekableFile(stream)
            await blob.upload_blob(non_seekable_file, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data)

    @record
    def test_append_blob_from_stream_non_seekable_chunked_upload_unknown_size_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_stream_non_seekable_chunked_upload_unknown_size_async())

    async def _test_append_blob_from_stream_with_multiple_appends_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream1:
            stream1.write(data)
        with open(FILE_PATH, 'wb') as stream2:
            stream2.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream1:
            await blob.upload_blob(stream1, blob_type=BlobType.AppendBlob)
        with open(FILE_PATH, 'rb') as stream2:
            await blob.upload_blob(stream2, blob_type=BlobType.AppendBlob)

        # Assert
        data = data * 2
        await self.assertBlobEqual(blob, data)

    @record
    def test_append_blob_from_stream_with_multiple_appends_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_stream_with_multiple_appends_async())

    async def _test_append_blob_from_stream_chunked_upload_with_count_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, length=blob_size, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data[:blob_size])

    @record
    def test_append_blob_from_stream_chunked_upload_with_count_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_stream_chunked_upload_with_count_async())

    async def _test_append_blob_from_stream_chunked_upload_with_count_parallel_async(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            append_resp = await blob.upload_blob(stream, length=blob_size, blob_type=BlobType.AppendBlob)
        blob_properties = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data[:blob_size])
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @record
    def test_append_blob_from_stream_chunked_upload_with_count_parallel_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_stream_chunked_upload_with_count_parallel_async())

    async def _test_append_blob_from_text_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        append_resp = await blob.upload_blob(text, blob_type=BlobType.AppendBlob)
        blob_properties = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(blob, data)
        self.assertEqual(blob_properties.etag, append_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, append_resp.get('last_modified'))

    @record
    def test_append_blob_from_text_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_text_async())

    async def _test_append_blob_from_text_with_encoding_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        await blob.upload_blob(text, encoding='utf-16', blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, data)

    @record
    def test_append_blob_from_text_with_encoding_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_text_with_encoding_async())

    async def _test_append_blob_from_text_with_encoding_and_progress_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []

        def progress_gen(upload):
            progress.append((0, len(data)))
            yield upload

        upload_data = progress_gen(text)
        await blob.upload_blob(upload_data, encoding='utf-16', blob_type=BlobType.AppendBlob)

        # Assert
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_append_blob_from_text_with_encoding_and_progress_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_text_with_encoding_and_progress_async())

    async def _test_append_blob_from_text_chunked_upload_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        await blob.upload_blob(data, blob_type=BlobType.AppendBlob)

        # Assert
        await self.assertBlobEqual(blob, encoded_data)

    @record
    def test_append_blob_from_text_chunked_upload_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_from_text_chunked_upload_async())

    async def _test_append_blob_with_md5_async(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()
        data = b'hello world'

        # Act
        await blob.append_block(data, validate_content=True)

        # Assert

    @record
    def test_append_blob_with_md5_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_blob_with_md5_async())


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
