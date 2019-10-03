# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from datetime import datetime, timedelta
from azure.core import HttpResponseError
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    StorageErrorCode,
    BlobPermissions
)
from azure.storage.blob._shared.policies import StorageContentValidation
from testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
SOURCE_BLOB_SIZE = 8 * 1024


# ------------------------------------------------------------------------------

class StorageBlockBlobTest(StorageTestCase):

    def setUp(self):
        super(StorageBlockBlobTest, self).setUp()
        url = self._get_account_url()
        credential = self._get_shared_key_credential()

        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bsc = BlobServiceClient(
            url,
            credential=credential,
            connection_data_block_size=4 * 1024,
            max_single_put_size=32 * 1024,
            max_block_size=4 * 1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name('utcontainer')

        # create source blob to be copied from
        self.source_blob_name = self.get_resource_name('srcblob')
        self.source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)

        blob = self.bsc.get_blob_client(self.container_name, self.source_blob_name)
        if not self.is_playback():
            self.bsc.create_container(self.container_name)
            blob.upload_blob(self.source_blob_data)

        # generate a SAS so that it is accessible with a URL
        sas_token = blob.generate_shared_access_signature(
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        self.source_blob_url = BlobClient(blob.url, credential=sas_token).url

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bsc.delete_container(self.container_name)
            except HttpResponseError:
                pass

        return super(StorageBlockBlobTest, self).tearDown()

    @record
    def test_put_block_from_url_and_commit(self):
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # Act part 1: make put block from url calls
        split = 4 * 1024
        dest_blob.stage_block_from_url(
            block_id=1,
            source_url=self.source_blob_url,
            source_offset=0,
            source_length=split - 1)
        dest_blob.stage_block_from_url(
            block_id=2,
            source_url=self.source_blob_url,
            source_offset=split,
            source_length=split)

        # Assert blocks
        committed, uncommitted = dest_blob.get_block_list('all')
        self.assertEqual(len(uncommitted), 2)
        self.assertEqual(len(committed), 0)

        # Act part 2: commit the blocks
        dest_blob.commit_block_list(['1', '2'])

        # Assert destination blob has right content
        content = dest_blob.download_blob().content_as_bytes()
        self.assertEqual(content, self.source_blob_data)

    @record
    def test_put_block_from_url_and_validate_content_md5(self):
        # Arrange
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
        self.assertEqual(len(uncommitted), 1)
        self.assertEqual(len(committed), 0)

        # Act part 2: put block from url with wrong md5
        fake_md5 = StorageContentValidation.get_content_md5(b"POTATO")
        with self.assertRaises(HttpResponseError) as error:
            dest_blob.stage_block_from_url(
                block_id=2,
                source_url=self.source_blob_url,
                source_content_md5=fake_md5,
                source_offset=0,
                source_length=8 * 1024)
        self.assertEqual(error.exception.error_code, StorageErrorCode.md5_mismatch)

        # Assert block was not staged
        committed, uncommitted = dest_blob.get_block_list('all')
        self.assertEqual(len(uncommitted), 1)
        self.assertEqual(len(committed), 0)

    @record
    def test_copy_blob_sync(self):
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')
        dest_blob = self.bsc.get_blob_client(self.container_name, dest_blob_name)

        # Act
        copy_props = dest_blob.start_copy_from_url(self.source_blob_url, requires_sync=True)

        # Assert
        self.assertIsNotNone(copy_props)
        self.assertIsNotNone(copy_props['copy_id'])
        self.assertEqual('success', copy_props['copy_status'])

        # Verify content
        content = dest_blob.download_blob().content_as_bytes()
        self.assertEqual(self.source_blob_data, content)
