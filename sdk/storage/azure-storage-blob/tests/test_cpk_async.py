# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.storage.blob import BlobType, BlobBlock, CustomerProvidedEncryptionKey, BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient
from _shared.testcase import GlobalStorageAccountPreparer
from _shared.asynctestcase import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
                                                    key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")


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


class StorageCPKAsyncTest(AsyncStorageTestCase):
    async def _setup(self, bsc):
        self.config = bsc._config
        self.byte_data = self.get_random_bytes(64 * 1024)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            await bsc.create_container(self.container_name)


    def _teardown(self, bsc):
        if self.is_live:
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(bsc.delete_container(self.container_name))
            except:
                pass

        return super(StorageCPKAsyncTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name("cpk")

    async def _create_block_blob(self, bsc, blob_name=None, data=None, cpk=None, max_concurrency=1):
        blob_name = blob_name if blob_name else self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        data = data if data else b''
        resp = await blob_client.upload_blob(data, cpk=cpk, max_concurrency=max_concurrency)
        return blob_client, resp

    async def _create_append_blob(self, bsc, cpk=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        await blob.create_append_blob(cpk=cpk)
        return blob

    async def _create_page_blob(self, bsc, cpk=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        await blob.create_page_blob(1024 * 1024, cpk=cpk)
        return blob

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_and_put_block_list(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        self.container_name = self.get_resource_name('utcontainer')
        blob_client, _ = await self._create_block_blob(bsc)
        await blob_client.stage_block('1', b'AAA', cpk=TEST_ENCRYPTION_KEY)
        await blob_client.stage_block('2', b'BBB', cpk=TEST_ENCRYPTION_KEY)
        await blob_client.stage_block('3', b'CCC', cpk=TEST_ENCRYPTION_KEY)

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = await blob_client.commit_block_list(block_list,
                                                                  cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), b'AAABBBCCC')
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_block_blob_with_chunks(self, resource_group, location, storage_account, storage_account_key):
        # parallel operation
        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        #  to force the in-memory chunks to be used
        self.config.use_byte_buffer = True

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = await self._create_block_blob(bsc, data=self.byte_data, cpk=TEST_ENCRYPTION_KEY,
                                                                     max_concurrency=2)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_block_blob_with_sub_streams(self, resource_group, location, storage_account, storage_account_key):
        # problem with the recording framework can only run live

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            retry_total=0,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        #  to force the in-memory chunks to be used
        self.config.use_byte_buffer = True

        blob_client, upload_response = await self._create_block_blob(bsc, data=self.byte_data, cpk=TEST_ENCRYPTION_KEY,
                                                                     max_concurrency=2)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_block_blob_with_single_chunk(self, resource_group, location, storage_account, storage_account_key):
        # Act
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        data = b'AAABBBCCC'
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = await self._create_block_blob(bsc, data=data, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(upload_response['etag'])
        self.assertIsNotNone(upload_response['last_modified'])
        self.assertTrue(upload_response['request_server_encrypted'])
        self.assertEqual(upload_response['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), data)
        self.assertEqual(blob.properties.etag, upload_response['etag'])
        self.assertEqual(blob.properties.last_modified, upload_response['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_from_url_and_commit(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        # create source blob and get source blob url
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = await self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        # create destination blob
        self.config.use_byte_buffer = False
        destination_blob_client, _ = await self._create_block_blob(bsc, cpk=TEST_ENCRYPTION_KEY)

        # Act part 1: make put block from url calls
        await destination_blob_client.stage_block_from_url(block_id=1, source_url=source_blob_url,
                                                           source_offset=0, source_length=4 * 1024,
                                                           cpk=TEST_ENCRYPTION_KEY)
        await destination_blob_client.stage_block_from_url(block_id=2, source_url=source_blob_url,
                                                           source_offset=4 * 1024, source_length=4 * 1024,
                                                           cpk=TEST_ENCRYPTION_KEY)

        # Assert blocks
        committed, uncommitted = await destination_blob_client.get_block_list('all')
        self.assertEqual(len(uncommitted), 2)
        self.assertEqual(len(committed), 0)

        # commit the blocks without cpk should fail
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2')]
        with self.assertRaises(HttpResponseError):
            await destination_blob_client.commit_block_list(block_list)

        # Act commit the blocks with cpk should succeed
        put_block_list_resp = await destination_blob_client.commit_block_list(block_list,
                                                                              cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(put_block_list_resp['etag'])
        self.assertIsNotNone(put_block_list_resp['last_modified'])
        self.assertTrue(put_block_list_resp['request_server_encrypted'])
        self.assertEqual(put_block_list_resp['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content
        blob = await destination_blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data[0: 8 * 1024])
        self.assertEqual(blob.properties.etag, put_block_list_resp['etag'])
        self.assertEqual(blob.properties.last_modified, put_block_list_resp['last_modified'])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_append_block(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        blob_client = await self._create_append_blob(bsc, cpk=TEST_ENCRYPTION_KEY)

        # Act
        for content in [b'AAA', b'BBB', b'CCC']:
            append_blob_prop = await blob_client.append_block(content, cpk=TEST_ENCRYPTION_KEY)

            # Assert
            self.assertIsNotNone(append_blob_prop['etag'])
            self.assertIsNotNone(append_blob_prop['last_modified'])
            self.assertTrue(append_blob_prop['request_server_encrypted'])
            self.assertEqual(append_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), b'AAABBBCCC')
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_append_block_from_url(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # chunk upload
        source_blob_client, _ = await self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        self.config.use_byte_buffer = False
        destination_blob_client = await self._create_append_blob(bsc, cpk=TEST_ENCRYPTION_KEY)

        # Act
        append_blob_prop = await destination_blob_client.append_block_from_url(source_blob_url,
                                                                               source_offset=0,
                                                                               source_length=4 * 1024,
                                                                               cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(append_blob_prop['etag'])
        self.assertIsNotNone(append_blob_prop['last_modified'])
        # TODO: verify that the swagger is correct, header wasn't added for the response
        # self.assertTrue(append_blob_prop['request_server_encrypted'])
        self.assertEqual(append_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await destination_blob_client.download_blob()

            # Act get the blob content
        blob = await destination_blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data[0: 4 * 1024])
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_append_blob_with_chunks(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        blob_client = await self._create_append_blob(bsc, cpk=TEST_ENCRYPTION_KEY)

        # Act
        append_blob_prop = await blob_client.upload_blob(self.byte_data,
                                                         blob_type=BlobType.AppendBlob, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(append_blob_prop['etag'])
        self.assertIsNotNone(append_blob_prop['last_modified'])
        self.assertTrue(append_blob_prop['request_server_encrypted'])
        self.assertEqual(append_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_update_page(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        blob_client = await self._create_page_blob(bsc, cpk=TEST_ENCRYPTION_KEY)

        # Act
        page_blob_prop = await blob_client.upload_page(self.byte_data,
                                                       offset=0,
                                                       length=len(self.byte_data),
                                                       cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(offset=0,
                                               length=len(self.byte_data),
                                               cpk=TEST_ENCRYPTION_KEY, )

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_update_page_from_url(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = await self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = source_blob_client.url + "?" + source_blob_sas

        self.config.use_byte_buffer = False
        blob_client = await self._create_page_blob(bsc, cpk=TEST_ENCRYPTION_KEY)

        # Act
        page_blob_prop = await blob_client.upload_pages_from_url(source_blob_url,
                                                                 offset=0,
                                                                 length=len(self.byte_data),
                                                                 source_offset=0,
                                                                 cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        # TODO: FIX SWAGGER
        # self.assertEqual(page_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(offset=0,
                                               length=len(self.byte_data),
                                               cpk=TEST_ENCRYPTION_KEY, )

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_page_blob_with_chunks(self, resource_group, location, storage_account, storage_account_key):
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)

        # Act
        blob_client = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        page_blob_prop = await blob_client.upload_blob(self.byte_data,
                                                       blob_type=BlobType.PageBlob,
                                                       max_concurrency=2,
                                                       cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(page_blob_prop['etag'])
        self.assertIsNotNone(page_blob_prop['last_modified'])
        self.assertTrue(page_blob_prop['request_server_encrypted'])
        self.assertEqual(page_blob_prop['encryption_key_sha256'], TEST_ENCRYPTION_KEY.key_hash)

        # Act get the blob content without cpk should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.download_blob()

        # Act get the blob content
        blob = await blob_client.download_blob(cpk=TEST_ENCRYPTION_KEY)

        # Assert content was retrieved with the cpk
        self.assertEqual(await blob.readall(), self.byte_data)
        self.assertEqual(blob.properties.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_set_blob_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        blob_client, _ = await self._create_block_blob(bsc, data=b'AAABBBCCC', cpk=TEST_ENCRYPTION_KEY)

        # Act without the encryption key should fail
        with self.assertRaises(HttpResponseError):
            await blob_client.get_blob_properties()

        # Act
        blob_props = await blob_client.get_blob_properties(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertTrue(blob_props.server_encrypted)
        self.assertEqual(blob_props.encryption_key_sha256, TEST_ENCRYPTION_KEY.key_hash)

        # Act set blob properties
        metadata = {'hello': 'world', 'number': '42', 'up': 'upval'}
        with self.assertRaises(HttpResponseError):
            await blob_client.set_blob_metadata(
                metadata=metadata,
            )

        await blob_client.set_blob_metadata(metadata=metadata, cpk=TEST_ENCRYPTION_KEY)

        # Assert
        blob_props = await blob_client.get_blob_properties(cpk=TEST_ENCRYPTION_KEY)
        md = blob_props.metadata
        self.assertEqual(3, len(md))
        self.assertEqual(md['hello'], 'world')
        self.assertEqual(md['number'], '42')
        self.assertEqual(md['up'], 'upval')
        self.assertFalse('Up' in md)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_snapshot_blob(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            transport=AiohttpTestTransport(connection_data_block_size=1024))
        await self._setup(bsc)
        blob_client, _ = await self._create_block_blob(bsc, data=b'AAABBBCCC', cpk=TEST_ENCRYPTION_KEY)

        # Act without cpk should not work
        with self.assertRaises(HttpResponseError):
            await blob_client.create_snapshot()

        # Act with cpk should work
        blob_snapshot = await blob_client.create_snapshot(cpk=TEST_ENCRYPTION_KEY)

        # Assert
        self.assertIsNotNone(blob_snapshot)
