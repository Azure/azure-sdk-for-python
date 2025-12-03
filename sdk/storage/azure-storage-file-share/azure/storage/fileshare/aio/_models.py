# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

from typing import (
    Any, Callable, Dict, List, Optional
)

from azure.core.async_paging import AsyncPageIterator
from azure.core.exceptions import HttpResponseError

from .._shared.response_handlers import return_context_and_deserialized, process_storage_error
from .._generated.models import DirectoryItem
from .._models import Handle, ShareProperties, DirectoryProperties, FileProperties


def _wrap_item(item):
    if isinstance(item, DirectoryItem):
        return {'name': item.name, 'is_directory': True}
    return {'name': item.name, 'size': item.properties.content_length, 'is_directory': False}


class SharePropertiesPaged(AsyncPageIterator):
    """An iterable of Share properties.

    :param Callable command: Function to retrieve the next page of items.
    :param Optional[str] prefix: Filters the results to return only shares whose names
        begin with the specified prefix.
    :param Optional[int] results_per_page: The maximum number of share names to retrieve per
        call.
    :param Optional[str] continuation_token: An opaque continuation token.
    """

    service_endpoint: Optional[str] = None
    """The service URL."""
    prefix: Optional[str] = None
    """A filename prefix being used to filter the list."""
    marker: Optional[str] = None
    """The continuation token of the current page of results."""
    results_per_page: Optional[int] = None
    """The maximum number of results to retrieve per API call."""
    location_mode: Optional[str] = None
    """The location mode being used to list results. The available
        options include "primary" and "secondary"."""
    current_page: List[ShareProperties]
    """The current page of listed results."""

    def __init__(
        self, command: Callable,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None
    ) -> None:
        super(SharePropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                prefix=self.prefix,
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
        self.current_page = [ShareProperties._from_generated(i) for i in self._response.share_items]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class HandlesPaged(AsyncPageIterator):
    """An iterable of Handles.

    :param Callable command: Function to retrieve the next page of items.
    :param Optional[int] results_per_page: The maximum number of share names to retrieve per call.
    :param Optional[str] continuation_token: An opaque continuation token to retrieve the next page of results.
    """

    marker: Optional[str] = None
    """The continuation token of the current page of results."""
    results_per_page: Optional[int] = None
    """The maximum number of results retrieved per API call."""
    location_mode: Optional[str] = None
    """The location mode being used to list results.
        The available options include "primary" and "secondary"."""
    current_page: List[Handle]
    """The current page of listed results."""

    def __init__(
        self, command: Callable,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None
    ) -> None:
        super(HandlesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                marker=continuation_token or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.current_page = [Handle._from_generated(h) for h in self._response.handle_list]  # pylint: disable=protected-access
        return self._response.next_marker or None, self.current_page


class DirectoryPropertiesPaged(AsyncPageIterator):
    """An iterable for the contents of a directory.

    This iterable will yield dicts for the contents of the directory. The dicts
    will have the keys 'name' (str) and 'is_directory' (bool).
    Items that are files (is_directory=False) will have an additional 'content_length' key.

    :param Callable command: Function to retrieve the next page of items.
    :param Optional[str] prefix: Filters the results to return only directories whose names
        begin with the specified prefix.
    :param Optional[int] results_per_page: The maximum number of share names to retrieve per call.
    :param Optional[str] continuation_token: An opaque continuation token.
    """

    service_endpoint: Optional[str] = None
    """The service URL."""
    prefix: Optional[str] = None
    """A file name prefix being used to filter the list."""
    marker: Optional[str] = None
    """The continuation token of the current page of results."""
    results_per_page: Optional[int] = None
    """The maximum number of results retrieved per API call."""
    continuation_token: Optional[str] = None
    """The continuation token to retrieve the next page of results."""
    location_mode: Optional[str] = None
    """The location mode being used to list results. The available options include "primary" and "secondary"."""
    current_page: List[Dict[str, Any]]
    """The current page of listed results."""

    def __init__(
        self, command: Callable,
        prefix: Optional[str] = None,
        results_per_page: Optional[int] = None,
        continuation_token: Optional[str] = None
    ) -> None:
        super(DirectoryPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None
        self.current_page = []

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                marker=continuation_token or None,
                prefix=self.prefix,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        self.service_endpoint = self._response.service_endpoint
        self.marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [DirectoryProperties._from_generated(i) for i in self._response.segment.directory_items] # pylint: disable = protected-access
        self.current_page.extend([FileProperties._from_generated(i) for i in self._response.segment.file_items]) # pylint: disable = protected-access
        return self._response.next_marker or None, self.current_page
