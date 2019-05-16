# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import unittest
import pytest

from azure.common import AzureHttpError
from azure.core import HttpResponseError
from azure.storage.blob import (
    #BlobBlockList,
    SharedKeyCredentials,
    BlobServiceClient,
    ContainerClient,
    BlobClient
)
from azure.storage.blob.common import StandardBlobTier
from azure.storage.blob.models import ContentSettings, BlobBlock
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
FILE_PATH = 'blob_input.temp.dat'
LARGE_BLOB_SIZE = 64 * 1024 + 5
#------------------------------------------------------------------------------

class StorageBlockBlobTest(StorageTestCase):

    def setUp(self):
        super(StorageBlockBlobTest, self).setUp()

        url = self._get_account_url()
        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())

        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.config = BlobServiceClient.create_configuration()
        self.config.connection.data_block_size = 4 * 1024

        self.bsc = BlobServiceClient(url, credentials=credentials, configuration=self.config)


        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        #self.bs.MAX_BLOCK_SIZE = 4 * 1024
        #self.bs.MAX_SINGLE_PUT_SIZE = 32 * 1024

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bs.delete_container(self.container_name)
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageBlockBlobTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(b'')
        return blob

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        self.assertEqual(b"".join(list(actual_data)), expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for block blobs --------------------------------------------

    @record
    def test_put_block(self):
        # Arrange
        blob = self._create_blob()

        # Act
        for i in range(5):
            resp = blob.stage_block(i, 'block {0}'.format(i).encode('utf-8'))
            self.assertIsNone(resp)

        # Assert

    @record
    def test_put_block_unicode(self):
        # Arrange
        pytest.skip("We don't reject unicode")  # TODO
        blob = self._create_blob()

        # Act
        with self.assertRaises(TypeError):
            resp = blob.stage_block('1', u'啊齄丂狛狜')

        # Assert

    @record
    def test_put_block_with_md5(self):
        # Arrange
        pytest.skip("validate content not yet supported")  # TODO
        blob = self._create_blob()

        # Act
        blob.stage_block(1, b'block', validate_content=True)

        # Assert

    @record
    def test_put_block_list(self):
        # Arrange
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
        self.assertEqual(b"".join(list(content)), b'AAABBBCCC')
        self.assertEqual(content.properties.etag, put_block_list_resp.get('ETag'))
        self.assertEqual(content.properties.last_modified, put_block_list_resp.get('Last-Modified'))

    @record
    def test_put_block_list_invalid_block_id(self):
        # Arrange
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

    @record
    def test_put_block_list_with_md5(self):
        pytest.skip("validate content not yet supported")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, validate_content=True)

        # Assert

    @record
    def test_get_block_list_no_blocks(self):
        # Arrange
        blob = self._create_blob()

        # Act
        block_list = blob.get_block_list('all')

        # Assert
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 0)

    @record
    def test_get_block_list_uncommitted_blocks(self):
        # Arrange
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

    @record
    def test_get_block_list_committed_blocks(self):
        # Arrange
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

    @record
    def test_create_blob_from_bytes_single_put(self):
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('ETag'))
        self.assertEqual(props.last_modified, create_resp.get('Last-Modified'))

    @record
    def test_create_blob_from_0_bytes(self):
        pytest.skip("Raises error on range header")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b''

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('ETag'))
        self.assertEqual(props.last_modified, create_resp.get('Last-Modified'))

    @record
    def test_create_from_bytes_blob_unicode(self):
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = u'hello world'

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('ETag'))
        self.assertEqual(props.last_modified, create_resp.get('Last-Modified'))

    @record
    def test_create_from_bytes_blob_unicode(self):
        pytest.skip("We don't reject unicode")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world'
        with self.assertRaises(TypeError):
            create_resp = blob.upload_blob(data)

        # Assert

    def test_create_from_bytes_blob_with_lease_id(self):
        # parallel tests introduce random order of requests, can only run live
        pytest.skip("Large blobs not yet supported")  # TODO
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        lease_id = self.bs.acquire_blob_lease(self.container_name, blob_name)

        # Act
        create_resp = self.bs.create_blob_from_bytes(self.container_name, blob_name, data, lease_id=lease_id)

        # Assert
        blob = self.bs.get_blob_to_bytes(self.container_name, blob_name, lease_id=lease_id)
        self.assertEqual(blob.content, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_bytes_with_metadata(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data, metadata=metadata)

        # Assert
        md = self.bs.get_blob_metadata(self.container_name, blob_name)
        self.assertDictEqual(md, metadata)


    def test_create_blob_from_bytes_with_properties(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data,
                                       content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_blob_from_bytes_with_progress(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        create_resp = self.bs.create_blob_from_bytes(self.container_name, blob_name, data, progress_callback=callback)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_BLOCK_SIZE, progress)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_bytes_with_index(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data, 3)

        # Assert
        self.assertEqual(data[3:], self.bs.get_blob_to_bytes(self.container_name, blob_name).content)

    @record
    def test_create_blob_from_bytes_with_index_and_count(self):
        pytest.skip("Upload index not yet supported")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, 3, 5)

        # Assert
        self.assertEqual(data[3:8], self.bs.get_blob_to_bytes(self.container_name, blob_name).content)

    @record
    def test_create_blob_from_bytes_with_index_and_count_and_properties(self):
        pytest.skip("Upload index not yet supported")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data, 3, 5, content_settings=content_settings)

        # Assert
        self.assertEqual(data[3:8], self.bs.get_blob_to_bytes(self.container_name, blob_name).content)
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_bytes_non_parallel(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, length=LARGE_BLOB_SIZE, max_connections=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_blob_from_path(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        create_resp = self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    @record
    def test_create_blob_from_path_non_parallel(self):
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream, length=100, max_connections=1)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('ETag'))
        self.assertEqual(props.last_modified, create_resp.get('Last-Modified'))

    def test_create_blob_from_path_with_progress(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH,
                                      progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_BLOCK_SIZE, progress)

    def test_create_blob_from_path_with_properties(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        self.bs.create_blob_from_path(self.container_name, blob_name, FILE_PATH, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_blob_from_stream_chunked_upload(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = self.bs.create_blob_from_stream(self.container_name, blob_name, stream)
        blob = self.bs.get_blob_properties(self.container_name, blob_name)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(blob.properties.etag, create_resp.etag)
        self.assertEqual(blob.properties.last_modified, create_resp.last_modified)

    def test_create_blob_from_stream_non_seekable_chunked_upload_known_size(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        blob_size = len(data) - 66
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTest.NonSeekableFile(stream)
            self.bs.create_blob_from_stream(self.container_name, blob_name, non_seekable_file,
                                            count=blob_size, max_connections=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_create_blob_from_stream_non_seekable_chunked_upload_unknown_size(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTest.NonSeekableFile(stream)
            self.bs.create_blob_from_stream(self.container_name, blob_name,
                                            non_seekable_file, max_connections=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    def test_create_blob_from_stream_with_progress_chunked_upload(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream, progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_BLOCK_SIZE, progress, unknown_size=True)

    def test_create_blob_from_stream_chunked_upload_with_count(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            resp = self.bs.create_blob_from_stream(self.container_name, blob_name, stream, blob_size)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])

    def test_create_blob_from_stream_chunked_upload_with_count_and_properties(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream,
                                            blob_size, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    def test_create_blob_from_stream_chunked_upload_with_properties(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            self.bs.create_blob_from_stream(self.container_name, blob_name, stream,
                                            content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = self.bs.get_blob_properties(self.container_name, blob_name).properties
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_create_blob_from_text(self):
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        create_resp = blob.upload_blob(text)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('ETag'))
        self.assertEqual(props.last_modified, create_resp.get('Last-Modified'))

    @record
    def test_create_blob_from_text_with_encoding(self):
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        blob.upload_blob(text)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    @record
    def test_create_blob_from_text_with_encoding_and_progress(self):
        pytest.skip("Probably no longer applicable as we're dropping callbacks")
        # Arrange
        blob_name = self._get_blob_reference()
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        self.bs.create_blob_from_text(self.container_name, blob_name, text, 'utf-16',
                                      progress_callback=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.bs.MAX_BLOCK_SIZE, progress)

    def test_create_blob_from_text_chunked_upload(self):
        pytest.skip("Large blobs not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        self.bs.create_blob_from_text(self.container_name, blob_name, data)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

    @record
    def test_create_blob_with_md5(self):
        pytest.skip("Validate content not yet supported")  # TODO
        # Arrange
        blob_name = self._get_blob_reference()
        data = b'hello world'

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data,
                                       validate_content=True)

        # Assert

    def test_create_blob_with_md5_chunked(self):
        pytest.skip("Validate content not yet supported")  # TODO
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        blob_name = self._get_blob_reference()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data,
                                       validate_content=True)

        # Assert

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
