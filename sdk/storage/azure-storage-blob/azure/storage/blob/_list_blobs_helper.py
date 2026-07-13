# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from typing import Any, Callable, cast, List, Optional, Tuple, Union
from urllib.parse import unquote

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged, PageIterator

from ._deserialize import (
    get_blob_properties_from_generated_code,
    load_many_xml_nodes,
    load_xml_int,
    load_xml_string,
    parse_tags,
)
from ._generated.models import BlobItemInternal, BlobPrefix as GenBlobPrefix, FilterBlobItem
from ._generated._utils.serialization import Deserializer
from ._models import (
    BlobProperties,
    BlobType,
    ContentSettings,
    CopyProperties,
    FilteredBlob,
    ImmutabilityPolicy,
    LeaseProperties,
)
from ._shared.models import DictMixin
from ._shared.response_handlers import process_storage_error, return_context_and_deserialized, return_raw_deserialized

_ARROW_CONTENT_TYPE = "application/vnd.apache.arrow.stream"


def _parse_arrow_response(  # pylint: disable=too-many-locals,too-many-statements
    raw_bytes: Union[bytes, bytearray], container: Optional[str]
) -> Tuple[Optional[str], List[BlobProperties]]:
    """
    Parse an Apache Arrow IPC stream response into a list of BlobProperties.

    :param raw_bytes: The raw Arrow IPC bytes.
    :type raw_bytes: bytes or bytearray
    :param Optional[str] container: The container name to stamp on each item.
    :returns: A tuple of next marker and a list of BlobProperties.
    :rtype: Tuple[Optional[str], List[~azure.storage.blob.BlobProperties]]
    """
    from nanoarrow import ArrayStream  # pylint: disable=import-outside-toplevel
    from nanoarrow.ipc import InputStream  # pylint: disable=import-outside-toplevel

    # Declarative mapping: Arrow column name -> (BlobProperties attr, default value).
    # Arrow column names mirror the List Blobs XML element names (e.g. "Last-Modified").
    # Only scalar fields that map 1-to-1 are listed here; composite sub-objects are
    # handled separately below.
    _SCALAR_FIELDS: List[Tuple[str, str, Any]] = [
        ("Name", "name", None),
        ("Snapshot", "snapshot", None),
        ("VersionId", "version_id", None),
        ("IsCurrentVersion", "is_current_version", None),
        ("Etag", "etag", None),
        ("Deleted", "deleted", False),
        ("Last-Modified", "last_modified", None),
        ("Creation-Time", "creation_time", None),
        ("Content-Length", "size", None),
        ("ServerEncrypted", "server_encrypted", False),
        ("EncryptionScope", "encryption_scope", None),
        ("DeletedTime", "deleted_time", None),
        ("RemainingRetentionDays", "remaining_retention_days", None),
        ("AccessTier", "blob_tier", None),
        ("SmartAccessTier", "smart_access_tier", None),
        ("RehydratePriority", "rehydrate_priority", None),
        ("AccessTierChangeTime", "blob_tier_change_time", None),
        ("AccessTierInferred", "blob_tier_inferred", None),
        ("ArchiveStatus", "archive_status", None),
        ("BlobSequenceNumber", "page_blob_sequence_number", None),
        ("Sealed", "is_append_blob_sealed", None),
        ("LastAccessTime", "last_accessed_on", None),
        ("TagCount", "tag_count", None),
        ("HasVersionsOnly", "has_versions_only", None),
        ("LegalHold", "has_legal_hold", None),
        ("CustomerProvidedKeySha256", "encryption_key_sha256", None),
    ]

    # Sub-object field mappings: Arrow column name -> constructor kwarg name.
    _CONTENT_SETTINGS_FIELDS = {
        "Content-Type": "content_type",
        "Content-Encoding": "content_encoding",
        "Content-Language": "content_language",
        "Content-MD5": "content_md5",
        "Content-Disposition": "content_disposition",
        "Cache-Control": "cache_control",
    }
    _LEASE_FIELDS = {
        "LeaseStatus": "x-ms-lease-status",
        "LeaseState": "x-ms-lease-state",
        "LeaseDuration": "x-ms-lease-duration",
    }
    _COPY_FIELDS = {
        "CopyId": "x-ms-copy-id",
        "CopySource": "x-ms-copy-source",
        "CopyStatus": "x-ms-copy-status",
        "CopyProgress": "x-ms-copy-progress",
        "CopyCompletionTime": "x-ms-copy-completion-time",
        "CopyStatusDescription": "x-ms-copy-status-description",
        "IncrementalCopy": "x-ms-incremental-copy",
        "DestinationSnapshot": "x-ms-copy-destination-snapshot",
    }

    next_marker: Optional[str] = None
    blob_items: List[BlobProperties] = []

    with InputStream.from_readable(BytesIO(raw_bytes)) as stream:
        reader = ArrayStream(stream)
        schema = reader.schema

        # The continuation token is embedded in the Arrow schema metadata.
        metadata = schema.metadata
        if metadata is not None:
            meta_map = dict(metadata.items())
            raw_marker = meta_map.get(b"NextMarker") or meta_map.get(b"nextMarker")
            if raw_marker:
                next_marker = raw_marker.decode("utf-8") if isinstance(raw_marker, bytes) else raw_marker
                next_marker = next_marker or None

        field_names = [field.name for field in schema.fields]

        for batch in reader:
            num_rows = len(batch)
            if num_rows == 0:
                continue
            cols = {}
            for i in range(batch.n_children):
                child = batch.child(i)
                try:
                    cols[field_names[i]] = child.to_pylist()
                except KeyError:
                    offsets = list(child.buffer(1))
                    entries = child.child(0)
                    keys = entries.child(0).to_pylist()
                    values = entries.child(1).to_pylist()
                    cols[field_names[i]] = [
                        {keys[j]: values[j] for j in range(offsets[r], offsets[r + 1])} for r in range(num_rows)
                    ]

            for row in range(num_rows):

                def _get(
                    col_name: str, default: Any = None, _r: int = row
                ) -> Any:  # pylint: disable=cell-var-from-loop
                    col = cols.get(col_name)  # pylint: disable=cell-var-from-loop
                    if col is None:
                        return default
                    val = col[_r]
                    return val if val is not None else default

                blob = BlobProperties()
                blob.container = container  # type: ignore[assignment]
                blob.metadata = {}

                # Apply all scalar 1-to-1 fields from the mapping table.
                for arrow_col, blob_attr, default in _SCALAR_FIELDS:
                    setattr(blob, blob_attr, _get(arrow_col, default))

                # BlobType needs an enum conversion.
                blob_type_val = _get("BlobType")
                blob.blob_type = BlobType(blob_type_val) if blob_type_val else None  # type: ignore[assignment]

                # Composite sub-objects built from their own column sub-sets.
                blob.content_settings = ContentSettings(
                    **{kwarg: _get(col) for col, kwarg in _CONTENT_SETTINGS_FIELDS.items()}
                )
                blob.lease = LeaseProperties(**{kwarg: _get(col) for col, kwarg in _LEASE_FIELDS.items()})
                blob.copy = CopyProperties(**{kwarg: _get(col) for col, kwarg in _COPY_FIELDS.items()})
                blob.immutability_policy = ImmutabilityPolicy(
                    expiry_time=_get("ImmutabilityPolicyUntilDate"),
                    policy_mode=_get("ImmutabilityPolicyMode"),
                )

                # Metadata and tags are returned as their own map-typed columns when the
                # caller opts in via ``include``. They are absent otherwise.
                metadata_val = _get("Metadata")
                if isinstance(metadata_val, dict):
                    blob.metadata = metadata_val  # type: ignore[assignment]
                tags_val = _get("Tags", _get("BlobTags"))
                if isinstance(tags_val, dict):
                    blob.tags = tags_val
                blob_items.append(blob)

    return next_marker, blob_items


class IgnoreListBlobsDeserializer(Deserializer):
    def __call__(self, target_obj, response_data, content_type=None):  # pylint: disable=inconsistent-return-statements
        if target_obj == "ListBlobsFlatSegmentResponse":
            return None
        super().__call__(target_obj, response_data, content_type)


class BlobPropertiesPaged(PageIterator):
    """An Iterable of Blob properties."""

    service_endpoint: Optional[str]
    """The service URL."""
    prefix: Optional[str]
    """A blob name prefix being used to filter the list."""
    marker: Optional[str]
    """The continuation token of the current page of results."""
    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    continuation_token: Optional[str]
    """The continuation token to retrieve the next page of results."""
    location_mode: Optional[str]
    """The location mode being used to list results. The available
    options include "primary" and "secondary"."""
    current_page: Optional[List[BlobProperties]]
    """The current page of listed results."""
    container: Optional[str]
    """The container that the blobs are listed from."""
    delimiter: Optional[str]
    """A delimiting character used for hierarchy listing."""
    command: Callable
    """Function to retrieve the next page of items."""

    def __init__(
        self,
        command: Callable,
        container: str,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None,
        delimiter: Optional[str] = None,
        location_mode: Optional[str] = None,
    ) -> None:
        super(BlobPropertiesPaged, self).__init__(
            get_next=self._get_next_cb, extract_data=self._extract_data_cb, continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.container = container
        self.delimiter = delimiter
        self.current_page = None
        self.location_mode = location_mode

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode,
            )
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = cast(Tuple[Optional[str], Any], get_next_return)
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.container = self._response.container_name
        self.current_page = [self._build_item(item) for item in self._response.segment.blob_items]

        return self._response.next_marker or None, self.current_page

    def _build_item(self, item: Union[BlobItemInternal, BlobProperties]) -> BlobProperties:
        if isinstance(item, BlobProperties):
            return item
        if isinstance(item, BlobItemInternal):
            blob = get_blob_properties_from_generated_code(item)
            blob.container = self.container  # type: ignore [assignment]
            return blob
        return item


class BlobNamesPaged(PageIterator):
    """An Iterable of Blob names."""

    service_endpoint: Optional[str]
    """The service URL."""
    prefix: Optional[str]
    """A blob name prefix being used to filter the list."""
    marker: Optional[str]
    """The continuation token of the current page of results."""
    results_per_page: Optional[int]
    """The maximum number of blobs to retrieve per call."""
    continuation_token: Optional[str]
    """The continuation token to retrieve the next page of results."""
    location_mode: Optional[str]
    """The location mode being used to list results. The available
    options include "primary" and "secondary"."""
    current_page: Optional[List[BlobProperties]]
    """The current page of listed results."""
    container: Optional[str]
    """The container that the blobs are listed from."""
    delimiter: Optional[str]
    """A delimiting character used for hierarchy listing."""
    command: Callable
    """Function to retrieve the next page of items."""

    def __init__(
        self,
        command: Callable,
        container: Optional[str] = None,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None,
        location_mode: Optional[str] = None,
    ) -> None:
        super(BlobNamesPaged, self).__init__(
            get_next=self._get_next_cb, extract_data=self._extract_data_cb, continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.container = container
        self.current_page = None
        self.location_mode = location_mode

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_raw_deserialized,
                use_location=self.location_mode,
            )
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.get("ServiceEndpoint")
        self.prefix = load_xml_string(self._response, "Prefix")
        self.marker = load_xml_string(self._response, "Marker")
        self.results_per_page = load_xml_int(self._response, "MaxResults")
        self.container = self._response.get("ContainerName")

        blobs = load_many_xml_nodes(self._response, "Blob", wrapper="Blobs")
        self.current_page = [load_xml_string(blob, "Name") for blob in blobs]

        next_marker = load_xml_string(self._response, "NextMarker")
        return next_marker or None, self.current_page


class BlobPrefixPaged(BlobPropertiesPaged):
    def __init__(self, *args, **kwargs):
        super(BlobPrefixPaged, self).__init__(*args, **kwargs)
        self.name = self.prefix

    def _extract_data_cb(self, get_next_return):
        continuation_token, _ = super(BlobPrefixPaged, self)._extract_data_cb(get_next_return)
        self.current_page = self._response.segment.blob_prefixes + self._response.segment.blob_items
        self.current_page = [self._build_item(item) for item in self.current_page]
        self.delimiter = self._response.delimiter

        return continuation_token, self.current_page

    def _build_item(self, item):
        item = super(BlobPrefixPaged, self)._build_item(item)
        if isinstance(item, GenBlobPrefix):
            if item.name.encoded:
                name = unquote(item.name.content)
            else:
                name = item.name.content
            return BlobPrefix(
                self._command,
                container=self.container,
                prefix=name,
                results_per_page=self.results_per_page,
                location_mode=self.location_mode,
            )
        return item


class BlobPrefix(ItemPaged, DictMixin):
    """An Iterable of Blob properties.

    Returned from walk_blobs when a delimiter is used.
    Can be thought of as a virtual blob directory."""

    name: str
    """The prefix, or "directory name" of the blob."""
    service_endpoint: Optional[str]
    """The service URL."""
    prefix: str
    """A blob name prefix being used to filter the list."""
    marker: Optional[str]
    """The continuation token of the current page of results."""
    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    next_marker: Optional[str]
    """The continuation token to retrieve the next page of results."""
    location_mode: str
    """The location mode being used to list results. The available
    options include "primary" and "secondary"."""
    current_page: Optional[List[BlobProperties]]
    """The current page of listed results."""
    delimiter: str
    """A delimiting character used for hierarchy listing."""
    command: Callable
    """Function to retrieve the next page of items."""
    container: str
    """The name of the container."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(BlobPrefix, self).__init__(*args, page_iterator_class=BlobPrefixPaged, **kwargs)
        self.name = kwargs.get("prefix")  # type: ignore [assignment]
        self.prefix = kwargs.get("prefix")  # type: ignore [assignment]
        self.results_per_page = kwargs.get("results_per_page")
        self.container = kwargs.get("container")  # type: ignore [assignment]
        self.delimiter = kwargs.get("delimiter")  # type: ignore [assignment]
        self.location_mode = kwargs.get("location_mode")  # type: ignore [assignment]


class FilteredBlobPaged(PageIterator):
    """An Iterable of Blob properties."""

    service_endpoint: Optional[str]
    """The service URL."""
    prefix: Optional[str]
    """A blob name prefix being used to filter the list."""
    marker: Optional[str]
    """The continuation token of the current page of results."""
    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    continuation_token: Optional[str]
    """The continuation token to retrieve the next page of results."""
    location_mode: Optional[str]
    """The location mode being used to list results. The available
    options include "primary" and "secondary"."""
    current_page: Optional[List[BlobProperties]]
    """The current page of listed results."""
    command: Callable
    """Function to retrieve the next page of items."""
    container: Optional[str]
    """The name of the container."""

    def __init__(
        self,
        command: Callable,
        container: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None,
        location_mode: Optional[str] = None,
    ) -> None:
        super(FilteredBlobPaged, self).__init__(
            get_next=self._get_next_cb, extract_data=self._extract_data_cb, continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.marker = continuation_token
        self.results_per_page = results_per_page
        self.container = container
        self.current_page = None
        self.location_mode = location_mode

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode,
            )
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.marker = self._response.next_marker
        self.current_page = [self._build_item(item) for item in self._response.blobs]

        return self._response.next_marker or None, self.current_page

    @staticmethod
    def _build_item(item):
        if isinstance(item, FilterBlobItem):
            tags = parse_tags(item.tags)
            blob = FilteredBlob(name=item.name, container_name=item.container_name, tags=tags)
            return blob
        return item


class ArrowBlobPropertiesPaged(BlobPropertiesPaged):
    """A PageIterator that deserializes Apache Arrow IPC responses from list-blobs operations."""

    # The response type used to deserialize an XML fallback response.
    _xml_response_type = "ListBlobsFlatSegmentResponse"

    def __init__(self, *args: Any, deserializer: Any = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._deserializer = deserializer
        self._arrow_response: Optional[Tuple[Optional[str], List[BlobProperties]]] = None

    def _get_next_cb(self, continuation_token: Optional[str]) -> Any:
        try:
            return self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=self._arrow_cls,
                use_location=self.location_mode,
            )
        except HttpResponseError as error:
            process_storage_error(error)

    def _arrow_cls(self, pipeline_response: Any, deserialized: Any, response_headers: Any) -> Any:
        content_type = response_headers.get("Content-Type", "")
        location_mode = getattr(pipeline_response.http_response, "location_mode", None)
        # The response is Arrow only when the service returns the Arrow stream media type.
        if _ARROW_CONTENT_TYPE in content_type:
            raw_bytes = b"".join(deserialized)
            next_marker, blob_items = _parse_arrow_response(raw_bytes, self.container)
            self._arrow_response = (next_marker, blob_items)
            return location_mode, raw_bytes
        if hasattr(pipeline_response.http_response, "read"):
            pipeline_response.http_response.read()
        xml_response = self._deserializer(self._xml_response_type, pipeline_response.http_response)
        self._arrow_response = None
        return location_mode, xml_response

    def _extract_data_cb(self, get_next_return: Any) -> Tuple[Optional[str], List[BlobProperties]]:
        if self._arrow_response is not None:
            self.location_mode, _ = cast(Tuple[Optional[str], Any], get_next_return)
            next_marker, self.current_page = self._arrow_response
            self._arrow_response = None
            return next_marker or None, self.current_page or []
        return super()._extract_data_cb(get_next_return)


class ArrowBlobPrefixPaged(ArrowBlobPropertiesPaged):
    """Arrow-backed PageIterator for walk_blobs."""

    _xml_response_type = "ListBlobsHierarchySegmentResponse"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.name = self.prefix
        self.delimiter: Optional[str] = kwargs.get("delimiter")

    def _extract_data_cb(self, get_next_return):
        # Arrow responses only carry blob items; defer to the base class for those.
        if self._arrow_response is not None:
            return super()._extract_data_cb(get_next_return)
        # XML fallback: reuse the base to populate the response, then preserve the
        # hierarchy's virtual directories (BlobPrefix) alongside the blobs.
        next_marker, _ = super()._extract_data_cb(get_next_return)
        self.current_page = self._response.segment.blob_prefixes + self._response.segment.blob_items
        self.current_page = [self._build_item(item) for item in self.current_page]
        self.delimiter = self._response.delimiter
        return next_marker, self.current_page

    def _build_item(self, item):
        item = super()._build_item(item)
        if isinstance(item, GenBlobPrefix):
            if item.name.encoded:
                name = unquote(item.name.content)
            else:
                name = item.name.content
            return ArrowBlobPrefix(
                self._command,
                container=self.container,
                prefix=name,
                results_per_page=self.results_per_page,
                location_mode=self.location_mode,
                delimiter=self.delimiter,
                deserializer=self._deserializer,
            )
        return item


class ArrowBlobPrefix(BlobPrefix):
    """An Arrow-backed virtual blob directory returned from walk_blobs.

    Drilling into this prefix re-lists using the Apache Arrow operation, so nested pages
    are parsed the same way (Arrow when available, XML otherwise)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(BlobPrefix, self).__init__(  # pylint: disable=bad-super-call
            *args, page_iterator_class=ArrowBlobPrefixPaged, **kwargs
        )
        self.name = kwargs.get("prefix")  # type: ignore [assignment]
        self.prefix = kwargs.get("prefix")  # type: ignore [assignment]
        self.results_per_page = kwargs.get("results_per_page")
        self.container = kwargs.get("container")  # type: ignore [assignment]
        self.delimiter = kwargs.get("delimiter")  # type: ignore [assignment]
        self.location_mode = kwargs.get("location_mode")  # type: ignore [assignment]
