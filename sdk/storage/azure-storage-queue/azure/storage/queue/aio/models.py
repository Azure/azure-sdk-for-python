# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called

from typing import List # pylint: disable=unused-import
from azure.core.paging import Paged
from .._shared.response_handlers import (
    process_storage_error,
    return_context_and_deserialized,
    return_headers_and_deserialized)
from .._shared.models import DictMixin
from .._generated.models import StorageErrorException
from .._generated.models import AccessPolicy as GenAccessPolicy
from .._generated.models import Logging as GeneratedLogging
from .._generated.models import Metrics as GeneratedMetrics
from .._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from .._generated.models import CorsRule as GeneratedCorsRule
from ..models import QueueMessage, QueueProperties


class MessagesPaged(Paged):
    """An iterable of Queue Messages.

    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.queue.models.QueueMessage)

    :param callable command: Function to retrieve the next page of items.
    :param int results_per_page: The maximum number of messages to retrieve per
        call.
    """
    def __init__(self, command, results_per_page=None):
        super(MessagesPaged, self).__init__(None, None, async_command=command)
        self.results_per_page = results_per_page

    async def _async_advance_page(self):
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopIteration if no further page
        :return: The current page list
        :rtype: list
        """
        self._current_page_iter_index = 0
        try:
            messages = await self._async_get_next(number_of_messages=self.results_per_page)
            if not messages:
                raise StopAsyncIteration()
        except StorageErrorException as error:
            process_storage_error(error)
        self.current_page = [QueueMessage._from_generated(q) for q in messages]  # pylint: disable=protected-access
        return self.current_page


class QueuePropertiesPaged(Paged):
    """An iterable of Queue properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A queue name prefix being used to filter the list.
    :ivar str current_marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.queue.models.QueueProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str marker: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, marker=None):
        super(QueuePropertiesPaged, self).__init__(None, None, async_command=command)
        self.service_endpoint = None
        self.prefix = prefix
        self.current_marker = None
        self.results_per_page = results_per_page
        self.next_marker = marker or ""
        self.location_mode = None

    async def _async_advance_page(self):
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopIteration if no further page
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
        self.current_page = [QueueProperties._from_generated(q) for q in self._response.queue_items]  # pylint: disable=protected-access
        self.next_marker = self._response.next_marker or None
        return self.current_page
