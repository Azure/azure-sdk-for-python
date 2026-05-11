# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pyarrow as pa

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
TEST_DATA = b"abc123"
# ------------------------------------------------------------------------------

class TestStorageApacheArrow(StorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=storage_account_key.secret
        )
        self.container_name = self.get_resource_name("utcontainerarrow")
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
    def test_arrow_list_multiple_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["blob1", "blob2"]
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
        blob_names = ["blob1", "blob2", "blob3", "blob4"]
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
        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
            "flat_blob4",
        ]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blob_pages = container.list_blobs(use_arrow=True, results_per_page=3).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, blob_names[:3])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, blob_names[3:6])
        third_blobs_list = list(next(blob_pages))
        self.verify_blobs(third_blobs_list, blob_names[6:])

    def test_arrow_mock_xml_response(self):
        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
            "flat_blob4",
        ]
        account_url = "https://account.blob.core.windows.net/"
        container_name = "mycontainer"

        def _make_xml_response(names: list[str], next_marker: str | None = None) -> ListBlobsFlatSegmentResponse:
            items = [
                BlobItemInternal(
                    name=BlobName(content=name, encoded=False),
                    snapshot="",
                    properties=BlobPropertiesInternal(
                        etag="",
                        last_modified=datetime(2024, 1, 1, tzinfo=timezone.utc),
                        blob_type="BlockBlob",
                    ),
                    deleted=False,
                )
                for name in names
            ]
            return ListBlobsFlatSegmentResponse(
                service_endpoint=account_url,
                container_name=container_name,
                segment=BlobFlatListSegment(blob_items=items),
                next_marker=next_marker,
            )

        # Three pages of 3 blobs each, chained via next_marker.
        xml_pages = [
            _make_xml_response(blob_names[0:3], next_marker="marker1"),
            _make_xml_response(blob_names[3:6], next_marker="marker2"),
            _make_xml_response(blob_names[6:9], next_marker=None),
        ]
        page_index = 0

        container_client = ContainerClient(
            account_url=account_url,
            container_name=container_name,
            credential=AzureNamedKeyCredential("account", "A" * 64),
        )

        mock_http_response = MagicMock()
        mock_http_response.location_mode = None
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_http_response

        def fake_list_blob_flat_segment_apache_arrow(**kwargs):
            cls = kwargs.get("cls")
            return cls(mock_pipeline_response, None, {"Content-Type": "application/xml"})

        def deserializer_side_effect(target, _http_response):
            nonlocal page_index
            response = xml_pages[page_index]
            page_index += 1
            return response

        with patch.object(
            container_client._client.container,  # pylint: disable=protected-access
            "list_blob_flat_segment_apache_arrow",
            side_effect=fake_list_blob_flat_segment_apache_arrow,
        ):
            blob_pages = container_client.list_blobs(use_arrow=True, results_per_page=3).by_page()
            mock_deserializer = MagicMock(side_effect=deserializer_side_effect)
            blob_pages._deserializer = mock_deserializer
            first_blobs_list = list(next(blob_pages))
            self.verify_blobs(first_blobs_list, blob_names[0:3])
            second_blobs_list = list(next(blob_pages))
            self.verify_blobs(second_blobs_list, blob_names[3:6])
            third_blobs_list = list(next(blob_pages))
            self.verify_blobs(third_blobs_list, blob_names[6:9])

        # Confirm the XML deserializer was called once per page.
        assert mock_deserializer.call_count == 3

    def test_arrow_mock_expected_response(self):
        def _make_arrow_page(names: list[str], next_marker: str | None = None) -> bytes:
            schema_meta = {b"NextMarker": (next_marker or "").encode()} if next_marker else {}
            schema = pa.schema([pa.field("Name", pa.string())], metadata=schema_meta)
            batch = pa.record_batch([pa.array(names, type=pa.string())], schema=schema)
            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, schema) as writer:
                writer.write_batch(batch)
            return sink.getvalue().to_pybytes()

        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
            "flat_blob4",
        ]
        # Three pages of 3 blobs each, using the marker to chain pages.
        pages = [
            _make_arrow_page(blob_names[0:3], next_marker="marker1"),
            _make_arrow_page(blob_names[3:6], next_marker="marker2"),
            _make_arrow_page(blob_names[6:9], next_marker=None),
        ]
        page_index = 0

        container_client = ContainerClient(
            account_url="https://account.blob.core.windows.net",
            container_name="mycontainer",
            credential=AzureNamedKeyCredential("account", "A" * 64),
        )

        mock_http_response = MagicMock()
        mock_http_response.location_mode = None
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_http_response

        def fake_list_blob_flat_segment_apache_arrow(**kwargs):
            nonlocal page_index
            cls = kwargs.get("cls")
            raw = iter([pages[page_index]])
            page_index += 1
            return cls(mock_pipeline_response, raw, {"Content-Type": "application/vnd.apache.arrow.stream"})

        with patch.object(
            container_client._client.container,  # pylint: disable=protected-access
            "list_blob_flat_segment_apache_arrow",
            side_effect=fake_list_blob_flat_segment_apache_arrow,
        ):
            blob_pages = container_client.list_blobs(use_arrow=True, results_per_page=3).by_page()
            first_blobs_list = list(next(blob_pages))
            self.verify_blobs(first_blobs_list, blob_names[0:3])
            second_blobs_list = list(next(blob_pages))
            self.verify_blobs(second_blobs_list, blob_names[3:6])
            third_blobs_list = list(next(blob_pages))
            self.verify_blobs(third_blobs_list, blob_names[6:9])

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_walk_no_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.walk_blobs(use_arrow=True))

        self.verify_blobs(blobs_list, [])

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_walk_multiple_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["blob1", "blob2"]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.walk_blobs(use_arrow=True))
        self.verify_blobs(blobs_list, blob_names)

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_walk_blobs_paging(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["blob1", "blob2", "blob3", "blob4"]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blob_pages = container.walk_blobs(use_arrow=True, results_per_page=2).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, blob_names[:2])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, blob_names[2:])

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_walk_nested_blobs_paging(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
            "flat_blob4",
        ]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blob_pages = container.walk_blobs(use_arrow=True, results_per_page=3).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, blob_names[:3])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, blob_names[3:6])
        third_blobs_list = list(next(blob_pages))
        self.verify_blobs(third_blobs_list, blob_names[6:])

    def test_arrow_mock_walk_xml_response(self):
        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
            "flat_blob4",
        ]
        account_url = "https://account.blob.core.windows.net/"
        container_name = "mycontainer"

        def _make_xml_response(names: list[str], next_marker: str | None = None) -> ListBlobsFlatSegmentResponse:
            items = [
                BlobItemInternal(
                    name=BlobName(content=name, encoded=False),
                    snapshot="",
                    properties=BlobPropertiesInternal(
                        etag="",
                        last_modified=datetime(2024, 1, 1, tzinfo=timezone.utc),
                        blob_type="BlockBlob",
                    ),
                    deleted=False,
                )
                for name in names
            ]
            return ListBlobsFlatSegmentResponse(
                service_endpoint=account_url,
                container_name=container_name,
                segment=BlobFlatListSegment(blob_items=items),
                next_marker=next_marker,
            )

        # Three pages of 3 blobs each, chained via next_marker.
        xml_pages = [
            _make_xml_response(blob_names[0:3], next_marker="marker1"),
            _make_xml_response(blob_names[3:6], next_marker="marker2"),
            _make_xml_response(blob_names[6:9], next_marker=None),
        ]
        page_index = 0

        container_client = ContainerClient(
            account_url=account_url,
            container_name=container_name,
            credential=AzureNamedKeyCredential("account", "A" * 64),
        )

        mock_http_response = MagicMock()
        mock_http_response.location_mode = None
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_http_response

        def fake_list_blob_hierarchy_segment_apache_arrow(**kwargs):
            cls = kwargs.get("cls")
            return cls(mock_pipeline_response, None, {"Content-Type": "application/xml"})

        def deserializer_side_effect(target, _http_response):
            nonlocal page_index
            response = xml_pages[page_index]
            page_index += 1
            return response

        with patch.object(
            container_client._client.container,  # pylint: disable=protected-access
            "list_blob_hierarchy_segment_apache_arrow",
            side_effect=fake_list_blob_hierarchy_segment_apache_arrow,
        ):
            blob_pages = container_client.walk_blobs(use_arrow=True, results_per_page=3).by_page()
            mock_deserializer = MagicMock(side_effect=deserializer_side_effect)
            blob_pages._deserializer = mock_deserializer
            first_blobs_list = list(next(blob_pages))
            self.verify_blobs(first_blobs_list, blob_names[0:3])
            second_blobs_list = list(next(blob_pages))
            self.verify_blobs(second_blobs_list, blob_names[3:6])
            third_blobs_list = list(next(blob_pages))
            self.verify_blobs(third_blobs_list, blob_names[6:9])

        # Confirm the XML deserializer was called once per page.
        assert mock_deserializer.call_count == 3

    def test_arrow_mock_walk_expected_response(self):
        def _make_arrow_page(names: list[str], next_marker: str | None = None) -> bytes:
            schema_meta = {b"NextMarker": (next_marker or "").encode()} if next_marker else {}
            schema = pa.schema([pa.field("Name", pa.string())], metadata=schema_meta)
            batch = pa.record_batch([pa.array(names, type=pa.string())], schema=schema)
            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, schema) as writer:
                writer.write_batch(batch)
            return sink.getvalue().to_pybytes()

        blob_names = [
            "a/b/blob1",
            "a/b/blob2",
            "a/c/blob3",
            "d/blob4",
            "d/e/f/blob5",
            "flat_blob1",
            "flat_blob2",
            "flat_blob3",
            "flat_blob4",
        ]
        pages = [
            _make_arrow_page(blob_names[0:3], next_marker="marker1"),
            _make_arrow_page(blob_names[3:6], next_marker="marker2"),
            _make_arrow_page(blob_names[6:9], next_marker=None),
        ]
        page_index = 0

        container_client = ContainerClient(
            account_url="https://account.blob.core.windows.net",
            container_name="mycontainer",
            credential=AzureNamedKeyCredential("account", "A" * 64),
        )

        mock_http_response = MagicMock()
        mock_http_response.location_mode = None
        mock_pipeline_response = MagicMock()
        mock_pipeline_response.http_response = mock_http_response

        def fake_list_blob_hierarchy_segment_apache_arrow(**kwargs):
            nonlocal page_index
            cls = kwargs.get("cls")
            raw = iter([pages[page_index]])
            page_index += 1
            return cls(mock_pipeline_response, raw, {"Content-Type": "application/vnd.apache.arrow.stream"})

        with patch.object(
            container_client._client.container,  # pylint: disable=protected-access
            "list_blob_hierarchy_segment_apache_arrow",
            side_effect=fake_list_blob_hierarchy_segment_apache_arrow,
        ):
            blob_pages = container_client.walk_blobs(use_arrow=True, results_per_page=3).by_page()
            first_blobs_list = list(next(blob_pages))
            self.verify_blobs(first_blobs_list, blob_names[0:3])
            second_blobs_list = list(next(blob_pages))
            self.verify_blobs(second_blobs_list, blob_names[3:6])
            third_blobs_list = list(next(blob_pages))
            self.verify_blobs(third_blobs_list, blob_names[6:9])
