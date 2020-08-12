# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import unittest
import pytest
import uuid

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceModifiedError
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobType,
    ContentSettings,
    BlobBlock,
    StandardBlobTier
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer

from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer, GlobalResourceGroupPreparer

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
LARGE_BLOB_SIZE = 64 * 1024 + 5
#------------------------------------------------------------------------------

class StorageBlockBlobTest(StorageTestCase):

    def _setup(self, storage_account, key):
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=key,
            connection_data_block_size=4 * 1024,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        if self.is_live:
            self.bsc.create_container(self.container_name)

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    #--Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'', tags=tags)
        return blob

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        self.assertEqual(actual_data.readall(), expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for block blobs --------------------------------------------

    @GlobalStorageAccountPreparer()
    def test_put_block(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob = self._create_blob()

        # Act
        for i in range(5):
            headers = blob.stage_block(i, 'block {0}'.format(i).encode('utf-8'))
            self.assertIn('content_crc64', headers)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_put_block_with_response(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account.name, storage_account_key)
        blob = self._create_blob()

        def return_response(resp, _, headers):
            return (resp, headers)

        # Act
        resp, headers = blob.stage_block(0, 'block 0', cls=return_response)

        # Assert
        self.assertEqual(201, resp.status_code)
        self.assertIn('x-ms-content-crc64', headers)

    @GlobalStorageAccountPreparer()
    def test_put_block_unicode(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob = self._create_blob()

        # Act
        headers = blob.stage_block('1', u'啊齄丂狛狜')
        self.assertIn('content_crc64', headers)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_put_block_with_md5(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob = self._create_blob()

        # Act
        blob.stage_block(1, b'block', validate_content=True)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_put_block_list(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = blob.commit_block_list(block_list)

        # Assert
        content = blob.download_blob()
        self.assertEqual(content.readall(), b'AAABBBCCC')
        self.assertEqual(content.properties.etag, put_block_list_resp.get('etag'))
        self.assertEqual(content.properties.last_modified, put_block_list_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_put_block_list_invalid_block_id(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        try:
            block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='4')]
            blob.commit_block_list(block_list)
            self.fail()
        except HttpResponseError as e:
            self.assertGreaterEqual(str(e).find('specified block list is invalid'), 0)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_put_block_list_with_md5(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, validate_content=True)

        # Assert

    @GlobalStorageAccountPreparer()
    def test_put_block_list_with_blob_tier_specified(self, resource_group, location, storage_account, storage_account_key):

        # Arrange
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_client.stage_block('1', b'AAA')
        blob_client.stage_block('2', b'BBB')
        blob_client.stage_block('3', b'CCC')
        blob_tier = StandardBlobTier.Cool

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob_client.commit_block_list(block_list,
                                      standard_blob_tier=blob_tier)

        # Assert
        blob_properties = blob_client.get_blob_properties()
        self.assertEqual(blob_properties.blob_tier, blob_tier)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    def test_get_block_list_no_blocks(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob = self._create_blob(tags=tags)

        # Act
        with self.assertRaises(ResourceModifiedError):
            blob.get_block_list('all', if_tags_match_condition="\"condition tag\"='wrong tag'")
        block_list = blob.get_block_list('all', if_tags_match_condition="\"tag1\"='firsttag'")

        # Assert
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 0)

    @GlobalStorageAccountPreparer()
    def test_get_block_list_uncommitted_blocks(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = blob.get_block_list('uncommitted')

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

    @GlobalStorageAccountPreparer()
    def test_get_block_list_committed_blocks(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list)

        # Act
        block_list = blob.get_block_list('committed')

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

    @GlobalStorageAccountPreparer()
    def test_create_small_block_blob_with_no_overwrite(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = b'hello world'
        data2 = b'hello second world'

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True)

        with self.assertRaises(ResourceExistsError):
            blob.upload_blob(data2, overwrite=False)

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data1)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)

    @GlobalStorageAccountPreparer()
    def test_create_small_block_blob_with_overwrite(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = b'hello world'
        data2 = b'hello second world'

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True)
        update_resp = blob.upload_blob(data2, overwrite=True)

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)

    @GlobalStorageAccountPreparer()
    def test_create_large_block_blob_with_no_overwrite(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True, metadata={'blobdata': 'data1'})

        with self.assertRaises(ResourceExistsError):
            blob.upload_blob(data2, overwrite=False, metadata={'blobdata': 'data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data1)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.metadata, {'blobdata': 'data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE)

    @GlobalStorageAccountPreparer()
    def test_create_large_block_blob_with_overwrite(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True, metadata={'blobdata': 'data1'})
        update_resp = blob.upload_blob(data2, overwrite=True, metadata={'blobdata': 'data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.metadata, {'blobdata': 'data2'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_single_put(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_0_bytes(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b''

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_create_from_bytes_blob_unicode(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = u'hello world'

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_create_from_bytes_blob_unicode(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world'
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data.encode('utf-8'))
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_from_bytes_blob_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        lease = blob.acquire_lease()

        # Act
        create_resp = blob.upload_blob(data, lease=lease)

        # Assert
        output = blob.download_blob(lease=lease)
        self.assertEqual(output.readall(), data)
        self.assertEqual(output.properties.etag, create_resp.get('etag'))
        self.assertEqual(output.properties.last_modified, create_resp.get('last_modified'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        blob.upload_blob(data, metadata=metadata)

        # Assert
        md = blob.get_blob_properties().metadata
        self.assertDictEqual(md, metadata)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        blob.upload_blob(data, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
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

        create_resp = blob.upload_blob(data, raw_response_hook=callback)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_index(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data[3:])

        # Assert
        self.assertEqual(data[3:], blob.download_blob().readall())

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_index_and_count(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data[3:], length=5)

        # Assert
        self.assertEqual(data[3:8], blob.download_blob().readall())

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_index_and_count_and_properties(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        blob.upload_blob(data[3:], length=5, content_settings=content_settings)

        # Assert
        self.assertEqual(data[3:8], blob.download_blob().readall())
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, length=LARGE_BLOB_SIZE, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data)

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_bytes_with_blob_tier_specified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'
        blob_tier = StandardBlobTier.Cool

        # Act
        blob_client.upload_blob(data, standard_blob_tier=blob_tier)
        blob_properties = blob_client.get_blob_properties()

        # Assert
        self.assertEqual(blob_properties.blob_tier, blob_tier)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_path(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_input.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_path_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        FILE_PATH = 'create_blob_from_path_non_par.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream, length=100, max_concurrency=1)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_upload_blob_from_path_non_parallel_with_standard_blob_tier(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        FILE_PATH = '_path_non_parallel_with_standard_blob.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_tier = StandardBlobTier.Cool
        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=100, max_concurrency=1, standard_blob_tier=blob_tier)
        props = blob.get_blob_properties()

        # Assert
        self.assertEqual(props.blob_tier, blob_tier)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_path_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path_with_progr.temp.{}.dat'.format(str(uuid.uuid4()))
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
            blob.upload_blob(stream, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_path_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_path_with_properties.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_stream_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_stream_chunked_up.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_frm_stream_nonseek_chunk_upld_knwn_size(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        blob_size = len(data) - 66
        FILE_PATH = 'stream_nonseek_chunk_upld_knwn_size.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTest.NonSeekableFile(stream)
            blob.upload_blob(non_seekable_file, length=blob_size, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_from_stream_nonseek_chunk_upld_unkwn_size(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_nonseek_chunk_upld.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTest.NonSeekableFile(stream)
            blob.upload_blob(non_seekable_file, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_stream_with_progress_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_with_progress_chunked.temp.{}.dat'.format(str(uuid.uuid4()))
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
            blob.upload_blob(stream, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_stream_chunked_upload_with_count(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'chunked_upload_with_count.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            resp = blob.upload_blob(stream, length=blob_size)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_from_stream_chunk_upload_with_cntandrops(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'from_stream_chunk_upload_with_cntandrops.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_stream_chnked_upload_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'chnked_upload_with_properti.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_stream_chunked_upload_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_stream_chunked_upload.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_tier = StandardBlobTier.Cool

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2, standard_blob_tier=blob_tier)

        properties = blob.get_blob_properties()

        # Assert
        self.assertEqual(properties.blob_tier, blob_tier)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_text(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        create_resp = blob.upload_blob(text)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_text_with_encoding(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        blob.upload_blob(text, encoding='utf-16')

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    @GlobalStorageAccountPreparer()
    def test_create_blob_from_text_with_encoding_and_progress(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
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

        blob.upload_blob(text, encoding='utf-16', raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_from_text_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        blob.upload_blob(data)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

    @GlobalStorageAccountPreparer()
    def test_create_blob_with_md5(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        blob.upload_blob(data, validate_content=True)

        # Assert

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_create_blob_with_md5_chunked(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, validate_content=True)

        # Assert

#------------------------------------------------------------------------------
