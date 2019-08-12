# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import unittest
import pytest
import asyncio

from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType,
    ContentSettings,
    BlobBlock,
    StandardBlobTier
)
from testcase import (
    StorageTestCase,
    TestMode,
    record,
)

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_input.temp.dat'
LARGE_BLOB_SIZE = 64 * 1024 + 5
#------------------------------------------------------------------------------


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageBlockBlobTestAsync(StorageTestCase):

    def setUp(self):
        super(StorageBlockBlobTestAsync, self).setUp()

        url = self._get_account_url()

        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bsc = BlobServiceClient(
            url,
            credential=self.settings.STORAGE_ACCOUNT_KEY,
            connection_data_block_size=4 * 1024,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024,
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

        return super(StorageBlockBlobTestAsync, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    async def _setup(self):
        if not self.is_playback():
            try:
                await self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    async def _create_blob(self):
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b'')
        return blob

    async def assertBlobEqual(self, container_name, blob_name, expected_data):
        await self._setup()
        blob = self.bsc.get_blob_client(container_name, blob_name)
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

    #--Test cases for block blobs --------------------------------------------

    
    async def _test_put_block(self):
        await self._setup()
        # Arrange
        blob = await self._create_blob()

        # Act
        for i in range(5):
            resp = await blob.stage_block(i, 'block {0}'.format(i).encode('utf-8'))
            self.assertIsNone(resp)

        # Assert
    @record
    def test_put_block(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block())
    
    async def _test_put_block_unicode(self):
        await self._setup()
        # Arrange
        blob = await self._create_blob()

        # Act
        resp = await blob.stage_block('1', u'啊齄丂狛狜')
        self.assertIsNone(resp)

        # Assert

    @record
    def test_put_block_unicode(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_unicode())
    
    async def _test_put_block_with_md5(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        await blob.stage_block(1, b'block', validate_content=True)

        # Assert

    @record
    def test_put_block_with_md5(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_with_md5())
    
    async def _test_put_block_list(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.stage_block('1', b'AAA')
        await blob.stage_block('2', b'BBB')
        await blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = await blob.commit_block_list(block_list)

        # Assert
        content = await blob.download_blob()
        actual = await content.content_as_bytes()
        self.assertEqual(actual, b'AAABBBCCC')
        self.assertEqual(content.properties.etag, put_block_list_resp.get('etag'))
        self.assertEqual(content.properties.last_modified, put_block_list_resp.get('last_modified'))

    @record
    def test_put_block_list(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list())

    async def _test_put_block_list_invalid_block_id(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.stage_block('1', b'AAA')
        await blob.stage_block('2', b'BBB')
        await blob.stage_block('3', b'CCC')

        # Act
        try:
            block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='4')]
            await blob.commit_block_list(block_list)
            self.fail()
        except HttpResponseError as e:
            self.assertGreaterEqual(str(e).find('specified block list is invalid'), 0)

        # Assert

    @record
    def test_put_block_list_invalid_block_id(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_invalid_block_id())

    async def _test_put_block_list_with_md5(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.stage_block('1', b'AAA')
        await blob.stage_block('2', b'BBB')
        await blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, validate_content=True)

        # Assert
    @record
    def test_put_block_list_with_md5(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_put_block_list_with_md5())

    async def _test_get_block_list_no_blocks(self):
        # Arrange
        await self._setup()
        blob = await self._create_blob()

        # Act
        block_list = await blob.get_block_list('all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 0)

    @record
    def test_get_block_list_no_blocks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_block_list_no_blocks())

    async def _test_get_block_list_uncommitted_blocks(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.stage_block('1', b'AAA')
        await blob.stage_block('2', b'BBB')
        await blob.stage_block('3', b'CCC')

        # Act
        block_list = await blob.get_block_list('uncommitted')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 3)
        self.assertEqual(len(block_list[0]), 0)
        self.assertEqual(block_list[1][0].id, '1')
        self.assertEqual(block_list[1][0].size, 3)
        self.assertEqual(block_list[1][1].id, '2')
        self.assertEqual(block_list[1][1].size, 3)
        self.assertEqual(block_list[1][2].id, '3')
        self.assertEqual(block_list[1][2].size, 3)

    @record
    def test_get_block_list_uncommitted_blocks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_block_list_uncommitted_blocks())

    async def _test_get_block_list_committed_blocks(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.stage_block('1', b'AAA')
        await blob.stage_block('2', b'BBB')
        await blob.stage_block('3', b'CCC')

        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list)

        # Act
        block_list = await blob.get_block_list('committed')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list), 2)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 3)
        self.assertEqual(block_list[0][0].id, '1')
        self.assertEqual(block_list[0][0].size, 3)
        self.assertEqual(block_list[0][1].id, '2')
        self.assertEqual(block_list[0][1].size, 3)
        self.assertEqual(block_list[0][2].id, '3')
        self.assertEqual(block_list[0][2].size, 3)

    @record
    def test_get_block_list_committed_blocks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_block_list_committed_blocks())

    async def _test_create_small_block_blob_with_no_overwrite(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = b'hello world'
        data2 = b'hello second world'

        # Act
        create_resp = await blob.upload_blob(data1, overwrite=True)

        with self.assertRaises(ResourceExistsError):
            await blob.upload_blob(data2, overwrite=False)

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data1)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)

    @record
    def test_create_small_block_blob_with_no_overwrite(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_small_block_blob_with_no_overwrite())

    async def _test_create_small_block_blob_with_overwrite(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = b'hello world'
        data2 = b'hello second world'

        # Act
        create_resp = await blob.upload_blob(data1, overwrite=True)
        update_resp = await blob.upload_blob(data2, overwrite=True)

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)

    @record
    def test_create_small_block_blob_with_overwrite(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_small_block_blob_with_overwrite())

    async def _test_create_large_block_blob_with_no_overwrite(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = await blob.upload_blob(data1, overwrite=True, metadata={'BlobData': 'Data1'})

        with self.assertRaises(ResourceExistsError):
            await blob.upload_blob(data2, overwrite=False, metadata={'BlobData': 'Data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data1)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.metadata, {'BlobData': 'Data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE)

    @record
    def test_create_large_block_blob_with_no_overwrite(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_block_blob_with_no_overwrite())

    async def _test_create_large_block_blob_with_overwrite(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = await blob.upload_blob(data1, overwrite=True, metadata={'BlobData': 'Data1'})
        update_resp = await blob.upload_blob(data2, overwrite=True, metadata={'BlobData': 'Data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.metadata, {'BlobData': 'Data2'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)

    @record
    def test_create_large_block_blob_with_overwrite(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_large_block_blob_with_overwrite())

    async def _test_create_blob_from_bytes_single_put(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        create_resp = await blob.upload_blob(data)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_bytes_single_put(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_single_put())

    async def _test_create_blob_from_0_bytes(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b''

        # Act
        create_resp = await blob.upload_blob(data)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_0_bytes(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_0_bytes())

    async def _test_create_from_bytes_blob_unicode(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        create_resp = await blob.upload_blob(data)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_from_bytes_blob_unicode(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_from_bytes_blob_unicode())

    async def _test_create_from_bytes_blob_with_lease_id(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        lease = await blob.acquire_lease()

        # Act
        create_resp = await blob.upload_blob(data, lease=lease)

        # Assert
        output = await blob.download_blob(lease=lease)
        actual = await output.content_as_bytes()
        self.assertEqual(actual, data)
        self.assertEqual(output.properties.etag, create_resp.get('etag'))
        self.assertEqual(output.properties.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_from_bytes_blob_with_lease_id(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_from_bytes_blob_with_lease_id())

    async def _test_create_blob_from_bytes_with_metadata(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        await blob.upload_blob(data, metadata=metadata)

        # Assert
        md = await blob.get_blob_properties()
        md = md.metadata
        self.assertDictEqual(md, metadata)

    @record
    def test_create_blob_from_bytes_with_metadata(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_with_metadata())

    async def _test_create_blob_from_bytes_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        await blob.upload_blob(data, content_settings=content_settings)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_bytes_with_properties(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_with_properties())
    
    async def _test_create_blob_from_bytes_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        create_resp = await blob.upload_blob(data, raw_response_hook=callback)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_bytes_with_progress(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_with_progress())

    async def _test_create_blob_from_bytes_with_index(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data[3:])

        # Assert
        db = await blob.download_blob()
        output = await db.content_as_bytes()
        self.assertEqual(data[3:], output)

    @record
    def test_create_blob_from_bytes_with_index(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_with_index())

    async def _test_create_blob_from_bytes_with_index_and_count(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data[3:], length=5)

        # Assert
        db = await blob.download_blob()
        output = await db.content_as_bytes()
        self.assertEqual(data[3:8], output)

    @record
    def test_create_blob_from_bytes_with_index_and_count(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_with_index_and_count())

    async def _test_create_blob_from_bytes_with_index_and_count_and_properties(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        await blob.upload_blob(data[3:], length=5, content_settings=content_settings)

        # Assert
        db = await blob.download_blob()
        output = await db.content_as_bytes()
        self.assertEqual(data[3:8],output)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_bytes_with_index_and_count_and_properties(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_with_index_and_count_and_properties())

    async def _test_create_blob_from_bytes_non_parallel(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data, length=LARGE_BLOB_SIZE, max_connections=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data)

    @record
    def test_create_blob_from_bytes_non_parallel(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_bytes_non_parallel())

    async def _test_create_blob_from_path(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_path(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_path())

    async def _test_create_blob_from_path_non_parallel(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream, length=100, max_connections=1)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_path_non_parallel(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_path_non_parallel())

    async def _test_create_blob_from_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
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
            await blob.upload_blob(stream, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_create_blob_from_path_with_progress(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_path_with_progress())

    async def _test_create_blob_from_path_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, content_settings=content_settings)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_path_with_properties(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_path_with_properties())

    async def _test_create_blob_from_stream_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_stream_chunked_upload(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_chunked_upload())

    async def _test_create_blob_from_stream_non_seekable_chunked_upload_known_size(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        blob_size = len(data) - 66
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTestAsync.NonSeekableFile(stream)
            await blob.upload_blob(non_seekable_file, length=blob_size, max_connections=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    @record
    def test_create_blob_from_stream_non_seekable_chunked_upload_known_size(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_non_seekable_chunked_upload_known_size())

    async def _test_create_blob_from_stream_non_seekable_chunked_upload_unknown_size(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTestAsync.NonSeekableFile(stream)
            await blob.upload_blob(non_seekable_file, max_connections=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_blob_from_stream_non_seekable_chunked_upload_unknown_size(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_non_seekable_chunked_upload_unknown_size())

    async def _test_create_blob_from_stream_with_progress_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
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
            await blob.upload_blob(stream, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_create_blob_from_stream_with_progress_chunked_upload(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_with_progress_chunked_upload())

    async def _test_create_blob_from_stream_chunked_upload_with_count(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            resp = await blob.upload_blob(stream, length=blob_size)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    @record
    def test_create_blob_from_stream_chunked_upload_with_count(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_chunked_upload_with_count())

    async def _test_create_blob_from_stream_chunked_upload_with_count_and_properties(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, length=blob_size, content_settings=content_settings)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_stream_chunked_upload_with_count_and_properties(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_chunked_upload_with_count_and_properties())

    async def _test_create_blob_from_stream_chunked_upload_with_properties(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, content_settings=content_settings)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_stream_chunked_upload_with_properties(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_stream_chunked_upload_with_properties())

    async def _test_create_blob_from_text(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        create_resp = await blob.upload_blob(text)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_blob_from_text(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_text())

    async def _test_create_blob_from_text_with_encoding(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        await blob.upload_blob(text, encoding='utf-16')

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_blob_from_text_with_encoding(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_text_with_encoding())

    async def _test_create_blob_from_text_with_encoding_and_progress(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        await blob.upload_blob(text, encoding='utf-16', raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @record
    def test_create_blob_from_text_with_encoding_and_progress(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_text_with_encoding_and_progress())

    async def _test_create_blob_from_text_chunked_upload(self):
        # parallel tests introduce random order of requests, can only run live
        await self._setup()
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        await blob.upload_blob(data)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, encoded_data)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, encoded_data)

    @record
    def test_create_blob_from_text_chunked_upload(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_from_text_chunked_upload())

    async def _test_create_blob_with_md5(self):
        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        await blob.upload_blob(data, validate_content=True)

        # Assert

    @record
    def test_create_blob_with_md5(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_with_md5())

    async def _test_create_blob_with_md5_chunked(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        await self._setup()
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data, validate_content=True)

        # Assert

    @record
    def test_create_blob_with_md5_chunked(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_blob_with_md5_chunked())

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
