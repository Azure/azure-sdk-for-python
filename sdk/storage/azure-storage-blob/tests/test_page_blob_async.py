# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import uuid
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceModifiedError
from azure.mgmt.storage.aio import StorageManagementClient

from azure.storage.blob import (
    BlobImmutabilityPolicyMode,
    BlobProperties,
    BlobSasPermissions,
    BlobType,
    ImmutabilityPolicy,
    PremiumPageBlobTier,
    SequenceNumberAction,
    generate_blob_sas
)
from azure.storage.blob.aio import BlobClient, BlobServiceClient
from azure.storage.blob._shared.policies import StorageContentValidation
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from test_helpers_async import ProgressTracker
from settings.testcase import BlobPreparer


#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
LARGE_BLOB_SIZE = 64 * 1024 + 512
EIGHT_TB = 8 * 1024 * 1024 * 1024 * 1024
SOURCE_BLOB_SIZE = 8 * 1024
#------------------------------------------------------------------------------s

# class AiohttpTestTransport(AioHttpTransport):
#     """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
#     """
#     async def send(self, request, **config):
#         response = await super(AiohttpTestTransport, self).send(request, **config)
#         if not isinstance(response.headers, CIMultiDictProxy):
#             response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
#             response.content_type = response.headers.get("content-type")
#         return response


class TestStoragePageBlobAsync(AsyncStorageRecordedTestCase):
    #--Helpers-----------------------------------------------------------------

    async def _setup(self, bsc):
        self.config = bsc._config
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        if self.is_live:
            try:
                await bsc.create_container(self.container_name)
                await bsc.create_container(self.source_container_name)
            except:
                pass

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    def _get_blob_reference(self, bsc):
        return bsc.get_blob_client(
            self.container_name,
            self.get_resource_name(TEST_BLOB_PREFIX))

    async def _create_blob(self, bsc, length=512, sequence_number=None, tags=None):
        blob = self._get_blob_reference(bsc)
        await blob.create_page_blob(size=length, sequence_number=sequence_number, tags=tags)
        return blob

    async def _create_source_blob(self, bs, data, offset, length):
        blob_client = bs.get_blob_client(self.source_container_name,
                                              self.get_resource_name(TEST_BLOB_PREFIX))
        await blob_client.create_page_blob(size=length)
        await blob_client.upload_page(data, offset=offset, length=length)
        return blob_client

    async def _create_sparse_page_blob(self, bsc, size=1024*1024, data=''):
        blob_client = self._get_blob_reference(bsc)
        await blob_client.create_page_blob(size=size)

        range_start = 8*1024 + 512

        # the page blob will be super sparse like this
        # :'start                         some data                     end   '
        await blob_client.upload_page(data, offset=range_start, length=len(data))

        return blob_client

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

    async def assertBlobEqual(self, container_name, blob_name, expected_data, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        stream = await blob.download_blob()
        actual_data = await stream.readall()
        assert actual_data == expected_data

    async def assertRangeEqual(self, container_name, blob_name, expected_data, offset, length, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        stream = await blob.download_blob(offset=offset, length=length)
        actual_data = await stream.readall()
        assert actual_data == expected_data

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # --Test cases for page blobs --------------------------------------------

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_oauth(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        account_url = self.account_url(storage_account_name, "blob")
        if not isinstance(account_url, str):
            account_url = account_url.encode('utf-8')
            storage_account_key = storage_account_key.encode('utf-8')
        bsc = BlobServiceClient(account_url, credential=storage_account_key,
                                connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        access_token = await self.generate_oauth_token().get_token("https://storage.azure.com/.default")
        token = "Bearer {}".format(access_token.token)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        destination_blob_client = await self._create_blob(bsc, length=SOURCE_BLOB_SIZE)

        # Assert failure without providing token
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(
                source_blob_client.url, offset=0, length=8 * 1024, source_offset=0)
        # Assert it works with oauth token
        await destination_blob_client.upload_pages_from_url(
            source_blob_client.url, offset=0, length=8 * 1024, source_offset=0, source_authorization=token)
        # Assert destination blob has right content
        destination_blob = await destination_blob_client.download_blob()
        destination_blob_data = await destination_blob.readall()
        assert source_blob_data == destination_blob_data

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        resp = await blob.create_page_blob(1024)

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert await blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_immutability_policy(self, **kwargs):
        # Arrange
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")

        bsc = BlobServiceClient(self.account_url(versioned_storage_account_name, "blob"), credential=versioned_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = self.get_resource_name("vlwblob")
        blob = bsc.get_blob_client(container_name, blob_name)

        # Act
        immutability_policy = ImmutabilityPolicy(expiry_time=datetime.utcnow() + timedelta(seconds=5),
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp = await blob.create_page_blob(1024,
                                           immutability_policy=immutability_policy,
                                           legal_hold=True)
        props = await blob.get_blob_properties()

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert props['has_legal_hold']
        assert props['immutability_policy']['expiry_time'] is not None
        assert props['immutability_policy']['policy_mode'] is not None

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_page_blob_returns_vid(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        resp = await blob.create_page_blob(1024)

        # Assert
        assert resp['version_id'] is not None
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert await blob.get_blob_properties()

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_with_metadata(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        # Arrange
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        resp = await blob.create_page_blob(512, metadata=metadata)

        # Assert
        md = await blob.get_blob_properties()
        assert md.metadata == metadata

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_put_page_with_lease_id(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)
        lease = await blob.acquire_lease()

        # Act
        data = self.get_random_bytes(512)
        await blob.upload_page(data, offset=0, length=512, lease=lease)

        # Assert
        content = await blob.download_blob(lease=lease)
        actual = await content.readall()
        assert actual == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_put_page_with_lease_id_and_if_tags(self, **kwargs):
        # Arrange
        blob_storage_account_name = kwargs.pop("blob_storage_account_name")
        blob_storage_account_key = kwargs.pop("blob_storage_account_key")

        bsc = BlobServiceClient(self.account_url(blob_storage_account_name, "blob"), credential=blob_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob = await self._create_blob(bsc, tags=tags)
        with pytest.raises(ResourceModifiedError):
            await blob.acquire_lease(if_tags_match_condition="\"tag1\"='first tag'")
        lease = await blob.acquire_lease(if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Act
        data = self.get_random_bytes(512)
        with pytest.raises(ResourceModifiedError):
            await blob.upload_page(data, offset=0, length=512, lease=lease, if_tags_match_condition="\"tag1\"='first tag'")
        await blob.upload_page(data, offset=0, length=512, lease=lease, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        page_ranges, cleared = await blob.get_page_ranges()

        # Assert
        content = await (await blob.download_blob(lease=lease)).readall()
        assert content == data
        assert 1 == len(page_ranges)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)

        # Act
        data = self.get_random_bytes(512)
        resp = await blob.upload_page(data, offset=0, length=512)

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert resp.get('blob_sequence_number') is not None
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_8tb_blob(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        resp = await blob.create_page_blob(EIGHT_TB)
        props = await blob.get_blob_properties()
        page_ranges, cleared = await blob.get_page_ranges()

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert isinstance(props, BlobProperties)
        assert props.size == EIGHT_TB
        assert 0 == len(page_ranges)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_larger_than_8tb_blob_fail(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)

        # Act
        with pytest.raises(HttpResponseError):
            await blob.create_page_blob(EIGHT_TB + 1)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_8tb_blob_page(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        await blob.create_page_blob(EIGHT_TB)

        # Act
        data = self.get_random_bytes(512)
        start_offset = EIGHT_TB - 512
        length = 512
        resp = await blob.upload_page(data, offset=start_offset, length=length)
        props = await blob.get_blob_properties()
        page_ranges, cleared = await blob.get_page_ranges()

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert resp.get('blob_sequence_number') is not None
        await self.assertRangeEqual(self.container_name, blob.blob_name, data, start_offset, length, bsc)
        assert props.size == EIGHT_TB
        assert 1 == len(page_ranges)
        assert page_ranges[0]['start'] == start_offset
        assert page_ranges[0]['end'] == start_offset + length - 1

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_with_md5(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)

        # Act
        data = self.get_random_bytes(512)
        resp = await blob.upload_page(data, offset=0, length=512, validate_content=True)
        # Assert

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_clear_page(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)

        # Act
        resp = await blob.clear_page(offset=0, length=512)
        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert resp.get('blob_sequence_number') is not None
        await self.assertBlobEqual(self.container_name, blob.blob_name, b'\x00' * 512, bsc)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_put_page_if_sequence_number_lt_success(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)

        start_sequence = 10
        await blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        await blob.upload_page(data, offset=0, length=512, if_sequence_number_lt=start_sequence + 1)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_if_sequence_number_lt_failure(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        await blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with pytest.raises(HttpResponseError):
            await blob.upload_page(data, offset=0, length=512, if_sequence_number_lt=start_sequence)

        # Assert

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_if_sequence_number_lte_success(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        await blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        await blob.upload_page(data, offset=0, length=512, if_sequence_number_lte=start_sequence)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_if_sequence_number_lte_failure(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        await blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with pytest.raises(HttpResponseError):
            await blob.upload_page(data, offset=0, length=512, if_sequence_number_lte=start_sequence - 1)

        # Assert

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_if_sequence_number_eq_success(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        await blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        await blob.upload_page(data, offset=0, length=512, if_sequence_number_eq=start_sequence)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_if_sequence_number_eq_failure(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)
        start_sequence = 10
        await blob.create_page_blob(512, sequence_number=start_sequence)

        # Act
        with pytest.raises(HttpResponseError):
            await blob.upload_page(data, offset=0, length=512, if_sequence_number_eq=start_sequence - 1)

        # Assert

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, offset=0, length=4 * 1024, source_offset=0)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, offset=4 * 1024,
                                                                   length=4 * 1024, source_offset=4 * 1024)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_and_validate_content_md5(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        src_md5 = StorageContentValidation.get_content_md5(source_blob_data)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   source_content_md5=src_md5)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                source_content_md5=StorageContentValidation.get_content_md5(
                                                                    b"POTATO"))

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_source_if_modified(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = await source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   source_if_modified_since=source_properties.get(
                                                                       'last_modified') - timedelta(
                                                                       hours=15))
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                source_if_modified_since=source_properties.get(
                                                                    'last_modified'))

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_source_if_unmodified(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = await source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   source_if_unmodified_since=source_properties.get(
                                                                       'last_modified'))
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                source_if_unmodified_since=source_properties.get(
                                                                    'last_modified') - timedelta(
                                                                    hours=15))

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_source_if_match(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = await source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
            source_etag=source_properties.get('etag'),
            source_match_condition=MatchConditions.IfNotModified)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(
                source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
                source_etag='0x111111111111111',
                source_match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_source_if_none_match(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = await source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
            source_etag='0x111111111111111', source_match_condition=MatchConditions.IfModified)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(
                source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
                source_etag=source_properties.get('etag'), source_match_condition=MatchConditions.IfModified)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_if_modified(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = await source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   if_modified_since=source_properties.get(
                                                                       'last_modified') - timedelta(
                                                                       minutes=15))
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                if_modified_since=blob_properties.get(
                                                                    'last_modified'))

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_if_unmodified(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        source_properties = await source_blob_client.get_blob_properties()
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   if_unmodified_since=source_properties.get(
                                                                       'last_modified') + timedelta(minutes=15))
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                if_unmodified_since=source_properties.get(
                                                                    'last_modified') - timedelta(
                                                                    minutes=15))

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_if_match(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = self.generate_sas(
            generate_blob_sas,
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)
        destination_blob_properties = await destination_blob_client.get_blob_properties()

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(
            source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
            etag=destination_blob_properties.get('etag'),
            match_condition=MatchConditions.IfNotModified)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(
                source_blob_client.url + "?" + sas, 0, SOURCE_BLOB_SIZE, 0,
                etag='0x111111111111111',
                match_condition=MatchConditions.IfNotModified)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_if_none_match(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   etag='0x111111111111111',
                                                                   match_condition=MatchConditions.IfModified)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                etag=blob_properties.get('etag'),
                                                                match_condition=MatchConditions.IfModified)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_sequence_number_lt(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        start_sequence = 10
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE, sequence_number=start_sequence)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   if_sequence_number_lt=start_sequence + 1)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                if_sequence_number_lt=start_sequence)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_sequence_number_lte(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        start_sequence = 10
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE, sequence_number=start_sequence)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   if_sequence_number_lte=start_sequence)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                if_sequence_number_lte=start_sequence - 1)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_upload_pages_from_url_with_sequence_number_eq(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        start_sequence = 10
        source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        source_blob_client = await self._create_source_blob(bsc, source_blob_data, 0, SOURCE_BLOB_SIZE)
        sas = generate_blob_sas(
            source_blob_client.account_name,
            source_blob_client.container_name,
            source_blob_client.blob_name,
            snapshot=source_blob_client.snapshot,
            account_key=source_blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True, delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        destination_blob_client = await self._create_blob(bsc, SOURCE_BLOB_SIZE, sequence_number=start_sequence)

        # Act: make update page from url calls
        resp = await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas,
                                                                   0,
                                                                   SOURCE_BLOB_SIZE,
                                                                   0,
                                                                   if_sequence_number_eq=start_sequence)
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

        # Assert the destination blob is constructed correctly
        blob_properties = await destination_blob_client.get_blob_properties()
        await self.assertBlobEqual(self.container_name, destination_blob_client.blob_name, source_blob_data, bsc)
        assert blob_properties.get('etag') == resp.get('etag')
        assert blob_properties.get('last_modified') == resp.get('last_modified')

        # Act part 2: put block from url with wrong md5
        with pytest.raises(HttpResponseError):
            await destination_blob_client.upload_pages_from_url(source_blob_client.url + "?" + sas, 0,
                                                                SOURCE_BLOB_SIZE,
                                                                0,
                                                                if_sequence_number_eq=start_sequence + 1)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_unicode(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)

        # Act
        data = u'abcdefghijklmnop' * 32
        resp = await blob.upload_page(data, offset=0, length=512)

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_page_ranges(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        await self._setup(bsc)
        blob: BlobClient = await self._create_blob(bsc, length=2560)
        data = self.get_random_bytes(512)
        await blob.upload_page(data, offset=0, length=512)
        await blob.upload_page(data*2, offset=1024, length=1024)

        # Act
        ranges = []
        async for r in blob.list_page_ranges():
            ranges.append(r)

        # Assert
        assert ranges is not None
        assert 2 == len(ranges)
        assert 0 == ranges[0].start
        assert 511 == ranges[0].end
        assert not ranges[0].cleared
        assert 1024 == ranges[1].start
        assert 2047 == ranges[1].end
        assert not ranges[1].cleared

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_page_ranges_pagination(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        await self._setup(bsc)
        blob: BlobClient = await self._create_blob(bsc, length=3072)
        data = self.get_random_bytes(512)
        await blob.upload_page(data, offset=0, length=512)
        await blob.upload_page(data, offset=1024, length=512)
        await blob.upload_page(data * 2, offset=2048, length=1024)

        # Act
        page_list = blob.list_page_ranges(results_per_page=2).by_page()
        first_page = await page_list.__anext__()
        items_on_page1 = list()
        async for item in first_page:
            items_on_page1.append(item)
        second_page = await page_list.__anext__()
        items_on_page2 = list()
        async for item in second_page:
            items_on_page2.append(item)

        # Assert
        assert 2 == len(items_on_page1)
        assert 1 == len(items_on_page2)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_page_ranges_empty(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        await self._setup(bsc)
        blob: BlobClient = await self._create_blob(bsc, length=2560)

        # Act
        ranges = []
        async for r in blob.list_page_ranges():
            ranges.append(r)

        # Assert
        assert ranges is not None
        assert isinstance(ranges, list)
        assert 0 == len(ranges)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_page_ranges_offset(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        await self._setup(bsc)
        blob: BlobClient = await self._create_blob(bsc, length=2560)
        data = self.get_random_bytes(512)
        await blob.upload_page(data * 3, offset=0, length=1536)
        await blob.upload_page(data, offset=2048, length=512)

        # Act
        # Length with no offset, should raise ValueError
        with pytest.raises(ValueError):
            async for r in blob.list_page_ranges(length=1024):
                pass

        ranges = []
        async for r in blob.list_page_ranges(offset=1024, length=1024):
            ranges.append(r)

        # Assert
        assert ranges is not None
        assert isinstance(ranges, list)
        assert 1 == len(ranges)
        assert 1024 == ranges[0].start
        assert 1535 == ranges[0].end
        assert not ranges[0].cleared

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_page_ranges_diff(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        await self._setup(bsc)
        blob: BlobClient = await self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(1536)
        snapshot1 = await blob.create_snapshot()
        await blob.upload_page(data, offset=0, length=1536)
        snapshot2 = await blob.create_snapshot()
        await blob.clear_page(offset=512, length=512)

        # Act
        ranges1 = []
        async for r in blob.list_page_ranges(previous_snapshot=snapshot1):
            ranges1.append(r)
        ranges2 = []
        async for r in blob.list_page_ranges(previous_snapshot=snapshot2['snapshot']):
            ranges2.append(r)

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert 3 == len(ranges1)
        assert 0 == ranges1[0].start
        assert 511 == ranges1[0].end
        assert not ranges1[0].cleared
        assert 512 == ranges1[1].start
        assert 1023 == ranges1[1].end
        assert ranges1[1].cleared
        assert 1024 == ranges1[2].start
        assert 1535 == ranges1[2].end
        assert not ranges1[2].cleared

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert 1 == len(ranges2)
        assert 512 == ranges2[0].start
        assert 1023 == ranges2[0].end
        assert ranges2[0].cleared

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_list_page_ranges_diff_pagination(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        await self._setup(bsc)
        blob: BlobClient = await self._create_blob(bsc, length=2048)
        data = self.get_random_bytes(1536)
        snapshot = await blob.create_snapshot()
        await blob.upload_page(data, offset=0, length=1536)
        await blob.clear_page(offset=512, length=512)

        # Act
        page_list = blob.list_page_ranges(previous_snapshot=snapshot, results_per_page=2).by_page()
        first_page = await page_list.__anext__()
        items_on_page1 = list()
        async for item in first_page:
            items_on_page1.append(item)
        second_page = await page_list.__anext__()
        items_on_page2 = list()
        async for item in second_page:
            items_on_page2.append(item)

        # Assert
        assert 2 == len(items_on_page1)
        assert 1 == len(items_on_page2)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_get_page_ranges_no_pages(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)

        # Act
        ranges, cleared = await blob.get_page_ranges()

        # Assert
        assert ranges is not None
        assert isinstance(ranges, list)
        assert len(ranges) == 0

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_get_page_ranges_2_pages(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc, 2048)
        data = self.get_random_bytes(512)
        resp1 = await blob.upload_page(data, offset=0, length=512)
        resp2 = await blob.upload_page(data, offset=1024, length=512)

        # Act
        ranges, cleared = await blob.get_page_ranges()

        # Assert
        assert ranges is not None
        assert isinstance(ranges, list)
        assert len(ranges) == 2
        assert ranges[0]['start'] == 0
        assert ranges[0]['end'] == 511
        assert ranges[1]['start'] == 1024
        assert ranges[1]['end'] == 1535

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_get_page_ranges_diff(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc, 2048)
        data = self.get_random_bytes(1536)
        snapshot1 = await blob.create_snapshot()
        await blob.upload_page(data, offset=0, length=1536)
        snapshot2 = await blob.create_snapshot()
        await blob.clear_page(offset=512, length=512)

        # Act
        ranges1, cleared1 = await blob.get_page_ranges(previous_snapshot_diff=snapshot1)
        ranges2, cleared2 = await blob.get_page_ranges(previous_snapshot_diff=snapshot2['snapshot'])

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert len(ranges1) == 2
        assert isinstance(cleared1, list)
        assert len(cleared1) == 1
        assert ranges1[0]['start'] == 0
        assert ranges1[0]['end'] == 511
        assert cleared1[0]['start'] == 512
        assert cleared1[0]['end'] == 1023
        assert ranges1[1]['start'] == 1024
        assert ranges1[1]['end'] == 1535

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert len(ranges2) == 0
        assert isinstance(cleared2, list)
        assert len(cleared2) == 1
        assert cleared2[0]['start'] == 512
        assert cleared2[0]['end'] == 1023

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_get_page_managed_disk_diff(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc, 2048)
        data = self.get_random_bytes(1536)

        snapshot1 = await blob.create_snapshot()
        snapshot_blob1 = BlobClient.from_blob_url(blob.url, credential=storage_account_key, snapshot=snapshot1['snapshot'])
        sas_token1 = generate_blob_sas(
            snapshot_blob1.account_name,
            snapshot_blob1.container_name,
            snapshot_blob1.blob_name,
            snapshot=snapshot_blob1.snapshot,
            account_key=snapshot_blob1.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        await blob.upload_page(data, offset=0, length=1536)

        snapshot2 = await blob.create_snapshot()
        snapshot_blob2 = BlobClient.from_blob_url(blob.url, credential=storage_account_key, snapshot=snapshot2['snapshot'])
        sas_token2 = generate_blob_sas(
            snapshot_blob2.account_name,
            snapshot_blob2.container_name,
            snapshot_blob2.blob_name,
            snapshot=snapshot_blob2.snapshot,
            account_key=snapshot_blob2.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        await blob.clear_page(offset=512, length=512)

        # Act
        ranges1, cleared1 = await blob.get_page_range_diff_for_managed_disk(snapshot_blob1.url + '&' + sas_token1)
        ranges2, cleared2 = await blob.get_page_range_diff_for_managed_disk(snapshot_blob2.url + '&' + sas_token2)

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert len(ranges1) == 2
        assert isinstance(cleared1, list)
        assert len(cleared1) == 1
        assert ranges1[0]['start'] == 0
        assert ranges1[0]['end'] == 511
        assert cleared1[0]['start'] == 512
        assert cleared1[0]['end'] == 1023
        assert ranges1[1]['start'] == 1024
        assert ranges1[1]['end'] == 1535

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert len(ranges2) == 0
        assert isinstance(cleared2, list)
        assert len(cleared2) == 1
        assert cleared2[0]['start'] == 512
        assert cleared2[0]['end'] == 1023

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_update_page_fail(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc, 2048)
        data = self.get_random_bytes(512)
        resp1 = await blob.upload_page(data, offset=0, length=512)
        # Act
        try:
            await blob.upload_page(data, offset=1024, length=513)
        except ValueError as e:
            assert str(e) == 'length must be an integer that aligns with 512 page size'
            return

        # Assert
        raise Exception('Page range validation failed to throw on failure case')

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_resize_blob(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc, 1024)

        # Act
        resp = await blob.resize_blob(512)

        # Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert resp.get('blob_sequence_number') is not None
        props = await blob.get_blob_properties()
        assert isinstance(props, BlobProperties)
        assert props.size == 512

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_set_sequence_number_blob(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = await self._create_blob(bsc)

        # Act
        resp = await blob.set_sequence_number(SequenceNumberAction.Update, 6)

        #Assert
        assert resp.get('etag') is not None
        assert resp.get('last_modified') is not None
        assert resp.get('blob_sequence_number') is not None
        props = await blob.get_blob_properties()
        assert isinstance(props, BlobProperties)
        assert props.page_blob_sequence_number == 6

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_page_blob_with_no_overwrite(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = await blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'blobdata': 'data1'})

        with pytest.raises(ResourceExistsError):
            await blob.upload_blob(
                data2,
                overwrite=False,
                blob_type=BlobType.PageBlob,
                metadata={'blobdata': 'data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data1, bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        assert props.metadata == {'blobdata': 'data1'}
        assert props.size == LARGE_BLOB_SIZE
        assert props.blob_type == BlobType.PageBlob

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_page_blob_with_overwrite(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = await blob.upload_blob(
            data1,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'blobdata': 'data1'})
        update_resp = await blob.upload_blob(
            data2,
            overwrite=True,
            blob_type=BlobType.PageBlob,
            metadata={'blobdata': 'data2'})

        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data2, bsc)
        assert props.etag == update_resp.get('etag')
        assert props.last_modified == update_resp.get('last_modified')
        assert props.metadata == {'blobdata': 'data2'}
        assert props.size == LARGE_BLOB_SIZE + 512
        assert props.blob_type == BlobType.PageBlob

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_bytes(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = await blob.upload_blob(data, blob_type=BlobType.PageBlob)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_0_bytes(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(0)

        # Act
        create_resp = await blob.upload_blob(data, blob_type=BlobType.PageBlob)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_bytes_with_progress_first(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        create_resp = await blob.upload_blob(
            data, blob_type=BlobType.PageBlob, raw_response_hook=callback)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self.assert_upload_progress(LARGE_BLOB_SIZE, self.config.max_page_size, progress)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_bytes_with_index(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 1024

        # Act
        await blob.upload_blob(data[index:], blob_type=BlobType.PageBlob)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[1024:], bsc)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_bytes_with_index_and_count(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        index = 512
        count = 1024

        # Act
        create_resp = await blob.upload_blob(data[index:], length=count, blob_type=BlobType.PageBlob)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[index:index + count], bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_path(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_p.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream, blob_type=BlobType.PageBlob)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_path_with_progress(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path_with_p.temp.{}.dat'.format(str(uuid.uuid4()))
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
            await blob.upload_blob(stream, blob_type=BlobType.PageBlob, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data, bsc)
        self.assert_upload_progress(len(data), self.config.max_page_size, progress)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_stream(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = '_create_blob_from_s.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)
        props = await blob.get_blob_properties()

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_stream_with_empty_pages(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        # data is almost all empty (0s) except two ranges
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = bytearray(LARGE_BLOB_SIZE)
        data[512: 1024] = self.get_random_bytes(512)
        data[8192: 8196] = self.get_random_bytes(4)
        FILE_PATH = '_with_empty_pages.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            create_resp = await blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)
        props = await blob.get_blob_properties()

        # Assert
        # the uploader should have skipped the empty ranges
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        ranges = await blob.get_page_ranges()
        page_ranges, cleared = list(ranges)
        assert len(page_ranges) == 2
        assert page_ranges[0]['start'] == 0
        assert page_ranges[0]['end'] == 4095
        assert page_ranges[1]['start'] == 8192
        assert page_ranges[1]['end'] == 12287
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_stream_non_seekable(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_stream_non_see.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = TestStoragePageBlobAsync.NonSeekableFile(stream)
            await blob.upload_blob(
                non_seekable_file,
                length=blob_size,
                max_concurrency=1,
                blob_type=BlobType.PageBlob)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_stream_with_progress(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'rom_stream_with_progress.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        blob_size = len(data)
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(
                stream, length=blob_size, blob_type=BlobType.PageBlob, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self.assert_upload_progress(len(data), self.config.max_page_size, progress)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_stream_truncated(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = '_create_blob_from_stream_trunc.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(stream, length=blob_size, blob_type=BlobType.PageBlob)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_from_stream_with_progress_truncated(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'from_stream_with_progress_truncated.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        blob_size = len(data) - 512
        with open(FILE_PATH, 'rb') as stream:
            await blob.upload_blob(
                stream, length=blob_size, blob_type=BlobType.PageBlob, raw_response_hook=callback)

        # Assert
        await self.assertBlobEqual(self.container_name, blob.blob_name, data[:blob_size], bsc)
        self.assert_upload_progress(blob_size, self.config.max_page_size, progress)
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_with_md5_small(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(512)

        # Act
        await blob.upload_blob(data, validate_content=True, blob_type=BlobType.PageBlob)

        # Assert

    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_create_blob_with_md5_large(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        blob = self._get_blob_reference(bsc)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        await blob.upload_blob(data, validate_content=True, blob_type=BlobType.PageBlob)

        # Assert

    @pytest.mark.skip(reason="Failing live test https://github.com/Azure/azure-sdk-for-python/issues/10473")
    @pytest.mark.live_test_only
    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    @recorded_by_proxy_async
    async def test_incremental_copy_blob(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        source_blob = await self._create_blob(bsc, 2048)
        data = self.get_random_bytes(512)
        resp1 = await source_blob.upload_page(data, offset=0, length=512)
        resp2 = await source_blob.upload_page(data, offset=1024, length=512)
        source_snapshot_blob = await source_blob.create_snapshot()

        snapshot_blob = BlobClient.from_blob_url(
            source_blob.url, credential=source_blob.credential, snapshot=source_snapshot_blob)
        sas_token = generate_blob_sas(
            snapshot_blob.account_name,
            snapshot_blob.container_name,
            snapshot_blob.blob_name,
            snapshot=snapshot_blob.snapshot,
            account_key=snapshot_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(snapshot_blob.url, credential=sas_token)


        # Act
        dest_blob = bsc.get_blob_client(self.container_name, 'dest_blob')
        copy = await dest_blob.start_copy_from_url(sas_blob.url, incremental_copy=True)

        # Assert
        assert copy is not None
        assert copy['copy_id'] is not None
        assert copy['copy_status'] == 'pending'

        copy_blob = await self._wait_for_async_copy(dest_blob)
        assert copy_blob.copy.status == 'success'
        assert copy_blob.copy.destination_snapshot is not None

        # strip off protocol
        assert copy_blob.copy.source.endswith(sas_blob.url[5:])

    @pytest.mark.live_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_tier_on_create(self, premium_storage_account_name, premium_storage_account_key):
        # Test can only run live

        bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        url = self.account_url(premium_storage_account_name, "blob")
        credential = premium_storage_account_key
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if self.is_live:
                await container.create_container()

            # test create_blob API
            blob = self._get_blob_reference(bsc)
            pblob = pbs.get_blob_client(container_name, blob.blob_name)
            await pblob.create_page_blob(1024, premium_page_blob_tier=PremiumPageBlobTier.P4)

            props = await pblob.get_blob_properties()
            assert props.blob_tier == PremiumPageBlobTier.P4
            assert not props.blob_tier_inferred

            # test create_blob_from_bytes API
            blob2 = self._get_blob_reference(bsc)
            pblob2 = pbs.get_blob_client(container_name, blob2.blob_name)
            byte_data = self.get_random_bytes(1024)
            await pblob2.upload_blob(
                byte_data,
                premium_page_blob_tier=PremiumPageBlobTier.P6,
                blob_type=BlobType.PageBlob,
                overwrite=True)

            props2 = await pblob2.get_blob_properties()
            assert props2.blob_tier == PremiumPageBlobTier.P6
            assert not props2.blob_tier_inferred

            # test create_blob_from_path API
            blob3 = self._get_blob_reference(bsc)
            pblob3 = pbs.get_blob_client(container_name, blob3.blob_name)
            FILE_PATH = 'test_blob_tier_on_creat.temp.{}.dat'.format(str(uuid.uuid4()))
            with open(FILE_PATH, 'wb') as stream:
                stream.write(byte_data)
            with open(FILE_PATH, 'rb') as stream:
                await pblob3.upload_blob(
                    stream,
                    blob_type=BlobType.PageBlob,
                    premium_page_blob_tier=PremiumPageBlobTier.P10,
                    overwrite=True)

            props3 = await pblob3.get_blob_properties()
            assert props3.blob_tier == PremiumPageBlobTier.P10
            assert not props3.blob_tier_inferred

        finally:
            await container.delete_container()
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_tier_set_tier_api(self, premium_storage_account_name, premium_storage_account_key):
        bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        url = self.account_url(premium_storage_account_name, "blob")
        credential = premium_storage_account_key
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if self.is_live:
                try:
                    await container.create_container()
                except ResourceExistsError:
                    pass

            blob = self._get_blob_reference(bsc)
            pblob = pbs.get_blob_client(container_name, blob.blob_name)
            await pblob.create_page_blob(1024)
            blob_ref = await pblob.get_blob_properties()
            assert PremiumPageBlobTier.P10 == blob_ref.blob_tier
            assert blob_ref.blob_tier is not None
            assert blob_ref.blob_tier_inferred

            pcontainer = pbs.get_container_client(container_name)
            blobs = []
            async for b in pcontainer.list_blobs():
                blobs.append(b)

            # Assert
            assert blobs is not None
            assert len(blobs) >= 1
            assert blobs[0] is not None
            self.assertNamedItemInContainer(blobs, blob.blob_name)

            await pblob.set_premium_page_blob_tier(PremiumPageBlobTier.P50)

            blob_ref2 = await pblob.get_blob_properties()
            assert PremiumPageBlobTier.P50 == blob_ref2.blob_tier
            assert not blob_ref2.blob_tier_inferred

            blobs = []
            async for b in pcontainer.list_blobs():
                blobs.append(b)

            # Assert
            assert blobs is not None
            assert len(blobs) >= 1
            assert blobs[0] is not None
            self.assertNamedItemInContainer(blobs, blob.blob_name)
            assert blobs[0].blob_tier == PremiumPageBlobTier.P50
            assert not blobs[0].blob_tier_inferred
        finally:
            await container.delete_container()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_tier_copy_blob(self, premium_storage_account_name, premium_storage_account_key):
        bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        url = self.account_url(premium_storage_account_name, "blob")
        credential = premium_storage_account_key
        pbs = BlobServiceClient(url, credential=credential)

        try:
            container_name = self.get_resource_name('utpremiumcontainer')
            container = pbs.get_container_client(container_name)

            if self.is_live:
                try:
                    await container.create_container()
                except ResourceExistsError:
                    pass

            bsc = BlobServiceClient(self.account_url(premium_storage_account_name, "blob"), credential=premium_storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
            source_blob = pbs.get_blob_client(
                container_name,
                self.get_resource_name(TEST_BLOB_PREFIX))
            await source_blob.create_page_blob(1024, premium_page_blob_tier=PremiumPageBlobTier.P10)

            # Act
            source_blob_url = '{0}/{1}/{2}'.format(
                self.account_url(premium_storage_account_name, "blob"), container_name, source_blob.blob_name)

            copy_blob = pbs.get_blob_client(container_name, 'blob1copy')
            copy = await copy_blob.start_copy_from_url(source_blob_url, premium_page_blob_tier=PremiumPageBlobTier.P30)

            # Assert
            assert copy is not None
            assert copy['copy_status'] == 'success'
            assert copy['copy_id'] is not None

            copy_ref = await copy_blob.get_blob_properties()
            assert copy_ref.blob_tier == PremiumPageBlobTier.P30

            source_blob2 = pbs.get_blob_client(
               container_name,
               self.get_resource_name(TEST_BLOB_PREFIX))

            await source_blob2.create_page_blob(1024)
            source_blob2_url = '{0}/{1}/{2}'.format(
                self.account_url(premium_storage_account_name, "blob"), source_blob2.container_name, source_blob2.blob_name)

            copy_blob2 = pbs.get_blob_client(container_name, 'blob2copy')
            copy2 = await copy_blob2.start_copy_from_url(source_blob2_url, premium_page_blob_tier=PremiumPageBlobTier.P60)
            assert copy2 is not None
            assert copy2['copy_status'] == 'success'
            assert copy2['copy_id'] is not None

            copy_ref2 = await copy_blob2.get_blob_properties()
            assert copy_ref2.blob_tier == PremiumPageBlobTier.P60
            assert not copy_ref2.blob_tier_inferred

            copy_blob3 = pbs.get_blob_client(container_name, 'blob3copy')
            copy3 = await copy_blob3.start_copy_from_url(source_blob2_url)
            assert copy3 is not None
            assert copy3['copy_status'] == 'success'
            assert copy3['copy_id'] is not None

            copy_ref3 = await copy_blob3.get_blob_properties()
            assert copy_ref3.blob_tier == PremiumPageBlobTier.P10
            assert copy_ref3.blob_tier_inferred
        finally:
            await container.delete_container()

    @BlobPreparer()
    @AsyncStorageRecordedTestCase.await_prepared_test
    async def _test_download_sparse_page_blob(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, connection_data_block_size=4 * 1024, max_page_size=4 * 1024)
        await self._setup(bsc)
        self.config.max_single_get_size = 4*1024
        self.config.max_chunk_get_size = 1024

        sparse_page_blob_size = 1024 * 1024
        data = self.get_random_bytes(2048)
        blob_client = await self._create_sparse_page_blob(size=sparse_page_blob_size, data=data)

        # Act
        page_ranges, cleared = await blob_client.get_page_ranges()
        start = page_ranges[0]['start']
        end = page_ranges[0]['end']

        content = await blob_client.download_blob()
        content = await content.readall()

        # Assert
        assert sparse_page_blob_size == len(content)
        # make sure downloaded data is the same as the uploaded data
        assert data == content[start: end + 1]
        # assert all unlisted ranges are empty
        for byte in content[:start-1]:
            try:
                assert byte == '\x00'
            except:
                assert byte == 0
        for byte in content[end+1:]:
            try:
                assert byte == '\x00'
            except:
                assert byte == 0

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_progress_chunked_non_parallel(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        await self._setup(bsc)

        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_page_size=1024)

        await blob_client.upload_blob(
            data,
            blob_type=BlobType.PageBlob,
            overwrite=True,
            max_concurrency=1,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_progress_chunked_parallel(self, **kwargs):
        # Arrange
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), storage_account_key)
        await self._setup(bsc)

        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_page_size=1024)

        await blob_client.upload_blob(
            data,
            blob_type=BlobType.PageBlob,
            overwrite=True,
            max_concurrency=3,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

#------------------------------------------------------------------------------
