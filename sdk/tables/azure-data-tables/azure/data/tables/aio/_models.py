# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum

from azure.data.tables._deserialize import _convert_to_entity
from azure.data.tables._shared.models import Services
from azure.data.tables._shared.response_handlers import return_context_and_deserialized, process_storage_error
from azure.core.exceptions import HttpResponseError
from azure.core.async_paging import AsyncPageIterator
# from .._generated.models import AccessPolicy as GenAccessPolicy
# from .._generated.models import Logging as GeneratedLogging
# from .._generated.models import Metrics as GeneratedMetrics
# from .._generated.models import RetentionPolicy as GeneratedRetentionPolicy
# from .._generated.models import CorsRule as GeneratedCorsRule


class TablePropertiesPaged(AsyncPageIterator):
    """An iterable of Table properties.

    :keyword str service_endpoint: The service URL.
    :keyword str prefix: A queue name prefix being used to filter the list.
    :keyword str marker: The continuation token of the current page of results.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str next_marker: The continuation token to retrieve the next page of results.
    :keyword str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, prefix=None, query_options=None, continuation_token=None):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.prefix = prefix
        self.service_endpoint = None
        self.next_table_name = None
        self._headers = None
        self.query_options = query_options
        self.location_mode = None

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                next_table_name=continuation_token or None,
                # query_options=self.query_options or None,
                cls=return_context_and_deserialized,
                use_location=self.location_mode
            )
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response, self._headers = get_next_return
        props_list = [t for t in self._response.value]
        return self._headers['x-ms-continuation-NextTableName'] or None, props_list


class TableEntityPropertiesPaged(AsyncPageIterator):
    """An iterable of TableEntity properties.

    :keyword str service_endpoint: The service URL.
    :keyword str prefix: A queue name prefix being used to filter the list.
    :keyword str marker: The continuation token of the current page of results.
    :keyword int results_per_page: The maximum number of results retrieved per API call.
    :keyword str next_marker: The continuation token to retrieve the next page of results.
    :keyword str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, results_per_page=None, table=None,
                 continuation_token=None):
        super(TableEntityPropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or {}
        )
        self._command = command
        self._headers = None
        self.results_per_page = results_per_page
        self.table = table
        self.location_mode = None

    async def _get_next_cb(self, continuation_token):
        row_key = ""
        partition_key = ""
        for key, value in continuation_token.items():
            if key == "RowKey":
                row_key = value
            if key == "PartitionKey":
                partition_key = value
        try:
            return await self._command(
                query_options=self.results_per_page or None,
                next_row_key=row_key or None,
                next_partition_key=partition_key or None,
                table=self.table,
                cls=return_context_and_deserialized,
                use_location=self.location_mode
            )
        except HttpResponseError as error:
            process_storage_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response, self._headers = get_next_return
        props_list = [_convert_to_entity(t) for t in self._response.value]
        next_entity = {}
        if self._headers['x-ms-continuation-NextPartitionKey'] or self._headers['x-ms-continuation-NextRowKey']:
            next_entity = {'PartitionKey': self._headers['x-ms-continuation-NextPartitionKey'],
                           'RowKey': self._headers['x-ms-continuation-NextRowKey']}
        return next_entity or None, props_list

