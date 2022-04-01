# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient
)
from azure.storage.blob import (
    StandardBlobTier
)
from azure.storage.blob._generated.models import RehydratePriority
from settings.testcase import BlobPreparer
from devtools_testutils.storage.aio import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
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


class BlobStorageAccountTestAsync(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------
    async def _setup(self, bsc):
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                await bsc.create_container(self.container_name)
            except:
                pass

    def _get_blob_reference(self, bsc):
        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        return bsc.get_blob_client(self.container_name, blob_name)

    async def _create_blob(self, bsc):
        blob = self._get_blob_reference(bsc)
        await blob.upload_blob(b'')
        return blob

    async def assertBlobEqual(self, container_name, blob_name, expected_data, bsc):
        blob = bsc.get_blob_client(container_name, blob_name)
        actual_data = await blob.download_blob().readall()
        self.assertEqual(actual_data, expected_data)
    # --------------------------------------------------------------------------

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_standard_blob_tier_set_tier_api(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())

        await self._setup(bsc)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            blob_name = self.get_resource_name(tier.value)
            blob = bsc.get_blob_client(self.container_name, blob_name)
            await blob.upload_blob(b'hello world')

            blob_ref = await blob.get_blob_properties()
            self.assertIsNotNone(blob_ref.blob_tier)
            self.assertTrue(blob_ref.blob_tier_inferred)
            self.assertIsNone(blob_ref.blob_tier_change_time)

            # Act
            await blob.set_standard_blob_tier(tier)

            # Assert
            blob_ref2 = await blob.get_blob_properties()
            self.assertEqual(tier, blob_ref2.blob_tier)
            self.assertFalse(blob_ref2.blob_tier_inferred)
            self.assertIsNotNone(blob_ref2.blob_tier_change_time)

            await blob.delete_blob()

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_std_blob_tier_w_rehydrate_priority(self, storage_account_name, storage_account_key):
        # Arrange
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        await self._setup(bsc)
        blob_client = await self._create_blob(bsc)
        blob_tier = StandardBlobTier.Archive
        rehydrate_tier = StandardBlobTier.Cool
        rehydrate_priority = RehydratePriority.standard

        # Act
        await blob_client.set_standard_blob_tier(blob_tier,
                                                 rehydrate_priority=rehydrate_priority)
        await blob_client.set_standard_blob_tier(rehydrate_tier)
        blob_props = await blob_client.get_blob_properties()

        # Assert
        self.assertEqual('rehydrate-pending-to-cool', blob_props.archive_status)

    @BlobPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rehydration_status(self, storage_account_name, storage_account_key):
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, transport=AiohttpTestTransport())
        await self._setup(bsc)
        blob_name = 'rehydration_test_blob_1'
        blob_name2 = 'rehydration_test_blob_2'
        container = bsc.get_container_client(self.container_name)

        data = b'hello world'
        blob = await container.upload_blob(blob_name, data)
        await blob.set_standard_blob_tier(StandardBlobTier.Archive)
        await blob.set_standard_blob_tier(StandardBlobTier.Cool)

        blob_ref = await blob.get_blob_properties()
        self.assertEqual(StandardBlobTier.Archive, blob_ref.blob_tier)
        self.assertEqual("rehydrate-pending-to-cool", blob_ref.archive_status)
        self.assertFalse(blob_ref.blob_tier_inferred)

        blobs = []
        async for b in container.list_blobs():
            blobs.append(b)

        await blob.delete_blob()

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 1)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, blob.blob_name)
        self.assertEqual(StandardBlobTier.Archive, blobs[0].blob_tier)
        self.assertEqual("rehydrate-pending-to-cool", blobs[0].archive_status)
        self.assertFalse(blobs[0].blob_tier_inferred)

        blob2 = await container.upload_blob(blob_name2, data)
        await blob2.set_standard_blob_tier(StandardBlobTier.Archive)
        await blob2.set_standard_blob_tier(StandardBlobTier.Hot)

        blob_ref2 = await blob2.get_blob_properties()
        self.assertEqual(StandardBlobTier.Archive, blob_ref2.blob_tier)
        self.assertEqual("rehydrate-pending-to-hot", blob_ref2.archive_status)
        self.assertFalse(blob_ref2.blob_tier_inferred)

        blobs = []
        async for b in container.list_blobs():
            blobs.append(b)

        # Assert
        self.assertIsNotNone(blobs)
        self.assertGreaterEqual(len(blobs), 1)
        self.assertIsNotNone(blobs[0])
        self.assertNamedItemInContainer(blobs, blob2.blob_name)
        self.assertEqual(StandardBlobTier.Archive, blobs[0].blob_tier)
        self.assertEqual("rehydrate-pending-to-hot", blobs[0].archive_status)
        self.assertFalse(blobs[0].blob_tier_inferred)
