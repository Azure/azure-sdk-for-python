# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from azure.core.paging import Paged

from .._shared.response_handlers import return_context_and_deserialized, process_storage_error
from .._shared.models import DictMixin, get_enum_value
from .._generated.models import StorageErrorException
from .._generated.models import DirectoryItem
from ..models import Handle, ShareProperties


def _wrap_item(item):
    if isinstance(item, DirectoryItem):
        return {'name': item.name, 'is_directory': True}
    return {'name': item.name, 'size': item.properties.content_length, 'is_directory': False}


class SharePropertiesPaged(Paged):
    """An iterable of Share properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file name prefix being used to filter the list.
    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.file.models.ShareProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only shares whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, marker=None, **kwargs):
        super(SharePropertiesPaged, self).__init__(None, None, async_command=command)
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
        self.current_page = [ShareProperties._from_generated(i) for i in self._response.share_items]  # pylint: disable=protected-access
        self.next_marker = self._response.next_marker or None
        return self.current_page


class HandlesPaged(Paged):
    """An iterable of Handles.

    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.file.models.Handle)

    :param callable command: Function to retrieve the next page of items.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, results_per_page=None, marker=None, **kwargs):
        super(HandlesPaged, self).__init__(None, None, async_command=command)
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
        self.current_page = [Handle._from_generated(h) for h in self._response.handle_list]  # pylint: disable=protected-access
        self.next_marker = self._response.next_marker or None
        return self.current_page


class DirectoryPropertiesPaged(Paged):
    """An iterable for the contents of a directory.

    This iterable will yield dicts for the contents of the directory. The dicts
    will have the keys 'name' (str) and 'is_directory' (bool).
    Items that are files (is_directory=False) will have an additional 'content_length' key.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file name prefix being used to filter the list.
    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(dict(str, Any))

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only directories whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of share names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, marker=None, **kwargs):
        super(DirectoryPropertiesPaged, self).__init__(None, None, async_command=command)
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
                prefix=self.prefix,
                maxresults=self.results_per_page,
                cls=return_context_and_deserialized,
                use_location=self.location_mode)
        except StorageErrorException as error:
            process_storage_error(error)

        self.service_endpoint = self._response.service_endpoint
        self.prefix = self._response.prefix
        self.current_marker = self._response.marker
        self.results_per_page = self._response.max_results
        self.current_page = [_wrap_item(i) for i in self._response.segment.directory_items]
        self.current_page.extend([_wrap_item(i) for i in self._response.segment.file_items])
        self.next_marker = self._response.next_marker or None
        return self.current_page
