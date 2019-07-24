# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from typing import List, Any, TYPE_CHECKING # pylint: disable=unused-import

from azure.core.paging import Paged

from ..models import BlobProperties, ContainerProperties
from .._shared.response_handlers import return_context_and_deserialized, process_storage_error
from .._shared.models import DictMixin

from .._generated.models import StorageErrorException
from .._generated.models import BlobPrefix as GenBlobPrefix
from .._generated.models import BlobItem


class ContainerPropertiesPaged(Paged):
    """An Iterable of Container properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A container name prefix being used to filter the list.
    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.ContainerProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only containers whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of container names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, marker=None):
        super(ContainerPropertiesPaged, self).__init__(None, None, async_command=command)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = marker or ""
        self.location_mode = None

    async def _async_advance_page(self):
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopAsyncIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopAsyncIteration("End of paging")
        self._current_page_iter_index = 0
        try:
            self.location_mode, self._response = await self._async_get_next(
                marker=self.next_marker or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.container_items
        self.next_marker = self._response.next_marker or None
        return self.current_page

    async def __anext__(self): # type: ignore
        item = await super(ContainerPropertiesPaged, self).__anext__()
        if isinstance(item, ContainerProperties):
            return item
        return ContainerProperties._from_generated(item)  # pylint: disable=protected-access


class BlobPropertiesPaged(Paged):
    """An Iterable of Blob properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str marker: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(
            self, command,
            container=None,
            prefix=None,
            results_per_page=None,
            marker=None,
            delimiter=None,
            location_mode=None):
        super(BlobPropertiesPaged, self).__init__(None, None, async_command=command)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = marker or ""
        self.container = container
        self.delimiter = delimiter
        self.current_page = None
        self.location_mode = location_mode

    async def _async_advance_page(self):
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopAsyncIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopAsyncIteration("End of paging")
        self._current_page_iter_index = 0

        try:
            self.location_mode, self._response = await self._async_get_next(
                prefix=self.prefix,
                marker=self.next_marker or None,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.segment.blob_items
        self.next_marker = self._response.next_marker or None
        self.container = self._response.container_name
        self.delimiter = self._response.delimiter
        return self.current_page

    async def __anext__(self):
        item = await super(BlobPropertiesPaged, self).__anext__()
        if isinstance(item, BlobProperties):
            return item
        if isinstance(item, BlobItem):
            blob = BlobProperties._from_generated(item)  # pylint: disable=protected-access
            blob.container = self.container
            return blob
        return item


class BlobPrefix(BlobPropertiesPaged, DictMixin):
    """An Iterable of Blob properties.

    Returned from walk_blobs when a delimiter is used.
    Can be thought of as a virtual blob directory.

    :ivar str name: The prefix, or "directory name" of the blob.
    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A blob name prefix being used to filter the list.
    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.blob.models.BlobProperties)
    :ivar str container: The container that the blobs are listed from.
    :ivar str delimiter: A delimiting character used for hierarchy listing.

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of blobs to retrieve per
        call.
    :param str marker: An opaque continuation token.
    :param str delimiter:
        Used to capture blobs whose names begin with the same substring up to
        the appearance of the delimiter character. The delimiter may be a single
        character or a string.
    :param location_mode: Specifies the location the request should be sent to.
        This mode only applies for RA-GRS accounts which allow secondary read access.
        Options include 'primary' or 'secondary'.
    """
    def __init__(self, *args, **kwargs):
        super(BlobPrefix, self).__init__(*args, **kwargs)
        self.name = self.prefix

    async def _async_advance_page(self):
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopAsyncIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_marker is None:
            raise StopAsyncIteration("End of paging")
        self._current_page_iter_index = 0
        self.location_mode, self._response = await self._async_get_next(
            prefix=self.prefix,
            marker=self.next_marker or None,
            maxresults=self.results_per_page,
            cls=return_context_and_deserialized,
            use_location=self.location_mode)
        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = self._response.segment.blob_prefixes
        self.current_page.extend(self._response.segment.blob_items)
        self.next_marker = self._response.next_marker or None
        self.container = self._response.container_name
        self.delimiter = self._response.delimiter

    async def __anext__(self):
        item = await super(BlobPrefix, self).__anext__()
        if isinstance(item, GenBlobPrefix):
            return BlobPrefix(
                self._get_next,
                container=self.container,
                prefix=item.name,
                results_per_page=self.results_per_page,
                location_mode=self.location_mode)
        return item
