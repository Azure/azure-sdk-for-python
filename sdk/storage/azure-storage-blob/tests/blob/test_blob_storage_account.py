# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

import unittest

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
from azure.storage.blob.common import StandardBlobTier
from tests.testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
# ------------------------------------------------------------------------------


class BlobStorageAccountTest(StorageTestCase):
    def setUp(self):
        super(BlobStorageAccountTest, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()
        self.bsc = BlobServiceClient(url, credential=credential)
        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bsc.create_container(self.container_name)

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bsc.delete_container(self.container_name)
            except:
                pass

        return super(BlobStorageAccountTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        return self.bsc.get_blob_client(self.container_name, blob_name)

    def _create_blob(self):
        blob = self._get_blob_reference()
        blob.upload_blob(b'')
        return blob

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob().content_as_bytes()
        self.assertEqual(actual_data, expected_data)

    # --Tests specific to Blob Storage Accounts (not general purpose)------------

    @record
    def test_standard_blob_tier_set_tier_api(self):
        container = self.bsc.get_container_client(self.container_name)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]
        
        for tier in tiers:
            blob = self._get_blob_reference()
            data = b'hello world'
            blob.upload_blob(data)

            blob_ref = blob.get_blob_properties()
            self.assertIsNotNone(blob_ref.blob_tier)
            self.assertTrue(blob_ref.blob_tier_inferred)
            self.assertIsNone(blob_ref.blob_tier_change_time)

            blobs = list(container.list_blobs())

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob.blob_name)
            self.assertIsNotNone(blobs[0].blob_tier)
            self.assertTrue(blobs[0].blob_tier_inferred)
            self.assertIsNone(blobs[0].blob_tier_change_time)

            blob.set_standard_blob_tier(tier)

            blob_ref2 = blob.get_blob_properties()
            self.assertEqual(tier, blob_ref2.blob_tier)
            self.assertFalse(blob_ref2.blob_tier_inferred)
            self.assertIsNotNone(blob_ref2.blob_tier_change_time)

            blobs = list(container.list_blobs())

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob.blob_name)
            self.assertEqual(blobs[0].blob_tier, tier)
            self.assertFalse(blobs[0].blob_tier_inferred)
            self.assertIsNotNone(blobs[0].blob_tier_change_time)

            blob.delete_blob()

    @record
    def test_rehydration_status(self):
        blob_name = 'rehydration_test_blob_1'
        blob_name2 = 'rehydration_test_blob_2'
        container = self.bsc.get_container_client(self.container_name)

        data = b'hello world'
        blob = container.upload_blob(blob_name, data)
        blob.set_standard_blob_tier(StandardBlobTier.Archive)
        blob.set_standard_blob_tier(StandardBlobTier.Cool)

        blob_ref = blob.get_blob_properties()
        self.assertEqual(StandardBlobTier.Archive, blob_ref.blob_tier)
        self.assertEqual("rehydrate-pending-to-cool", blob_ref.archive_status)
        self.assertFalse(blob_ref.blob_tier_inferred)

        blobs = list(container.list_blobs())
        blob.delete_blob()

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 1)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, blob.blob_name)
        self.assertEqual(StandardBlobTier.Archive, blobs[0].blob_tier)
        self.assertEqual("rehydrate-pending-to-cool", blobs[0].archive_status)
        self.assertFalse(blobs[0].blob_tier_inferred)

        blob2 = container.upload_blob(blob_name2, data)
        blob2.set_standard_blob_tier(StandardBlobTier.Archive)
        blob2.set_standard_blob_tier(StandardBlobTier.Hot)

        blob_ref2 = blob2.get_blob_properties()
        self.assertEqual(StandardBlobTier.Archive, blob_ref2.blob_tier)
        self.assertEqual("rehydrate-pending-to-hot", blob_ref2.archive_status)
        self.assertFalse(blob_ref2.blob_tier_inferred)

        blobs = list(container.list_blobs())

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 1)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, blob2.blob_name)
        self.assertEqual(StandardBlobTier.Archive, blobs[0].blob_tier)
        self.assertEqual("rehydrate-pending-to-hot", blobs[0].archive_status)
        self.assertFalse(blobs[0].blob_tier_inferred)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
