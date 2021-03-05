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
import uuid

from datetime import datetime, timedelta

from azure.storage.blob._shared.policies import StorageContentValidation

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import GlobalStorageAccountPreparer, GlobalResourceGroupPreparer
from _shared.asynctestcase import AsyncStorageTestCase

from azure.storage.blob import (
    BlobType,
    ContentSettings,
    BlobBlock,
    StandardBlobTier,
    generate_blob_sas,
    BlobSasPermissions, CustomerProvidedEncryptionKey
)

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
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


class StorageBlockBlobTestAsync(AsyncStorageTestCase):
    #--Helpers-----------------------------------------------------------------
    async def _setup(self, storage_account, key, container_name='utcontainer'):
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account, "blob"),
            credential=key,
            connection_data_block_size=4 * 1024,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024,
            transport=AiohttpTestTransport())
        self.config = self.bsc._config
        self.container_name = self.get_resource_name(container_name)
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    def _get_blob_reference(self, prefix=TEST_BLOB_PREFIX):
        return self.get_resource_name(prefix)

    def _get_blob_with_special_chars_reference(self):
        return 'भारत¥test/testsubÐirÍ/'+self.get_resource_name('srcÆblob')

    async def _create_source_blob_url_with_special_chars(self, tags=None):
        blob_name = self._get_blob_with_special_chars_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(self.get_random_bytes(8 * 1024))
        sas_token_for_special_chars = generate_blob_sas(
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        return BlobClient.from_blob_url(blob.url, credential=sas_token_for_special_chars).url

    async def _create_blob(self, tags=None, data=b'', **kwargs):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data, tags=tags, **kwargs)
        return blob

    async def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        stream = await blob.download_blob()
        actual_data = await stream.readall()
        self.assertEqual(actual_data, expected_data)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    #--Test cases for block blobs --------------------------------------------

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_with_and_without_overwrite(
            self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob = await self._create_blob(data=b"source blob data")
        # Act
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        await new_blob_client.upload_blob(b'destination blob data')
        # Assert
        with self.assertRaises(ResourceExistsError):
            await new_blob_client.upload_blob_from_url(source_blob, overwrite=False)
        new_blob = await new_blob_client.upload_blob_from_url(source_blob, overwrite=True)
        self.assertIsNotNone(new_blob)
        new_blob_download = await new_blob_client.download_blob()
        new_blob_content = await new_blob_download.readall()
        self.assertEqual(new_blob_content, b'source blob data')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_with_existing_blob(
            self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key, container_name="testcontainer")
        blob = await self._create_blob(data=b"test data")
        # Act
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob = await new_blob_client.upload_blob_from_url(source_blob)
        # Assert
        self.assertIsNotNone(new_blob)
        downloaded_blob = await new_blob_client.download_blob()
        new_blob_content = await downloaded_blob.readall()
        self.assertEqual(new_blob_content, b'test data')

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_with_standard_tier_specified(
            self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key, container_name="testcontainer")
        blob = await self._create_blob()
        self.bsc.get_blob_client(self.container_name, blob.blob_name)
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        # Act
        source_blob = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_tier = StandardBlobTier.Hot
        await new_blob.upload_blob_from_url(source_blob, standard_blob_tier=blob_tier)

        new_blob_properties = await new_blob.get_blob_properties()

        # Assert
        self.assertEqual(new_blob_properties.blob_tier, blob_tier)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_with_destination_lease(
            self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        source_blob = await self._create_blob()
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=source_blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        await new_blob_client.upload_blob(data="test")
        new_blob_lease = await new_blob_client.acquire_lease()
        with self.assertRaises(HttpResponseError):
            await new_blob_client.upload_blob_from_url(
                source_blob_url, destination_lease="baddde9e-8247-4276-8bfa-c7a8081eba1d", overwrite=True)
        with self.assertRaises(HttpResponseError):
            await new_blob_client.upload_blob_from_url(source_blob_url)
        await new_blob_client.upload_blob_from_url(
            source_blob_url, destination_lease=new_blob_lease)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_if_match_condition(
            self, resource_group, location, storage_account, storage_account_key):
        # Act
        await self._setup(storage_account, storage_account_key)
        source_blob = await self._create_blob()
        early_test_datetime = (datetime.utcnow() - timedelta(minutes=15))
        late_test_datetime = (datetime.utcnow() + timedelta(minutes=15))
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=source_blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        await new_blob_client.upload_blob(data="fake data")

        # Assert
        with self.assertRaises(ResourceModifiedError):
            await new_blob_client.upload_blob_from_url(
                source_blob_url, if_modified_since=late_test_datetime, overwrite=True)
        await new_blob_client.upload_blob_from_url(
            source_blob_url, if_modified_since=early_test_datetime, overwrite=True)
        with self.assertRaises(ResourceModifiedError):
            await new_blob_client.upload_blob_from_url(
                source_blob_url, if_unmodified_since=early_test_datetime, overwrite=True)
        await new_blob_client.upload_blob_from_url(
            source_blob_url, if_unmodified_since=late_test_datetime, overwrite=True)
        with self.assertRaises(ResourceNotFoundError):
            await new_blob_client.upload_blob_from_url(
                source_blob_url, source_if_modified_since=late_test_datetime, overwrite=True)
        await new_blob_client.upload_blob_from_url(
            source_blob_url, source_if_modified_since=early_test_datetime, overwrite=True)
        with self.assertRaises(ResourceNotFoundError):
            await new_blob_client.upload_blob_from_url(
                source_blob_url, source_if_unmodified_since=early_test_datetime, overwrite=True)
        await new_blob_client.upload_blob_from_url(
            source_blob_url, source_if_unmodified_since=late_test_datetime, overwrite=True)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_with_cpk(self, resource_group, location, storage_account, storage_account_key):
        # Act
        await self._setup(storage_account, storage_account_key)
        source_blob = await self._create_blob(data=b"This is test data to be copied over.")
        test_cpk = CustomerProvidedEncryptionKey(key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
                                                 key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=source_blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await new_blob.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=True, cpk=test_cpk)

        # Assert
        with self.assertRaises(HttpResponseError):
            await new_blob.create_snapshot()
        await new_blob.create_snapshot(cpk=test_cpk)
        self.assertIsNotNone(new_blob.create_snapshot)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_overwrite_properties(
            self, resource_group, location, storage_account, storage_account_key):
        # Act
        await self._setup(storage_account, storage_account_key)
        source_blob_content_settings = ContentSettings(content_language='spanish')
        new_blob_content_settings = ContentSettings(content_language='english')
        source_blob_tags = {"tag1": "sourcetag", "tag2": "secondsourcetag"}
        new_blob_tags = {"tag1": "copytag"}
        new_blob_cpk = CustomerProvidedEncryptionKey(key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
                                                 key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")
        source_blob = await self._create_blob(
                                 data=b"This is test data to be copied over.",
                                 tags=source_blob_tags,
                                 content_settings=source_blob_content_settings,
                                 )
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=source_blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, source_blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await new_blob.upload_blob_from_url(source_blob_url,
                                            include_source_blob_properties=True,
                                            tags=new_blob_tags,
                                            content_settings=new_blob_content_settings,
                                            cpk=new_blob_cpk)
        new_blob_props = await new_blob.get_blob_properties(cpk=new_blob_cpk)

        # Assert that source blob properties did not take precedence.
        self.assertEqual(new_blob_props.tag_count, 1)
        self.assertEqual(new_blob_props.content_settings.content_language, new_blob_content_settings.content_language)
        self.assertEqual(new_blob_props.encryption_key_sha256, new_blob_cpk.key_hash)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_with_source_content_md5(
            self, resource_group, location, storage_account, storage_account_key):
        # Act
        await self._setup(storage_account, storage_account_key)
        source_blob = await self._create_blob(data=b"This is test data to be copied over.")
        source_blob_props = await source_blob.get_blob_properties()
        source_md5 = source_blob_props.content_settings.content_md5
        bad_source_md5 = StorageContentValidation.get_content_md5(b"this is bad data")
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=source_blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        await new_blob.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=True, source_content_md5=source_md5)
        with self.assertRaises(HttpResponseError):
            await new_blob.upload_blob_from_url(
                source_blob_url, include_source_blob_properties=False, source_content_md5=bad_source_md5)
        new_blob_props = await new_blob.get_blob_properties()
        new_blob_content_md5 = new_blob_props.content_settings.content_md5
        self.assertEqual(new_blob_content_md5, source_md5)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_from_url_source_and_destination_properties(
            self, resource_group, location, storage_account, storage_account_key):
        # Act
        await self._setup(storage_account, storage_account_key)
        content_settings = ContentSettings(
                content_type='application/octet-stream',
                content_language='spanish',
                content_disposition='inline'
        )
        source_blob = await self._create_blob(
                                 data=b"This is test data to be copied over.",
                                 tags={"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"},
                                 content_settings=content_settings,
                                 standard_blob_tier=StandardBlobTier.Cool
                                 )
        await source_blob.acquire_lease()
        source_blob_props = await source_blob.get_blob_properties()
        sas = generate_blob_sas(account_name=storage_account.name, account_key=storage_account_key,
                                container_name=self.container_name, blob_name=source_blob.blob_name,
                                permission=BlobSasPermissions(read=True), expiry=datetime.utcnow() + timedelta(hours=1))
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account, "blob"), self.container_name, source_blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob_copy1 = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob_copy2 = self.bsc.get_blob_client(self.container_name, 'blob2copy')
        await new_blob_copy1.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=True)
        await new_blob_copy2.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=False)

        new_blob_copy1_props = await new_blob_copy1.get_blob_properties()
        new_blob_copy2_props = await new_blob_copy2.get_blob_properties()

        # Assert
        self.assertEqual(new_blob_copy1_props.content_settings.content_language,
                         source_blob_props.content_settings.content_language)
        self.assertNotEqual(new_blob_copy2_props.content_settings.content_language,
                            source_blob_props.content_settings.content_language)

        self.assertEqual(source_blob_props.lease.status, 'locked')
        self.assertEqual(new_blob_copy1_props.lease.status, 'unlocked')
        self.assertEqual(new_blob_copy2_props.lease.status, 'unlocked')

        self.assertEqual(source_blob_props.blob_tier, 'Cool')
        self.assertEqual(new_blob_copy1_props.blob_tier, 'Hot')
        self.assertEqual(new_blob_copy2_props.blob_tier, 'Hot')

        self.assertEqual(source_blob_props.tag_count, 3)
        self.assertEqual(new_blob_copy1_props.tag_count, None)
        self.assertEqual(new_blob_copy2_props.tag_count, None)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        # Arrange
        blob = await self._create_blob()

        # Act
        for i in range(5):
            headers = await blob.stage_block(i, 'block {0}'.format(i).encode('utf-8'))
            self.assertIn('content_crc64', headers)

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_copy_blob_async(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        dest_blob = await self._create_blob()
        source_blob_url = await self._create_source_blob_url_with_special_chars()

        # Act
        copy_props = await dest_blob.start_copy_from_url(source_blob_url, requires_sync=True)

        # Assert
        self.assertIsNotNone(copy_props)
        self.assertIsNotNone(copy_props['copy_id'])
        self.assertEqual('success', copy_props['copy_status'])

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_from_url_and_commit(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        dest_blob = await self._create_blob()
        source_blob_url = await self._create_source_blob_url_with_special_chars()
        split = 4 * 1024
        # Act part 1: make put block from url calls
        await dest_blob.stage_block_from_url(
            block_id=1,
            source_url=source_blob_url,
            source_offset=0,
            source_length=split)
        await dest_blob.stage_block_from_url(
            block_id=2,
            source_url=source_blob_url,
            source_offset=split,
            source_length=split)

        # Assert blocks
        committed, uncommitted = await dest_blob.get_block_list('all')
        self.assertEqual(len(uncommitted), 2)
        self.assertEqual(len(committed), 0)
        # Act part 2: commit the blocks
        await dest_blob.commit_block_list(['1', '2'])
        committed, uncommitted = await dest_blob.get_block_list('all')
        self.assertEqual(len(uncommitted), 0)
        self.assertEqual(len(committed), 2)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_with_response(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account.name, storage_account_key)
        # Arrange
        def return_response(resp, _, headers):
            return (resp, headers)

        blob = await self._create_blob()

        # Act
        resp, headers = await blob.stage_block(0, 'block 0', cls=return_response)

        # Assert
        self.assertEqual(201, resp.http_response.status_code)
        self.assertIn('x-ms-content-crc64', headers)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_unicode(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        # Arrange
        blob = await self._create_blob()

        # Act
        headers = await blob.stage_block('1', u'啊齄丂狛狜')
        self.assertIn('content_crc64', headers)

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_with_md5(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob = await self._create_blob()

        # Act
        await blob.stage_block(1, b'block', validate_content=True)

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_list(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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
        actual = await content.readall()
        self.assertEqual(actual, b'AAABBBCCC')
        self.assertEqual(content.properties.etag, put_block_list_resp.get('etag'))
        self.assertEqual(content.properties.last_modified, put_block_list_resp.get('last_modified'))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_list_invalid_block_id(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_block_list_with_md5(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.stage_block('1', b'AAA')
        await blob.stage_block('2', b'BBB')
        await blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob.commit_block_list(block_list, validate_content=True)

        # Assert
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def _test_put_block_list_with_blob_tier_specified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob_client.stage_block('1', b'AAA')
        await blob_client.stage_block('2', b'BBB')
        await blob_client.stage_block('3', b'CCC')
        blob_tier = StandardBlobTier.Cool

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        await blob_client.commit_block_list(block_list,
                                            standard_blob_tier=blob_tier)

        # Assert
        blob_properties = await blob_client.get_blob_properties()
        self.assertEqual(blob_properties.blob_tier, blob_tier)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='storagename')
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_block_list_no_blocks(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob = await self._create_blob(tags=tags)

        # Act
        with self.assertRaises(ResourceModifiedError):
            await blob.get_block_list('all', if_tags_match_condition="\"condition tag\"='wrong tag'")
        block_list = await blob.get_block_list('all', if_tags_match_condition="\"tag1\"='firsttag'")

        # Assert
        self.assertIsNotNone(block_list)
        self.assertEqual(len(block_list[1]), 0)
        self.assertEqual(len(block_list[0]), 0)


    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_block_list_uncommitted_blocks(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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


    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_block_list_committed_blocks(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_blob_content_md5(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob1_name = self._get_blob_reference(prefix="blob1")
        blob2_name = self._get_blob_reference(prefix="blob2")
        blob1 = self.bsc.get_blob_client(self.container_name, blob1_name)
        blob2 = self.bsc.get_blob_client(self.container_name, blob2_name)
        data1 = b'hello world'
        data2 = b'hello world this wont work'

        # Act
        await blob1.upload_blob(data1, overwrite=True)
        blob1_props = await blob1.get_blob_properties()
        blob1_md5 = blob1_props.content_settings.content_md5
        blob2_content_settings = ContentSettings(content_md5=blob1_md5)

        # Passing data that does not match the md5
        with self.assertRaises(HttpResponseError):
            await blob2.upload_blob(data2, content_settings=blob2_content_settings)
        # Correct data and corresponding md5
        await blob2.upload_blob(data1, content_settings=blob2_content_settings)
        blob2_props = await blob2.get_blob_properties()
        blob2_md5 = blob2_props.content_settings.content_md5
        self.assertEqual(blob1_md5, blob2_md5)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_small_block_blob_with_no_overwrite(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_small_block_blob_with_overwrite(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_block_blob_with_no_overwrite(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = await blob.upload_blob(data1, overwrite=True, metadata={'blobdata': 'data1'})

        with self.assertRaises(ResourceExistsError):
            await blob.upload_blob(data2, overwrite=False, metadata={'blobdata': 'data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data1)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.metadata, {'blobdata': 'data1'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_large_block_blob_with_overwrite(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = await blob.upload_blob(data1, overwrite=True, metadata={'blobdata': 'data1'})
        update_resp = await blob.upload_blob(data2, overwrite=True, metadata={'blobdata': 'data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data2)
        self.assertEqual(props.etag, update_resp.get('etag'))
        self.assertEqual(props.last_modified, update_resp.get('last_modified'))
        self.assertEqual(props.blob_type, BlobType.BlockBlob)
        self.assertEqual(props.metadata, {'blobdata': 'data2'})
        self.assertEqual(props.size, LARGE_BLOB_SIZE + 512)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_single_put(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_0_bytes(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_from_bytes_blob_unicode(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_from_bytes_blob_with_lease_id(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob = await self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        lease = await blob.acquire_lease()

        # Act
        create_resp = await blob.upload_blob(data, lease=lease)

        # Assert
        output = await blob.download_blob(lease=lease)
        actual = await output.readall()
        self.assertEqual(actual, data)
        self.assertEqual(output.properties.etag, create_resp.get('etag'))
        self.assertEqual(output.properties.last_modified, create_resp.get('last_modified'))

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_with_index(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data[3:])

        # Assert
        db = await blob.download_blob()
        output = await db.readall()
        self.assertEqual(data[3:], output)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_with_index_and_count(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data[3:], length=5)

        # Assert
        db = await blob.download_blob()
        output = await db.readall()
        self.assertEqual(data[3:8], output)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_frm_bytes_with_index_cnt_props(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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
        output = await db.readall()
        self.assertEqual(data[3:8],output)
        properties = await blob.get_blob_properties()
        self.assertEqual(properties.content_settings.content_type, content_settings.content_type)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_bytes_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data, length=LARGE_BLOB_SIZE, max_concurrency=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def _test_create_blob_from_bytes_with_blob_tier_specified(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'
        blob_tier = StandardBlobTier.Cool

        # Act
        await blob_client.upload_blob(data, standard_blob_tier=blob_tier)
        blob_properties = await blob_client.get_blob_properties()

        # Assert
        self.assertEqual(blob_properties.blob_tier, blob_tier)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_path(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_path_non_parallel(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        FILE_PATH = 'from_path_non_parallel.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream, length=100, max_concurrency=1)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self.assertEqual(props.etag, create_resp.get('etag'))
        self.assertEqual(props.last_modified, create_resp.get('last_modified'))
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def _test_upload_blob_from_path_non_parallel_with_standard_blob_tier(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        FILE_PATH = 'non_parallel_with_standard_blob_tier.temp.{}.dat'.format(str(uuid.uuid4()))
        data = self.get_random_bytes(100)
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_tier = StandardBlobTier.Cool
        # Act
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, length=100, max_concurrency=1, standard_blob_tier=blob_tier)
        props = await blob.get_blob_properties()

        # Assert
        self.assertEqual(props.blob_tier, blob_tier)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_path_with_progress(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_path_with_progressasync.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_path_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path_with_propertiesasync.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_stream_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_stream_chunked_uploadasync.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_frm_stream_nonseek_chunk_upload_knwn_size(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        blob_size = len(data) - 66
        FILE_PATH = 'create_frm_stream_nonseek_chunk_upload_knwn_sizeasync.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTestAsync.NonSeekableFile(stream)
            await blob.upload_blob(non_seekable_file, length=blob_size, max_concurrency=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_blob_frm_strm_nonseek_chunk_upld_unkwn_size(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'strm_nonseek_chunk_upld_unkwn_size_async.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = StorageBlockBlobTestAsync.NonSeekableFile(stream)
            await blob.upload_blob(non_seekable_file, max_concurrency=1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_stream_with_progress_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'from_stream_with_progress_chunked_upload.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_stream_chunked_upload_with_count(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_stream_chunked_upload_with.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            resp = await blob.upload_blob(stream, length=blob_size)

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_frm_stream_chu_upld_with_countandprops(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = '_frm_stream_chu_upld_with_count.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_stream_chunked_upload_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        await self._setup(storage_account, storage_account_key)
        # Arrange
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = '_from_stream_chunked_upload_with_propert.temp.{}.dat'.format(str(uuid.uuid4()))
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
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def _test_create_blob_from_stream_chunked_upload_with_properties(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'tream_chunked_upload_with_properti.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_tier = StandardBlobTier.Cool

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2,
                                   standard_blob_tier=blob_tier)

        properties = await blob.get_blob_properties()

        # Assert
        self.assertEqual(properties.blob_tier, blob_tier)
        self._teardown(FILE_PATH)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_text(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_text_with_encoding(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        await blob.upload_blob(text, encoding='utf-16')

        # Assert
        await self.assertBlobEqual(self.container_name, blob_name, data)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_text_with_encoding_and_progress(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_from_text_chunked_upload(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live
        await self._setup(storage_account, storage_account_key)

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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_md5(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        await blob.upload_blob(data, validate_content=True)

        # Assert

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_blob_with_md5_chunked(self, resource_group, location, storage_account, storage_account_key):
        # parallel tests introduce random order of requests, can only run live

        # Arrange
        await self._setup(storage_account, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data, validate_content=True)

        # Assert


#------------------------------------------------------------------------------
