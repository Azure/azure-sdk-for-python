# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio

from typing import Callable, List, Optional
from urllib.parse import unquote

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator
from azure.core.exceptions import HttpResponseError

from .._deserialize import (
    get_blob_properties_from_generated_code,
    load_many_xml_nodes,
    load_xml_int,
    load_xml_string
)
from .._generated.models import BlobItemInternal, BlobPrefix as GenBlobPrefix
from .._list_blobs_helper import _ARROW_CONTENT_TYPE, _parse_arrow_response
from .._models import BlobProperties
from .._shared.models import DictMixin
from .._shared.response_handlers import (
    process_storage_error,
    return_context_and_deserialized,
    return_raw_deserialized
)


class BlobPropertiesPaged(AsyncPageIterator):
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
        self, command: Callable,
        container: Optional[str] = None,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None,
        delimiter: Optional[str] = None,
        location_mode: Optional[str] = None,
    ) -> None:
        super(BlobPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
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

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.container = self._response.container_name
        self.current_page = [self._build_item(item) for item in self._response.segment.blob_items]

        return self._response.next_marker or None, self.current_page

    def _build_item(self, item):
        if isinstance(item, BlobProperties):
            return item
        if isinstance(item, BlobItemInternal):
            blob = get_blob_properties_from_generated_code(item)
            blob.container = self.container  # type: ignore [assignment]
            return blob
        return item


class BlobNamesPaged(AsyncPageIterator):
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
        self, command: Callable,
        container: Optional[str] = None,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None,
        location_mode: Optional[str] = None
    ) -> None:
        super(BlobNamesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.container = container
        self.current_page = None
        self.location_mode = location_mode

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_raw_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.get('ServiceEndpoint')
        self.prefix = load_xml_string(self._response, 'Prefix')
        self.marker = load_xml_string(self._response, 'Marker')
        self.results_per_page = load_xml_int(self._response, 'MaxResults')
        self.container = self._response.get('ContainerName')

        blobs = load_many_xml_nodes(self._response, 'Blob', wrapper='Blobs')
        self.current_page = [load_xml_string(blob, 'Name') for blob in blobs]

        next_marker = load_xml_string(self._response, 'NextMarker')
        return next_marker or None, self.current_page


class BlobPrefix(AsyncItemPaged, DictMixin):
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

    def __init__(self, *args, **kwargs):
        super(BlobPrefix, self).__init__(*args, page_iterator_class=BlobPrefixPaged, **kwargs)
        self.name = kwargs.get('prefix')
        self.prefix = kwargs.get('prefix')
        self.results_per_page = kwargs.get('results_per_page')
        self.container = kwargs.get('container')
        self.delimiter = kwargs.get('delimiter')
        self.location_mode = kwargs.get('location_mode')


class BlobPrefixPaged(BlobPropertiesPaged):
    def __init__(self, *args, **kwargs):
        super(BlobPrefixPaged, self).__init__(*args, **kwargs)
        self.name = self.prefix

    async def _extract_data_cb(self, get_next_return):
        continuation_token, _ = await super(BlobPrefixPaged, self)._extract_data_cb(get_next_return)
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
                location_mode=self.location_mode)
        return item


class ArrowBlobPropertiesPaged(BlobPropertiesPaged):
    """An async PageIterator that deserializes Apache Arrow IPC responses from list-blobs operations."""

    def __init__(self, *args, deserializer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._deserializer = deserializer
        self._arrow_response = None

    async def _arrow_cls(self, pipeline_response, deserialized, response_headers):
        content_type = response_headers.get("Content-Type", "")
        location_mode = getattr(pipeline_response.http_response, "location_mode", None)
        if _ARROW_CONTENT_TYPE in content_type:
            raw_bytes = b"".join(deserialized)
            next_marker, blob_items = _parse_arrow_response(raw_bytes, self.container)
            self._arrow_response = (next_marker, blob_items)
            return location_mode, raw_bytes
        if hasattr(pipeline_response.http_response, "read"):
            await pipeline_response.http_response.read()
        xml_response = self._deserializer("ListBlobsFlatSegmentResponse", pipeline_response.http_response)
        self._arrow_response = None
        return location_mode, xml_response

    async def _get_next_cb(self, continuation_token):
        try:
            result = await self._command(
                prefix=self.prefix,
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=self._arrow_cls,
                use_location=self.location_mode,
            )
            if asyncio.iscoroutine(result):
                return await result
            return result
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        if self._arrow_response is not None:
            self.location_mode, _ = get_next_return
            next_marker, self.current_page = self._arrow_response
            self._arrow_response = None
            return next_marker or None, self.current_page or []
        return await super()._extract_data_cb(get_next_return)


class ArrowBlobPrefixPaged(ArrowBlobPropertiesPaged):
    """Arrow-backed AsyncPageIterator for walk_blobs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.prefix
        self.delimiter = kwargs.get("delimiter")
