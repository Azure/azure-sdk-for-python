# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

pytestmark = pytest.mark.xfail
from datetime import datetime, timedelta
from azure.common import AzureHttpError
from azure.storage.blob import (
    #BlobBlock,  # TODO
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    #BlobPermissions,
)
#from azure.storage.common._common_conversion import _get_content_md5
from tests.testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
SOURCE_BLOB_SIZE = 8 * 1024


# ------------------------------------------------------------------------------

class StorageBlockBlobTest(StorageTestCase):

    def setUp(self):
        super(StorageBlockBlobTest, self).setUp()

        self.bs = self._create_storage_service(BlockBlobService, self.settings)
        self.container_name = self.get_resource_name('utcontainer')

        # create source blob to be copied from
        self.source_blob_name = self.get_resource_name('srcblob')
        self.source_blob_data = self.get_random_bytes(SOURCE_BLOB_SIZE)

        if not self.is_playback():
            self.bs.create_container(self.container_name)
            self.bs.create_blob_from_bytes(self.container_name, self.source_blob_name, self.source_blob_data)

        # generate a SAS so that it is accessible with a URL
        sas_token = self.bs.generate_blob_shared_access_signature(
            self.container_name,
            self.source_blob_name,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        self.source_blob_url = self.bs.make_blob_url(self.container_name, self.source_blob_name, sas_token=sas_token)

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bs.delete_container(self.container_name)
            except AzureHttpError:
                pass

        return super(StorageBlockBlobTest, self).tearDown()

    @record
    def test_put_block_from_url_and_commit(self):
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')

        # Act part 1: make put block from url calls
        self.bs.put_block_from_url(self.container_name, dest_blob_name, self.source_blob_url,
                                   source_range_start=0, source_range_end=4 * 1024 - 1, block_id=1)
        self.bs.put_block_from_url(self.container_name, dest_blob_name, self.source_blob_url,
                                   source_range_start=4 * 1024, source_range_end=8 * 1024, block_id=2)

        # Assert blocks
        block_list = self.bs.get_block_list(self.container_name, dest_blob_name, None, 'all')
        self.assertEqual(len(block_list.uncommitted_blocks), 2)
        self.assertEqual(len(block_list.committed_blocks), 0)

        # Act part 2: commit the blocks
        block_list = [BlobBlock(id='1'), BlobBlock(id='2')]
        self.bs.put_block_list(self.container_name, dest_blob_name, block_list)

        # Assert destination blob has right content
        blob = self.bs.get_blob_to_bytes(self.container_name, dest_blob_name)
        self.assertEqual(blob.content, self.source_blob_data)

    @record
    def test_put_block_from_url_and_validate_content_md5(self):
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')
        src_md5 = _get_content_md5(self.source_blob_data)

        # Act part 1: put block from url with md5 validation
        self.bs.put_block_from_url(self.container_name, dest_blob_name, self.source_blob_url,
                                   source_range_start=0, source_range_end=8 * 1024, block_id=1, source_content_md5=src_md5)

        # Assert block was staged
        block_list = self.bs.get_block_list(self.container_name, dest_blob_name, None, 'all')
        self.assertEqual(len(block_list.uncommitted_blocks), 1)
        self.assertEqual(len(block_list.committed_blocks), 0)

        # Act part 2: put block from url with wrong md5
        with self.assertRaises(AzureHttpError):
            self.bs.put_block_from_url(self.container_name, dest_blob_name, self.source_blob_url,
                                       source_range_start=0, source_range_end=8 * 1024, block_id=2,
                                       source_content_md5=_get_content_md5(b"POTATO"))

        # Assert block was not staged
        block_list = self.bs.get_block_list(self.container_name, dest_blob_name, None, 'all')
        self.assertEqual(len(block_list.uncommitted_blocks), 1)
        self.assertEqual(len(block_list.committed_blocks), 0)

    @record
    def test_copy_blob_sync(self):
        # Arrange
        dest_blob_name = self.get_resource_name('destblob')

        # Act
        copy_props = self.bs.copy_blob(self.container_name, dest_blob_name, self.source_blob_url, requires_sync=True)

        # Assert
        self.assertIsNotNone(copy_props)
        self.assertIsNotNone(copy_props.id)
        self.assertEqual('success', copy_props.status)

        # Verify content
        dest_blob = self.bs.get_blob_to_bytes(self.container_name, dest_blob_name)
        self.assertEqual(self.source_blob_data, dest_blob.content)
