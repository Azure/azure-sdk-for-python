# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContainerClient

from devtools_testutils import FakeTokenCredential, recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
SMALL_BLOB_SIZE = 1024
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
# ------------------------------------------------------------------------------

class TestStorageApacheArrow(StorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key.secret
        )
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name, timeout=5)
            except ResourceExistsError:
                pass
            try:
                self.bsc.create_container(self.source_container_name, timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)

    def _create_blob(self, tags=None, data=b"", **kwargs):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(data, tags=tags, overwrite=True, **kwargs)
        return blob

    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_one_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self._create_blob()

        container = self.bsc.get_container_client(self.container_name)
        blobs = list(container.list_blobs(use_arrow=True))
        assert blobs is not None
        print(blobs)
        print(len(blobs))
