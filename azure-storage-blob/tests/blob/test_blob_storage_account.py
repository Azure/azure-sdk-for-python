# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

pytestmark = pytest.mark.xfail
import unittest

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
#from azure.storage.blob.models import StandardBlobTier
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

        self.bs = self._create_storage_service_for_blob_storage_account(BlockBlobService, self.settings)

        self.container_name = self.get_resource_name('utcontainer')

        if not self.is_playback():
            self.bs.create_container(self.container_name)

    def tearDown(self):
        if not self.is_playback():
            try:
                self.bs.delete_container(self.container_name)
            except:
                pass

        return super(BlobStorageAccountTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_blob(self):
        blob_name = self._get_blob_reference()
        self.bs.create_blob_from_bytes(self.container_name, blob_name, b'')
        return blob_name

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        actual_data = self.bs.get_blob_to_bytes(container_name, blob_name)
        self.assertEqual(actual_data.content, expected_data)

    # --Tests specific to Blob Storage Accounts (not general purpose)------------

    @record
    def test_standard_blob_tier_set_tier_api(self):
        self.bs.create_container(self.container_name)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]
        
        for tier in tiers:
            blob_name = self._get_blob_reference()
            data = b'hello world'
            self.bs.create_blob_from_bytes(self.container_name, blob_name, data)

            blob_ref = self.bs.get_blob_properties(self.container_name, blob_name)
            self.assertIsNotNone(blob_ref.properties.blob_tier)
            self.assertTrue(blob_ref.properties.blob_tier_inferred)
            self.assertIsNone(blob_ref.properties.blob_tier_change_time)

            blobs = list(self.bs.list_blobs(self.container_name))

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob_name)
            self.assertIsNotNone(blobs[0].properties.blob_tier)
            self.assertTrue(blobs[0].properties.blob_tier_inferred)
            self.assertIsNone(blobs[0].properties.blob_tier_change_time)

            self.bs.set_standard_blob_tier(self.container_name, blob_name, tier)

            blob_ref2 = self.bs.get_blob_properties(self.container_name, blob_name)
            self.assertEqual(tier, blob_ref2.properties.blob_tier)
            self.assertFalse(blob_ref2.properties.blob_tier_inferred)
            self.assertIsNotNone(blob_ref2.properties.blob_tier_change_time)

            blobs = list(self.bs.list_blobs(self.container_name))

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob_name)
            self.assertEqual(blobs[0].properties.blob_tier, tier)
            self.assertFalse(blobs[0].properties.blob_tier_inferred)
            self.assertIsNotNone(blobs[0].properties.blob_tier_change_time)

            self.bs.delete_blob(self.container_name, blob_name)

    @record
    def test_rehydration_status(self):
        blob_name = 'rehydration_test_blob_1'
        blob_name2 = 'rehydration_test_blob_2'

        data = b'hello world'
        self.bs.create_blob_from_bytes(self.container_name, blob_name, data)
        self.bs.set_standard_blob_tier(self.container_name, blob_name, StandardBlobTier.Archive)
        self.bs.set_standard_blob_tier(self.container_name, blob_name, StandardBlobTier.Cool)

        blob_ref = self.bs.get_blob_properties(self.container_name, blob_name)
        self.assertEqual(StandardBlobTier.Archive, blob_ref.properties.blob_tier)
        self.assertEqual("rehydrate-pending-to-cool", blob_ref.properties.rehydration_status)
        self.assertFalse(blob_ref.properties.blob_tier_inferred)

        blobs = list(self.bs.list_blobs(self.container_name))
        self.bs.delete_blob(self.container_name, blob_name)

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 1)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, blob_name)
        self.assertEqual(StandardBlobTier.Archive, blobs[0].properties.blob_tier)
        self.assertEqual("rehydrate-pending-to-cool", blobs[0].properties.rehydration_status)
        self.assertFalse(blobs[0].properties.blob_tier_inferred)

        self.bs.create_blob_from_bytes(self.container_name, blob_name2, data)
        self.bs.set_standard_blob_tier(self.container_name, blob_name2, StandardBlobTier.Archive)
        self.bs.set_standard_blob_tier(self.container_name, blob_name2, StandardBlobTier.Hot)

        blob_ref2 = self.bs.get_blob_properties(self.container_name, blob_name2)
        self.assertEqual(StandardBlobTier.Archive, blob_ref2.properties.blob_tier)
        self.assertEqual("rehydrate-pending-to-hot", blob_ref2.properties.rehydration_status)
        self.assertFalse(blob_ref2.properties.blob_tier_inferred)

        blobs = list(self.bs.list_blobs(self.container_name))

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 1)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, blob_name2)
        self.assertEqual(StandardBlobTier.Archive, blobs[0].properties.blob_tier)
        self.assertEqual("rehydrate-pending-to-hot", blobs[0].properties.rehydration_status)
        self.assertFalse(blobs[0].properties.blob_tier_inferred)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
