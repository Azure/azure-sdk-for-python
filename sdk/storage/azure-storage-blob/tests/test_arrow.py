# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobProperties, BlobServiceClient, ContainerClient

from devtools_testutils import FakeTokenCredential, recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
# TODO: Replace
TEST_DATA = b""
# ------------------------------------------------------------------------------

class TestStorageApacheArrow(StorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key.secret
        )
        # TODO: Replace
        self.container_name = "utcontainerc93f2958"
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    def create_blobs(self, blob_names: list[str]):
        for blob_name in blob_names:
            blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
            blob_client.upload_blob(TEST_DATA, overwrite=True)

    def verify_blobs(self, blobs_list: list[BlobProperties], blob_names: list[str]):
        assert len(blobs_list) == len(blob_names)
        all_names = {blob.name for blob in blobs_list}
        for blob_name in blob_names:
            assert blob_name in all_names

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_no_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.list_blobs(use_arrow=True))

        self.verify_blobs(blobs_list, [])

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_one_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["blobc93f2958"]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.list_blobs(use_arrow=True))
        self.verify_blobs(blobs_list, blob_names)

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_blobs_paging(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["a", "b", "c", "d"]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blob_pages = container.list_blobs(use_arrow=True, results_per_page=2).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, blob_names[:2])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, blob_names[2:])

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_nested_blobs_paging(self, **kwargs):
        # start_from, end_before
        pass

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_xml_response(self, **kwargs):
        # Many blobs, mock XML response, large, nested
        pass

    # Do the same for walk_blobs
