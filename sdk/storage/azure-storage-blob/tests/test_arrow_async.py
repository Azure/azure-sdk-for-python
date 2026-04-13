# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobProperties
from azure.storage.blob.aio import BlobServiceClient, ContainerClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
# TODO: Replace
TEST_DATA = b""
# ------------------------------------------------------------------------------

class TestStorageApacheArrow(StorageRecordedTestCase):
    async def _setup(self, storage_account_name, storage_account_key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key.secret
        )
        # TODO: Replace
        self.container_name = "utcontainerc93f2958"
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    async def create_blobs(self, blob_names: list[str]):
        for blob_name in blob_names:
            blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
            await blob_client.upload_blob(TEST_DATA, overwrite=True)

    def verify_blobs(self, blobs_list: list[BlobProperties], blob_names: list[str]):
        assert len(blobs_list) == len(blob_names)
        all_names = {blob.name for blob in blobs_list}
        for blob_name in blob_names:
            assert blob_name in all_names

