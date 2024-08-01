# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from datetime import datetime, timedelta

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import (
    AccountSasPermissions,
    BlobBlock,
    BlobSasPermissions,
    BlobType,
    ContainerEncryptionScope,
    ContainerSasPermissions,
    generate_account_sas,
    generate_blob_sas,
    generate_container_sas,
    ResourceTypes,
)
from azure.storage.blob.aio import BlobServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
# For local testing, ensure these encryption scopes are created for your account.
# For Live pipeline, these are created by ARM template.
TEST_ENCRYPTION_SCOPE = "testscope1"
TEST_ENCRYPTION_SCOPE_2 = "testscope2"
TEST_CONTAINER_ENCRYPTION_SCOPE = ContainerEncryptionScope(default_encryption_scope="testscope1")
TEST_CONTAINER_ENCRYPTION_SCOPE_DENY_OVERRIDE = ContainerEncryptionScope(
    default_encryption_scope="testscope1",
    prevent_encryption_scope_override=True)
# ------------------------------------------------------------------------------


class TestStorageCPKAsync(AsyncStorageRecordedTestCase):
    async def _setup(self, bsc):
        self.config = bsc._config
        self.byte_data = self.get_random_bytes(10 * 1024)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                await bsc.create_container(self.container_name)
            except:
                pass

    def _teardown(self, bsc):
        if self.is_live:
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(bsc.delete_container(self.container_name))
            except:
                pass

    # --Helpers-----------------------------------------------------------------

    def _get_blob_reference(self):
        return self.get_resource_name("cpk")

    async def _create_block_blob(self, bsc, blob_name=None, data=None, encryption_scope=None, max_concurrency=1, overwrite=False):
        blob_name = blob_name if blob_name else self._get_blob_reference()
        blob_client = bsc.get_blob_client(self.container_name, blob_name)
        data = data if data else b''
        resp = await blob_client.upload_blob(data, encryption_scope=encryption_scope, max_concurrency=max_concurrency, overwrite=overwrite)
        return blob_client, resp

    async def _create_append_blob(self, bsc, encryption_scope=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        await blob.create_append_blob(encryption_scope=encryption_scope)
        return blob

    async def _create_page_blob(self, bsc, encryption_scope=None):
        blob_name = self._get_blob_reference()
        blob = bsc.get_blob_client(
            self.container_name,
            blob_name)
        await blob.create_page_blob(1024 * 1024, encryption_scope=encryption_scope)
        return blob

    # -- Test cases for APIs supporting CPK ----------------------------------------------

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_and_put_block_list(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        self.container_name = self.get_resource_name('utcontainer')
        blob_client, _ = await self._create_block_blob(bsc)
        await blob_client.stage_block('1', b'AAA', encryption_scope=TEST_ENCRYPTION_SCOPE)
        await blob_client.stage_block('2', b'BBB', encryption_scope=TEST_ENCRYPTION_SCOPE)
        await blob_client.stage_block('3', b'CCC', encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = await blob_client.commit_block_list(block_list, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert put_block_list_resp['etag'] is not None
        assert put_block_list_resp['last_modified'] is not None
        assert put_block_list_resp['request_server_encrypted']
        assert put_block_list_resp['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == b'AAABBBCCC'
        assert blob.properties.etag == put_block_list_resp['etag']
        assert blob.properties.last_modified == put_block_list_resp['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_and_put_block_list_with_blob_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        blob_name = self._get_blob_reference()
        token1 = self.generate_sas(
            generate_blob_sas,
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, write=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE,
        )
        blob_client = BlobServiceClient(self.account_url(storage_account_name, "blob"), token1)\
            .get_blob_client(self.container_name, blob_name)

        await blob_client.stage_block('1', b'AAA')
        await blob_client.stage_block('2', b'BBB')
        await blob_client.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = await blob_client.commit_block_list(block_list)

        # Assert
        assert put_block_list_resp['etag'] is not None
        assert put_block_list_resp['last_modified'] is not None
        assert put_block_list_resp['request_server_encrypted']
        assert put_block_list_resp['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()
        content = await blob.readall()

        # Assert content was retrieved with the cpk
        assert content == b'AAABBBCCC'
        assert blob.properties.etag == put_block_list_resp['etag']
        assert blob.properties.last_modified == put_block_list_resp['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE
        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_and_put_block_list_with_blob_sas_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        blob_name = self._get_blob_reference()
        token1 = self.generate_sas(
            generate_blob_sas,
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, write=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE,
        )
        blob_client = BlobServiceClient(self.account_url(storage_account_name, "blob"), token1)\
            .get_blob_client(self.container_name, blob_name)

        # both ses in SAS and encryption_scopes are both set and have DIFFERENT values will throw exception
        with pytest.raises(HttpResponseError):
            await blob_client.stage_block('1', b'AAA', encryption_scope=TEST_ENCRYPTION_SCOPE_2)

        # both ses in SAS and encryption_scopes are both set and have SAME values will succeed
        await blob_client.stage_block('1', b'AAA', encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        block_list = [BlobBlock(block_id='1')]
        # both ses in SAS and encryption_scopes are both set and have DIFFERENT values will throw exception
        with pytest.raises(HttpResponseError):
            await blob_client.commit_block_list(block_list, encryption_scope=TEST_ENCRYPTION_SCOPE_2)

        # both ses in SAS and encryption_scopes are both set and have SAME values will succeed
        put_block_list_resp = await blob_client.commit_block_list(block_list, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert put_block_list_resp['etag'] is not None
        assert put_block_list_resp['last_modified'] is not None
        assert put_block_list_resp['request_server_encrypted']
        assert put_block_list_resp['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # generate a sas with a different encryption scope
        token2 = self.generate_sas(
            generate_blob_sas,
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, write=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE_2,
        )
        blob_client_diff_encryption_scope_sas = BlobServiceClient(self.account_url(storage_account_name, "blob"), token2)\
            .get_blob_client(self.container_name, blob_name)

        # blob can be downloaded successfully no matter which encryption scope is used on the blob actually
        # the encryption scope on blob is TEST_ENCRYPTION_SCOPE and ses is TEST_ENCRYPTION_SCOPE_2 in SAS token,
        # while we can still download the blob successfully
        blob = await blob_client_diff_encryption_scope_sas.download_blob()
        content = await blob.readall()

        # Assert content was retrieved with the cpk
        assert content == b'AAA'
        assert blob.properties.etag == put_block_list_resp['etag']
        assert blob.properties.last_modified == put_block_list_resp['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE
        self._teardown(bsc)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_block_blob_with_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        #  to force the in-memory chunks to be used
        self.config.use_byte_buffer = True

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = await self._create_block_blob(
            bsc,
            data=self.byte_data,
            encryption_scope=TEST_ENCRYPTION_SCOPE,
            max_concurrency=2)

        # Assert
        assert upload_response['etag'] is not None
        assert upload_response['last_modified'] is not None
        assert upload_response['request_server_encrypted']
        assert upload_response['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data
        assert blob.properties.etag == upload_response['etag']
        assert blob.properties.last_modified == upload_response['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_block_blob_with_sub_streams(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        # create_blob_from_bytes forces the in-memory chunks to be used
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024,
            retry_total=0)
        await self._setup(bsc)
        #  to force the in-memory chunks to be used
        self.config.use_byte_buffer = True

        blob_client, upload_response = await self._create_block_blob(
            bsc,
            data=self.byte_data,
            encryption_scope=TEST_ENCRYPTION_SCOPE,
            max_concurrency=2)

        # Assert
        assert upload_response['etag'] is not None
        assert upload_response['last_modified'] is not None
        assert upload_response['request_server_encrypted']
        assert upload_response['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data
        assert blob.properties.etag == upload_response['etag']
        assert blob.properties.last_modified == upload_response['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_block_blob_with_single_chunk(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        data = b'AAABBBCCC'
        # create_blob_from_bytes forces the in-memory chunks to be used
        blob_client, upload_response = await self._create_block_blob(bsc, data=data, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert upload_response['etag'] is not None
        assert upload_response['last_modified'] is not None
        assert upload_response['request_server_encrypted']
        assert upload_response['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == data
        assert blob.properties.etag == upload_response['etag']
        assert blob.properties.last_modified == upload_response['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_block_from_url_and_commit(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        # create source blob and get source blob url
        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = await self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = self.generate_sas(
            generate_blob_sas,
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
        destination_blob_client, _ = await self._create_block_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act part 1: make put block from url calls
        await destination_blob_client.stage_block_from_url(block_id=1, source_url=source_blob_url,
                                                           source_offset=0, source_length=4 * 1024,
                                                           encryption_scope=TEST_ENCRYPTION_SCOPE)
        await destination_blob_client.stage_block_from_url(block_id=2, source_url=source_blob_url,
                                                           source_offset=4 * 1024, source_length=4 * 1024,
                                                           encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert blocks
        committed, uncommitted = await destination_blob_client.get_block_list('all')
        assert len(uncommitted) == 2
        assert len(committed) == 0

        # commit the blocks without cpk should fail
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2')]
        with pytest.raises(HttpResponseError):
            await destination_blob_client.commit_block_list(block_list)

        # Act commit the blocks with cpk should succeed
        put_block_list_resp = await destination_blob_client.commit_block_list(block_list, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert put_block_list_resp['etag'] is not None
        assert put_block_list_resp['last_modified'] is not None
        assert put_block_list_resp['request_server_encrypted']
        assert put_block_list_resp['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await destination_blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data[0: 8 * 1024]
        assert blob.properties.etag == put_block_list_resp['etag']
        assert blob.properties.last_modified == put_block_list_resp['last_modified']
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        blob_client = await self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        for content in [b'AAA', b'BBB', b'CCC']:
            append_blob_prop = await blob_client.append_block(content, encryption_scope=TEST_ENCRYPTION_SCOPE)

            # Assert
            assert append_blob_prop['etag'] is not None
            assert append_blob_prop['last_modified'] is not None
            assert append_blob_prop['request_server_encrypted']
            assert append_blob_prop['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == b'AAABBBCCC'
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_append_block_from_url(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # chunk upload
        source_blob_client, _ = await self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = self.generate_sas(
            generate_blob_sas,
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
        destination_blob_client = await self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        append_blob_prop = await destination_blob_client.append_block_from_url(source_blob_url,
                                                                               source_offset=0,
                                                                               source_length=4 * 1024,
                                                                               encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert append_blob_prop['etag'] is not None
        assert append_blob_prop['last_modified'] is not None
        assert append_blob_prop['request_server_encrypted']
        assert append_blob_prop['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await destination_blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data[0: 4 * 1024]
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_append_blob_with_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        blob_client = await self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        append_blob_prop = await blob_client.upload_blob(self.byte_data,
                                                         blob_type=BlobType.AppendBlob, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert append_blob_prop['etag'] is not None
        assert append_blob_prop['last_modified'] is not None
        assert append_blob_prop['request_server_encrypted']
        assert append_blob_prop['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        blob_client = await self._create_page_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        page_blob_prop = await blob_client.upload_page(self.byte_data,
                                                       offset=0,
                                                       length=len(self.byte_data),
                                                       encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert page_blob_prop['etag'] is not None
        assert page_blob_prop['last_modified'] is not None
        assert page_blob_prop['request_server_encrypted']
        assert page_blob_prop['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob(offset=0, length=len(self.byte_data))

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_update_page_from_url(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        source_blob_name = self.get_resource_name("sourceblob")
        self.config.use_byte_buffer = True  # Make sure using chunk upload, then we can record the request
        source_blob_client, _ = await self._create_block_blob(bsc, blob_name=source_blob_name, data=self.byte_data)
        source_blob_sas = self.generate_sas(
            generate_blob_sas,
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
        blob_client = await self._create_page_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        page_blob_prop = await blob_client.upload_pages_from_url(source_blob_url,
                                                                 offset=0,
                                                                 length=len(self.byte_data),
                                                                 source_offset=0,
                                                                 encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert page_blob_prop['etag'] is not None
        assert page_blob_prop['last_modified'] is not None
        assert page_blob_prop['request_server_encrypted']
        assert page_blob_prop['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob(offset=0, length=len(self.byte_data))

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_page_blob_with_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        # Act
        blob_client = bsc.get_blob_client(self.container_name, self._get_blob_reference())
        page_blob_prop = await blob_client.upload_blob(self.byte_data,
                                                       blob_type=BlobType.PageBlob,
                                                       max_concurrency=2,
                                                       encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert page_blob_prop['etag'] is not None
        assert page_blob_prop['last_modified'] is not None
        assert page_blob_prop['request_server_encrypted']
        assert page_blob_prop['encryption_scope'] == TEST_ENCRYPTION_SCOPE

        # Act get the blob content
        blob = await blob_client.download_blob()

        # Assert content was retrieved with the cpk
        assert await blob.readall() == self.byte_data
        assert blob.properties.encryption_scope == TEST_ENCRYPTION_SCOPE

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_set_blob_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        blob_client, _ = await self._create_block_blob(bsc, data=b'AAABBBCCC', encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act
        blob_props = await blob_client.get_blob_properties()

        # Assert
        assert blob_props.server_encrypted
        assert blob_props.encryption_scope == TEST_ENCRYPTION_SCOPE

        # Act set blob properties
        metadata = {'hello': 'world', 'number': '42', 'up': 'upval'}
        with pytest.raises(HttpResponseError):
            await blob_client.set_blob_metadata(
                metadata=metadata,
            )

        await blob_client.set_blob_metadata(metadata=metadata, encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        blob_props = await blob_client.get_blob_properties()
        md = blob_props.metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['up'] == 'upval'
        assert not 'Up' in md

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        blob_client, _ = await self._create_block_blob(bsc, data=b'AAABBBCCC', encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Act without cpk should not work
        with pytest.raises(HttpResponseError):
            await blob_client.create_snapshot()

        # Act with cpk should work
        blob_snapshot = await blob_client.create_snapshot(encryption_scope=TEST_ENCRYPTION_SCOPE)

        # Assert
        assert blob_snapshot is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_list_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)
        await self._create_block_blob(bsc, blob_name="blockblob", data=b'AAABBBCCC', encryption_scope=TEST_ENCRYPTION_SCOPE)
        await self._create_append_blob(bsc, encryption_scope=TEST_ENCRYPTION_SCOPE)

        container_client = bsc.get_container_client(self.container_name)

        generator = container_client.list_blobs(include="metadata")
        async for blob in generator:
            assert blob is not None
            # Assert: every listed blob has encryption_scope
            assert blob.encryption_scope == TEST_ENCRYPTION_SCOPE

        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_list_blobs_using_container_encryption_scope_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        await self._setup(bsc)

        token = self.generate_sas(
            generate_container_sas,
            storage_account_name,
            self.container_name,
            storage_account_key,
            permission=ContainerSasPermissions(read=True, write=True, list=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE
        )
        bsc_with_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=token,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        # blob is encrypted using TEST_ENCRYPTION_SCOPE
        await self._create_block_blob(bsc_with_sas_credential, blob_name="blockblob", data=b'AAABBBCCC', overwrite=True)
        await self._create_append_blob(bsc_with_sas_credential)

        # generate a token with TEST_ENCRYPTION_SCOPE_2
        token2 = self.generate_sas(
            generate_container_sas,
            storage_account_name,
            self.container_name,
            storage_account_key,
            permission=ContainerSasPermissions(read=True, write=True, list=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE_2
        )
        bsc_with_diff_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=token2,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        container_client = bsc_with_diff_sas_credential.get_container_client(self.container_name)

        # The ses field in SAS token when list blobs is different from the encryption scope used on creating blob, while
        # list blobs should also succeed
        generator = container_client.list_blobs(include="metadata")
        async for blob in generator:
            assert blob is not None
            # Assert: every listed blob has encryption_scope
            # and the encryption scope is the same as the one on blob creation
            assert blob.encryption_scope == TEST_ENCRYPTION_SCOPE

        self._teardown(bsc)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_with_account_encryption_scope_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        sas_token = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE_2
        )
        bsc_with_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        await self._setup(bsc_with_sas_credential)
        # blob is encrypted using TEST_ENCRYPTION_SCOPE_2
        blob_client, _ = await self._create_block_blob(bsc_with_sas_credential, blob_name="blockblob", data=b'AAABBBCCC', overwrite=True)

        sas_token2 = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE
        )
        bsc_with_account_key_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token2,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        copied_blob = self.get_resource_name('copiedblob')
        copied_blob_client = bsc_with_account_key_credential.get_blob_client(self.container_name, copied_blob)

        # TODO: to confirm with Sean/Heidi ses in SAS cannot be set for async copy.
        #  The test failed for async copy (without requires_sync=True)
        await copied_blob_client.start_copy_from_url(blob_client.url, requires_sync=True)

        props = await copied_blob_client.get_blob_properties()

        assert props.encryption_scope == TEST_ENCRYPTION_SCOPE

        self._teardown(bsc_with_sas_credential)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_blob_from_url_with_ecryption_scope(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange

        # create sas for source blob
        sas_token = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        bsc_with_sas_credential = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        await self._setup(bsc_with_sas_credential)
        blob_client, _ = await self._create_block_blob(bsc_with_sas_credential, blob_name="blockblob", data=b'AAABBBCCC', overwrite=True)

        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        copied_blob = self.get_resource_name('copiedblob')
        copied_blob_client = bsc.get_blob_client(self.container_name, copied_blob)

        await copied_blob_client.start_copy_from_url(blob_client.url, requires_sync=True,
                                               encryption_scope=TEST_ENCRYPTION_SCOPE)

        props = await copied_blob_client.get_blob_properties()

        assert props.encryption_scope == TEST_ENCRYPTION_SCOPE

        self._teardown(bsc_with_sas_credential)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_copy_with_user_delegation_encryption_scope_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        # to get user delegation key
        oauth_token_credential = self.get_credential(BlobServiceClient, is_async=True)
        service_client = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=oauth_token_credential,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        user_delegation_key = await service_client.get_user_delegation_key(datetime.utcnow(),
                                                                           datetime.utcnow() + timedelta(hours=1))

        await self._setup(service_client)

        blob_name = self.get_resource_name('blob')

        sas_token = self.generate_sas(
            generate_blob_sas,
            storage_account_name,
            self.container_name,
            blob_name,
            account_key=user_delegation_key,
            permission=BlobSasPermissions(read=True, write=True, create=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            encryption_scope=TEST_ENCRYPTION_SCOPE
        )
        bsc_with_delegation_sas = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=sas_token,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)

        # blob is encrypted using TEST_ENCRYPTION_SCOPE
        blob_client, _ = await self._create_block_blob(bsc_with_delegation_sas, blob_name=blob_name, data=b'AAABBBCCC', overwrite=True)
        props = await blob_client.get_blob_properties()

        assert props.encryption_scope == TEST_ENCRYPTION_SCOPE

        self._teardown(service_client)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_container_with_default_cpk_n(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        container_client = await bsc.create_container(
            'asynccpkcontainer',
            container_encryption_scope=TEST_CONTAINER_ENCRYPTION_SCOPE)

        container_props = await container_client.get_container_properties()
        assert container_props.encryption_scope.default_encryption_scope == \
            TEST_CONTAINER_ENCRYPTION_SCOPE.default_encryption_scope
        assert container_props.encryption_scope.prevent_encryption_scope_override == False

        async for container in bsc.list_containers(name_starts_with='asynccpkcontainer'):
            assert container.encryption_scope.default_encryption_scope == \
                TEST_CONTAINER_ENCRYPTION_SCOPE.default_encryption_scope
            assert container_props.encryption_scope.prevent_encryption_scope_override == False

        blob_client = container_client.get_blob_client("appendblob")

        # providing encryption scope when upload the blob
        resp = await blob_client.upload_blob(b'aaaa', BlobType.AppendBlob, encryption_scope=TEST_ENCRYPTION_SCOPE_2)
        # Use the provided encryption scope on the blob
        assert resp['encryption_scope'] == TEST_ENCRYPTION_SCOPE_2

        await container_client.delete_container()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_container_with_default_cpk_n_deny_override(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key,
            max_single_put_size=1024,
            min_large_block_upload_threshold=1024,
            max_block_size=1024,
            max_page_size=1024)
        container_client = await bsc.create_container(
            'asyncdenyoverridecpkcontainer',
            container_encryption_scope=TEST_CONTAINER_ENCRYPTION_SCOPE_DENY_OVERRIDE
        )

        container_props = await container_client.get_container_properties()
        assert container_props.encryption_scope.default_encryption_scope == \
            TEST_CONTAINER_ENCRYPTION_SCOPE_DENY_OVERRIDE.default_encryption_scope
        assert container_props.encryption_scope.prevent_encryption_scope_override == True

        async for container in bsc.list_containers(name_starts_with='asyncdenyoverridecpkcontainer'):
            assert container.encryption_scope.default_encryption_scope == \
                TEST_CONTAINER_ENCRYPTION_SCOPE_DENY_OVERRIDE.default_encryption_scope
            assert container_props.encryption_scope.prevent_encryption_scope_override == True
        blob_client = container_client.get_blob_client("appendblob")

        # It's not allowed to set encryption scope on the blob when the container denies encryption scope override.
        with pytest.raises(HttpResponseError):
            await blob_client.upload_blob(b'aaaa', BlobType.AppendBlob, encryption_scope=TEST_ENCRYPTION_SCOPE_2)

        resp = await blob_client.upload_blob(b'aaaa', BlobType.AppendBlob)

        assert resp['encryption_scope'] == TEST_CONTAINER_ENCRYPTION_SCOPE_DENY_OVERRIDE.default_encryption_scope

        await container_client.delete_container()
