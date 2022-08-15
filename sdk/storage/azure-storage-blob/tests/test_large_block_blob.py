# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from os import path, remove, sys, urandom
import platform
import uuid
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    ContentSettings
)

if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from settings.testcase import BlobPreparer
from devtools_testutils.storage import StorageTestCase

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'largeblob'
LARGE_BLOB_SIZE = 12 * 1024 * 1024
LARGE_BLOCK_SIZE = 6 * 1024 * 1024

# ------------------------------------------------------------------------------
if platform.python_implementation() == 'PyPy':
    pytest.skip("Skip tests for Pypy", allow_module_level=True)

class StorageLargeBlockBlobTest(StorageTestCase):
    def _setup(self, storage_account_name, key):
        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key,
            max_single_put_size=32 * 1024,
            max_block_size=2 * 1024 * 1024,
            min_large_block_upload_threshold=1 * 1024 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        if self.is_live:
            try:
                self.bsc.create_container(self.container_name)
            except:
                pass

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

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        self.assertEqual(b"".join(list(actual_data.chunks())), expected_data)

    # --Test cases for block blobs --------------------------------------------
    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_block_bytes_large(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        for i in range(5):
            resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'), urandom(LARGE_BLOCK_SIZE))
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

            # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_block_bytes_large_with_md5(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        for i in range(5):
            resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                urandom(LARGE_BLOCK_SIZE),
                validate_content=True)
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_block_stream_large(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE)
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

            # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_put_block_stream_large_with_md5(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        for i in range(5):
            stream = BytesIO(bytearray(LARGE_BLOCK_SIZE))
            resp = resp = blob.stage_block(
                'block {0}'.format(i).encode('utf-8'),
                stream,
                length=LARGE_BLOCK_SIZE,
                validate_content=True)
            self.assertIsNotNone(resp)
            assert 'content_md5' in resp
            assert 'content_crc64' in resp
            assert 'request_id' in resp

        # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_path(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'large_blob_from_path.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2, overwrite=True)

        block_list = blob.get_block_list()

        # Assert
        self.assertIsNot(len(block_list), 0)
        self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_path_with_md5(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = "blob_from_path_with_md5.temp.dat"
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, validate_content=True, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_path_non_parallel(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(self.get_random_bytes(100))
        FILE_PATH = "blob_from_path_non_parallel.temp.dat"
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_path_with_progress(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = "blob_from_path_with_progress.temp.dat"
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
            blob.upload_blob(stream, max_concurrency=2, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_path_with_properties(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'blob_from_path_with_properties.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_stream_chunked_upload(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'blob_from_stream_chunked_upload.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_creat_lrgblob_frm_stream_w_progress_chnkd_upload(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'stream_w_progress_chnkd_upload.temp.{}.dat'.format(str(uuid.uuid4()))
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
            blob.upload_blob(stream, max_concurrency=2, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_large_blob_from_stream_chunked_upload_with_count(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'chunked_upload_with_count.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_creat_lrgblob_frm_strm_chnkd_uplod_w_count_n_props(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'plod_w_count_n_props.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(
                stream, length=blob_size, content_settings=content_settings, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_creat_lrg_blob_frm_stream_chnked_upload_w_props(self, storage_account_name, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = bytearray(urandom(LARGE_BLOB_SIZE))
        FILE_PATH = 'creat_lrg_blob.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)
        self._teardown(FILE_PATH)

# ------------------------------------------------------------------------------