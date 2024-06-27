# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import (
    BlobClient,
    BlobSasPermissions,
    BlobServiceClient,
    generate_blob_sas,
    StandardBlobTier,
    StorageErrorCode
)
from azure.storage.blob._shared.policies import StorageContentValidation

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
SOURCE_BLOB_SIZE = 8 * 1024


# ------------------------------------------------------------------------------

class TestStorageBlockBlob(StorageRecordedTestCase):

    def _setup(self, storage_account_name, key, container_prefix='utcontainer'):
        account_url = self.account_url(storage_account_name, "blob")
        if not isinstance(account_url, str):
            account_url = account_url.encode('utf-8')
            key = key.encode('utf-8')
        self.bsc = BlobServiceClient(
            account_url,
            credential=key,
            connection_data_block_size=4 * 1024,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name(container_prefix)

        # create source blob to be copied from
        self.source_blob_name = self.get_resource_name('srcblob')
        self.source_blob_name_with_special_chars = 'भारत¥test/testsubÐirÍ/'+self.get_resource_name('srcÆblob')
        self.source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)
        self.source_blob_with_special_chars_data = self.get_random_bytes(SOURCE_BLOB_SIZE)

        blob = self.bsc.get_blob_client(self.container_name, self.source_blob_name)
        blob_with_special_chars = self.bsc.get_blob_client(self.container_name, self.source_blob_name_with_special_chars)

        if self.is_live:
            self.bsc.create_container(self.container_name)
            blob.upload_blob(self.source_blob_data)
            blob_with_special_chars.upload_blob(self.source_blob_with_special_chars_data)

        # generate a SAS so that it is accessible with a URL
        sas_token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        # generate a SAS so that it is accessible with a URL
        sas_token_for_special_chars = self.generate_sas(
            generate_blob_sas,
            blob_with_special_chars.account_name,
            blob_with_special_chars.container_name,
            blob_with_special_chars.blob_name,
            snapshot=blob_with_special_chars.snapshot,
            account_key=blob_with_special_chars.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        self.source_blob_url_without_sas = blob.url
        self.source_blob_url = BlobClient.from_blob_url(blob.url, credential=sas_token).url
        self.source_blob_url_with_special_chars = BlobClient.from_blob_url(
            blob_with_special_chars.url, credential=sas_token_for_special_chars).url

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_from_url_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key, container_prefix="container1")
        split = 4 * 1024
        destination_blob_name = self.get_resource_name('destblob')
        destination_blob_client = self.bsc.get_blob_client(self.container_name, destination_blob_name)
        token = "Bearer {}".format(self.get_credential(BlobServiceClient).get_token("https://storage.azure.com/.default").token)

        # Assert this operation fails without a credential
        with pytest.raises(HttpResponseError):
            destination_blob_client.stage_block_from_url(
                block_id=1,
                source_url=self.source_blob_url_without_sas,
                source_offset=0,
                source_length=split)
        # Assert it passes after passing an oauth credential
        destination_blob_client.stage_block_from_url(
                block_id=1,
                source_url=self.source_blob_url_without_sas,
                source_offset=0,
                source_length=split,
                source_authorization=token)
        destination_blob_client.stage_block_from_url(
            block_id=2,
            source_url=self.source_blob_url_without_sas,
            source_offset=split,
            source_length=split,
            source_authorization=token)

        committed, uncommitted = destination_blob_client.get_block_list('all')
        assert len(uncommitted) == 2
        assert len(committed) == 0

        # Act part 2: commit the blocks
        destination_blob_client.commit_block_list(['1', '2'])

        # Assert destination blob has right content
        destination_blob_data = destination_blob_client.download_blob().readall()
        assert len(destination_blob_data) == (8 * 1024)
        assert destination_blob_data == self.source_blob_data
        assert self.source_blob_data == destination_blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_from_url_and_commit(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # Act part 1: make put block from url calls
        split = 4 * 1024
        dest_blob.stage_block_from_url(
            block_id=1,
            source_url=self.source_blob_url,
            source_offset=0,
            source_length=split)
        dest_blob.stage_block_from_url(
            block_id=2,
            source_url=self.source_blob_url,
            source_offset=split,
            source_length=split)

        # Assert blocks
        committed, uncommitted = dest_blob.get_block_list('all')
        assert len(uncommitted) == 2
        assert len(committed) == 0

        # Act part 2: commit the blocks
        dest_blob.commit_block_list(['1', '2'])

        # Assert destination blob has right content
        content = dest_blob.download_blob().readall()
        assert len(content) == (8 * 1024)
        assert content == self.source_blob_data

        dest_blob.stage_block_from_url(
            block_id=3,
            source_url=self.source_blob_url_with_special_chars,
            source_offset=0,
            source_length=split)
        dest_blob.stage_block_from_url(
            block_id=4,
            source_url=self.source_blob_url_with_special_chars,
            source_offset=split,
            source_length=split)

        # Assert blocks
        committed, uncommitted = dest_blob.get_block_list('all')
        assert len(uncommitted) == 2
        assert len(committed) == 2

        # Act part 2: commit the blocks
        dest_blob.commit_block_list(['3', '4'])

        # Assert destination blob has right content
        content = dest_blob.download_blob().readall()
        assert len(content) == (8 * 1024)
        assert content == self.source_blob_with_special_chars_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_from_url_and_validate_content_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)
        src_md5 = StorageContentValidation.get_content_md5(self.source_blob_data)

        # Act part 1: put block from url with md5 validation
        dest_blob.stage_block_from_url(
            block_id=1,
            source_url=self.source_blob_url,
            source_content_md5=src_md5,
            source_offset=0,
            source_length=8 * 1024)

        # Assert block was staged
        committed, uncommitted = dest_blob.get_block_list('all')
        assert len(uncommitted) == 1
        assert len(committed) == 0

        # Act part 2: put block from url with wrong md5
        fake_md5 = StorageContentValidation.get_content_md5(b"POTATO")
        with pytest.raises(HttpResponseError) as error:
            dest_blob.stage_block_from_url(
                block_id=2,
                source_url=self.source_blob_url,
                source_content_md5=fake_md5,
                source_offset=0,
                source_length=8 * 1024)
        assert error.value.error_code == StorageErrorCode.md5_mismatch

        # Assert block was not staged
        committed, uncommitted = dest_blob.get_block_list('all')
        assert len(uncommitted) == 1
        assert len(committed) == 0

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_sync(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # Act
        copy_props = dest_blob.start_copy_from_url(self.source_blob_url, requires_sync=True)

        # Assert
        assert copy_props is not None
        assert (copy_props['copy_id']) is not None
        assert 'success' == copy_props['copy_status']

        # Verify content
        content = dest_blob.download_blob().readall()
        assert self.source_blob_data == content

        copy_props_with_special_chars = dest_blob.start_copy_from_url(self.source_blob_url_with_special_chars, requires_sync=True)

        # Assert
        assert copy_props_with_special_chars is not None
        assert copy_props_with_special_chars['copy_id'] is not None
        assert 'success' == copy_props_with_special_chars['copy_status']

        # Verify content
        content = dest_blob.download_blob().readall()
        assert self.source_blob_with_special_chars_data == content

    @BlobPreparer()
    @recorded_by_proxy
    def test_copy_blob_with_cold_tier_sync(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)
        blob_tier = StandardBlobTier.Cold

        # Act
        dest_blob.start_copy_from_url(self.source_blob_url, standard_blob_tier=blob_tier, requires_sync=True)
        copy_blob_properties = dest_blob.get_blob_properties()

        # Assert
        assert copy_blob_properties.blob_tier == blob_tier

    @BlobPreparer()
    @recorded_by_proxy
    def test_sync_copy_blob_returns_vid(self, **kwargs):
        storage_account_name = kwargs.pop("versioned_storage_account_name")
        storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # Act
        copy_props = dest_blob.start_copy_from_url(self.source_blob_url, requires_sync=True)

        # Assert
        assert copy_props['version_id'] is not None
        assert copy_props is not None
        assert copy_props['copy_id'] is not None
        assert 'success' == copy_props['copy_status']

        # Verify content
        content = dest_blob.download_blob().readall()
        assert self.source_blob_data == content
