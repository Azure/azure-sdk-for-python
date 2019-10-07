# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import asyncio
import unittest

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)

from azure.storage.blob.models import (
    StandardBlobTier
)

from testcase import (
    StorageTestCase,
    TestMode,
    record
)

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


class BlobStorageAccountTestAsync(StorageTestCase):
    def setUp(self):
        super(BlobStorageAccountTestAsync, self).setUp()

        url = self._get_account_url()
        credential = self._get_shared_key_credential()
        self.bsc = BlobServiceClient(url, credential=credential, transport=AiohttpTestTransport())
        self.container_name = self.get_resource_name('utcontainer')

        # if not self.is_playback():
        #     self.bsc.create_container(self.container_name)

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.bsc.delete_container(self.container_name))
            except:
                pass

        return super(BlobStorageAccountTestAsync, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    async def _setup(self):
        if not self.is_playback():
            try:
                await self.bsc.create_container(self.container_name)
            except:
                pass

    def _get_blob_reference(self):
        blob_name = self.get_resource_name(TEST_BLOB_PREFIX)
        return self.bsc.get_blob_client(self.container_name, blob_name)

    async def _create_blob(self):
        blob = self._get_blob_reference()
        await blob.upload_blob(b'')
        return blob

    async def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = await blob.download_blob().content_as_bytes()
        self.assertEqual(actual_data, expected_data)

    # --Tests specific to Blob Storage Accounts (not general purpose)------------

    async def _test_standard_blob_tier_set_tier_api(self):
        await self._setup()
        container = self.bsc.get_container_client(self.container_name)
        tiers = [StandardBlobTier.Archive, StandardBlobTier.Cool, StandardBlobTier.Hot]

        for tier in tiers:
            blob = self._get_blob_reference()
            data = b'hello world'
            await blob.upload_blob(data)

            blob_ref = await blob.get_blob_properties()
            self.assertIsNotNone(blob_ref.blob_tier)
            self.assertTrue(blob_ref.blob_tier_inferred)
            self.assertIsNone(blob_ref.blob_tier_change_time)

            blobs = []
            async for b in container.list_blobs():
                blobs.append(b)

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob.blob_name)
            self.assertIsNotNone(blobs[0].blob_tier)
            self.assertTrue(blobs[0].blob_tier_inferred)
            self.assertIsNone(blobs[0].blob_tier_change_time)

            await blob.set_standard_blob_tier(tier)

            blob_ref2 = await blob.get_blob_properties()
            self.assertEqual(tier, blob_ref2.blob_tier)
            self.assertFalse(blob_ref2.blob_tier_inferred)
            self.assertIsNotNone(blob_ref2.blob_tier_change_time)

            blobs = []
            async for b in container.list_blobs():
                blobs.append(b)

            # Assert
            self.assertIsNotNone(blobs)
            self.assertGreaterEqual(len(blobs), 1)
            self.assertIsNotNone(blobs[0])
            self.assertNamedItemInContainer(blobs, blob.blob_name)
            self.assertEqual(blobs[0].blob_tier, tier)
            self.assertFalse(blobs[0].blob_tier_inferred)
            self.assertIsNotNone(blobs[0].blob_tier_change_time)

            await blob.delete_blob()

    @record
    def test_standard_blob_tier_set_tier_api(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_standard_blob_tier_set_tier_api())

    async def _test_rehydration_status(self):
        await self._setup()
        blob_name = 'rehydration_test_blob_1'
        blob_name2 = 'rehydration_test_blob_2'
        container = self.bsc.get_container_client(self.container_name)

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

    @record
    def test_rehydration_status(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rehydration_status())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
