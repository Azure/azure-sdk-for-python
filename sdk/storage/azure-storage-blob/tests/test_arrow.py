# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobProperties, BlobServiceClient, BlobType, ContainerClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

# ------------------------------------------------------------------------------
TEST_DATA = b"abc123"
# ------------------------------------------------------------------------------


def _rich_blob_xml(name: str) -> str:
    """A single <Blob> element with as many properties populated as possible."""
    return (
        "<Blob>"
        f"<Name>{name}</Name>"
        "<Properties>"
        "<Creation-Time>Mon, 01 Jan 2024 00:00:00 GMT</Creation-Time>"
        "<Last-Modified>Tue, 02 Jan 2024 03:04:05 GMT</Last-Modified>"
        "<Etag>0x8DABCDEF1234567</Etag>"
        "<Content-Length>1234</Content-Length>"
        "<Content-Type>text/plain</Content-Type>"
        "<Content-Encoding>gzip</Content-Encoding>"
        "<Content-Language>en-US</Content-Language>"
        "<Content-MD5>ASNFZ4mrze8BI0VniavN7w==</Content-MD5>"
        "<Cache-Control>no-cache</Cache-Control>"
        "<Content-Disposition>inline</Content-Disposition>"
        "<BlobType>BlockBlob</BlobType>"
        "<AccessTier>Hot</AccessTier>"
        "<AccessTierInferred>true</AccessTierInferred>"
        "<LeaseStatus>unlocked</LeaseStatus>"
        "<LeaseState>available</LeaseState>"
        "<ServerEncrypted>true</ServerEncrypted>"
        "<TagCount>1</TagCount>"
        "</Properties>"
        "<Metadata><color>blue</color><size>large</size></Metadata>"
        "<Tags><TagSet><Tag><Key>env</Key><Value>prod</Value></Tag></TagSet></Tags>"
        "</Blob>"
    )


def _simple_blob_xml(name: str) -> str:
    """A minimal but valid <Blob> element."""
    return (
        "<Blob>"
        f"<Name>{name}</Name>"
        "<Properties>"
        "<Last-Modified>Tue, 02 Jan 2024 03:04:05 GMT</Last-Modified>"
        "<Etag>0x8DABCDEF1234567</Etag>"
        "<BlobType>BlockBlob</BlobType>"
        "</Properties>"
        "</Blob>"
    )


def _enumeration_results_xml(blobs_xml: str, next_marker: str = "") -> bytes:
    """Wrap one or more <Blob> elements in a valid List Blobs response body."""
    marker = f"<NextMarker>{next_marker}</NextMarker>" if next_marker else "<NextMarker/>"
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<EnumerationResults ServiceEndpoint="https://account.blob.core.windows.net/" ContainerName="mycontainer">'
        "<Prefix></Prefix><MaxResults>10</MaxResults>"
        f"<Blobs>{blobs_xml}</Blobs>{marker}"
        "</EnumerationResults>"
    ).encode("utf-8")


def _blob_prefix_xml(name: str) -> str:
    """A <BlobPrefix> (virtual directory) element for a hierarchy listing."""
    return f"<BlobPrefix><Name>{name}</Name></BlobPrefix>"


def _hierarchy_results_xml(blobs_xml: str, next_marker: str = "") -> bytes:
    """Wrap <BlobPrefix>/<Blob> elements in a valid hierarchical List Blobs response body."""
    marker = f"<NextMarker>{next_marker}</NextMarker>" if next_marker else "<NextMarker/>"
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<EnumerationResults ServiceEndpoint="https://account.blob.core.windows.net/" ContainerName="mycontainer">'
        "<Prefix></Prefix><MaxResults>10</MaxResults><Delimiter>/</Delimiter>"
        f"<Blobs>{blobs_xml}</Blobs>{marker}"
        "</EnumerationResults>"
    ).encode("utf-8")


class _MockXmlHttpResponse:
    """A minimal HTTP response carrying a raw XML body for the deserializer to parse."""

    def __init__(self, xml_body: bytes) -> None:
        self._body = xml_body
        self.headers = {"content-type": "application/xml"}
        self.location_mode = None

    def body(self) -> bytes:
        return self._body

    def text(self, encoding=None) -> str:  # pylint: disable=unused-argument
        return self._body.decode("utf-8")

    def read(self) -> bytes:
        return self._body


def _mock_container_client() -> ContainerClient:
    return ContainerClient(
        account_url="https://account.blob.core.windows.net",
        container_name="mycontainer",
        credential=AzureNamedKeyCredential("account", "A" * 64),
    )


class TestStorageApacheArrow(StorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), credential=storage_account_key.secret
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
        for blob in blobs_list:
            # Skip virtual-directory entries from walk_blobs; they carry only a name.
            if not isinstance(blob, BlobProperties) or blob.name.endswith("/"):
                continue
            assert blob.blob_type == BlobType.BLOCKBLOB
            assert blob.size == len(TEST_DATA)
            assert blob.etag is not None
            assert blob.last_modified is not None
            assert blob.creation_time is not None
            assert blob.last_accessed_on is not None
            assert blob.server_encrypted is True
            assert blob.blob_tier is not None
            assert blob.blob_tier_inferred is not None
            assert blob.lease.state == "available"
            assert blob.lease.status == "unlocked"
            assert blob.content_settings.content_type == "application/octet-stream"
            assert blob.content_settings.content_md5 is not None

    def verify_all_fields(self, blob: BlobProperties):
        # Verifies the properties produced by _rich_blob_xml were fully deserialized.
        assert blob.name == "dir/blob1"
        assert blob.blob_type == BlobType.BLOCKBLOB
        assert blob.etag == "0x8DABCDEF1234567"
        assert blob.size == 1234
        assert blob.server_encrypted is True
        assert blob.tag_count == 1
        assert blob.creation_time == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert blob.last_modified == datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        assert blob.blob_tier == "Hot"
        assert blob.blob_tier_inferred is True
        assert blob.content_settings.content_type == "text/plain"
        assert blob.content_settings.content_encoding == "gzip"
        assert blob.content_settings.content_language == "en-US"
        assert blob.content_settings.cache_control == "no-cache"
        assert blob.content_settings.content_disposition == "inline"
        assert blob.content_settings.content_md5 is not None
        assert blob.lease.status == "unlocked"
        assert blob.lease.state == "available"
        assert blob.metadata == {"color": "blue", "size": "large"}
        assert blob.tags == {"env": "prod"}

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_no_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.list_blobs(response_format="arrow"))

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
        blobs_list = list(container.list_blobs(response_format="arrow"))
        self.verify_blobs(blobs_list, blob_names)

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_blobs_with_metadata_and_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {"color": "blue", "size": "large"}
        tags = {"tag1": "firsttag", "tag2": "secondtag"}
        blob_client = self.bsc.get_blob_client(self.container_name, "blob1")
        blob_client.upload_blob(TEST_DATA, overwrite=True, metadata=metadata, tags=tags)

        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.list_blobs(response_format="arrow", include=["metadata", "tags"]))

        self.verify_blobs(blobs_list, ["blob1"])
        blob = blobs_list[0]
        assert blob.metadata == metadata
        assert blob.tags == tags

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_list_blobs_paging(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_names = ["blob1", "blob2", "blob3", "blob4"]
        self.create_blobs(blob_names)

        container = self.bsc.get_container_client(self.container_name)
        blob_pages = container.list_blobs(response_format="arrow", results_per_page=2).by_page()
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
        blob_pages = container.list_blobs(response_format="arrow", results_per_page=3).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, blob_names[:3])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, blob_names[3:6])
        third_blobs_list = list(next(blob_pages))
        self.verify_blobs(third_blobs_list, blob_names[6:])

    def test_arrow_list_xml_fallback(self):
        page1 = _enumeration_results_xml(_rich_blob_xml("dir/blob1") + _simple_blob_xml("blob2"), next_marker="marker1")
        page2 = _enumeration_results_xml(_simple_blob_xml("blob3"))
        pages = [page1, page2]
        page_index = 0

        container_client = _mock_container_client()

        def fake_list_blob_flat_segment_apache_arrow(**kwargs):
            nonlocal page_index
            cls = kwargs["cls"]
            pipeline_response = SimpleNamespace(http_response=_MockXmlHttpResponse(pages[page_index]))
            page_index += 1
            return cls(pipeline_response, iter([]), {"Content-Type": "application/xml"})

        with patch.object(
            container_client._client.container,  # pylint: disable=protected-access
            "list_blob_flat_segment_apache_arrow",
            side_effect=fake_list_blob_flat_segment_apache_arrow,
        ):
            blob_pages = container_client.list_blobs(
                response_format="arrow", results_per_page=2, include=["metadata", "tags"]
            ).by_page()
            first_page = list(next(blob_pages))
            second_page = list(next(blob_pages))

        # Paging is driven by the NextMarker parsed out of the XML.
        assert page_index == 2
        assert [blob.name for blob in first_page] == ["dir/blob1", "blob2"]
        assert [blob.name for blob in second_page] == ["blob3"]

        # The first blob has every property populated so we can assert the XML was fully deserialized.
        self.verify_all_fields(first_page[0])

    @BlobPreparer()
    @recorded_by_proxy
    def test_arrow_walk_no_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blobs_list = list(container.walk_blobs(response_format="arrow"))

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
        blobs_list = list(container.walk_blobs(response_format="arrow"))
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
        blob_pages = container.walk_blobs(response_format="arrow", results_per_page=2).by_page()
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
        blob_pages = container.walk_blobs(response_format="arrow", results_per_page=3).by_page()
        first_blobs_list = list(next(blob_pages))
        self.verify_blobs(first_blobs_list, ["a/", "d/", "flat_blob1"])
        second_blobs_list = list(next(blob_pages))
        self.verify_blobs(second_blobs_list, ["flat_blob2", "flat_blob3", "flat_blob4"])

    def test_arrow_walk_xml_fallback(self):
        page1 = _hierarchy_results_xml(
            _blob_prefix_xml("a/") + _blob_prefix_xml("d/") + _rich_blob_xml("dir/blob1"),
            next_marker="marker1",
        )
        page2 = _hierarchy_results_xml(_simple_blob_xml("blob3"))
        pages = [page1, page2]
        page_index = 0

        container_client = _mock_container_client()

        def fake_list_blob_hierarchy_segment_apache_arrow(**kwargs):
            nonlocal page_index
            cls = kwargs["cls"]
            pipeline_response = SimpleNamespace(http_response=_MockXmlHttpResponse(pages[page_index]))
            page_index += 1
            return cls(pipeline_response, iter([]), {"Content-Type": "application/xml"})

        with patch.object(
            container_client._client.container,  # pylint: disable=protected-access
            "list_blob_hierarchy_segment_apache_arrow",
            side_effect=fake_list_blob_hierarchy_segment_apache_arrow,
        ):
            blob_pages = container_client.walk_blobs(
                response_format="arrow", results_per_page=2, include=["metadata", "tags"]
            ).by_page()
            first_page = list(next(blob_pages))
            second_page = list(next(blob_pages))

        assert page_index == 2
        assert [item.name for item in first_page] == ["a/", "d/", "dir/blob1"]
        assert not isinstance(first_page[0], BlobProperties)
        assert not isinstance(first_page[1], BlobProperties)
        assert isinstance(first_page[2], BlobProperties)
        self.verify_all_fields(first_page[2])
        assert [item.name for item in second_page] == ["blob3"]
