# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobProperties, BlobServiceClient, ContainerClient
from azure.storage.blob._generated.models import (
    BlobFlatListSegment,
    BlobItemInternal,
    BlobName,
    BlobPropertiesInternal,
    ListBlobsFlatSegmentResponse,
)

from devtools_testutils import recorded_by_proxy
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
        blob_names = ["blobc93f2958"]  # TODO: Replace
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
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["a/blob1", "b/blob2", "c/blob3", "d/blob4", "e", "f"]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blob_pages = container.list_blobs(use_arrow=True, results_per_page=2).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, blob_names[:2])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, blob_names[2:4])
        third_blobs_list = list(next(blob_pages))
        self.verify_blobs(third_blobs_list, blob_names[4:])

    def test_arrow_xml_response(self):
        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
        ]

        # Build a real ListBlobsFlatSegmentResponse model (no XML parsing needed).
        blob_items = [
            BlobItemInternal(
                name=BlobName(content=name, encoded=False),
                snapshot="",
                properties=BlobPropertiesInternal(
                    etag="",
                    last_modified=datetime(2024, 1, 1, tzinfo=timezone.utc),
                    blob_type="BlockBlob"
                ),
                deleted=False,
            )
            for name in blob_names
        ]
        xml_response = ListBlobsFlatSegmentResponse(
            service_endpoint="https://account.blob.core.windows.net/",
            container_name="mycontainer",
            segment=BlobFlatListSegment(blob_items=blob_items),
            next_marker=None,
        )

        # Set up a minimal ContainerClient (no real HTTP calls needed).
        container_client = ContainerClient(
            account_url="https://account.blob.core.windows.net",
            container_name="mycontainer",
            credential=AzureNamedKeyCredential("account", "A" * 64),
        )

        # Mock pipeline_response: Content-Type is application/xml so _arrow_cls takes the XML path.
        mock_http_response = MagicMock()
        mock_http_response.location_mode = None
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_http_response

        # Intercept the generated operation: call cls with our fake pipeline_response.
        def fake_list_blob_flat_segment_apache_arrow(**kwargs):
            cls = kwargs.get("cls")
            return cls(mock_pipeline_response, None, {"Content-Type": "application/xml"})

        with patch.object(
            container_client._client.container,
            "list_blob_flat_segment_apache_arrow",
            side_effect=fake_list_blob_flat_segment_apache_arrow,
        ):
            page_iterator = container_client.list_blobs(use_arrow=True).by_page()
            page_iterator._deserializer = MagicMock(return_value=xml_response)
            blobs_list = [blob for page in page_iterator for blob in page]

        self.verify_blobs(blobs_list, blob_names)

    # Do the same for walk_blobs
