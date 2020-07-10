# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.async_paging import AsyncPageIterator
from azure.table._deserialization import _convert_to_entity
from azure.table._entity import Entity
from azure.table._generated.models import TableProperties
from azure.table._shared.response_handlers import return_context_and_deserialized, process_storage_error
from azure.core.exceptions import HttpResponseError


class TablePropertiesPaged(AsyncPageIterator):
    """An iterable of Table properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A queue name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
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
        self.results_per_page = results_per_page
        self.location_mode = None

    async def _get_next_cb(self, continuation_token):
        try:
            return await self._command(
                next_table_name=continuation_token or None,
                query_options=self.results_per_page or None,
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

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A queue name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
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
            continuation_token=continuation_token or ""
        )
        self._command = command
        self._headers = None
        self.results_per_page = results_per_page
        self.table = table
        self.location_mode = None

    async def _get_next_cb(self, continuation_token):
        row_key = None
        partition_key = None
        if continuation_token:
            tokens = continuation_token.split(" ")
            row_key = tokens[1]
            partition_key = tokens[0]
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
        props_list = [Entity(_convert_to_entity(t)) for t in self._response.value]
        pk = self._headers['x-ms-continuation-NextPartitionKey']
        rk = self._headers['x-ms-continuation-NextRowKey']
        next_entity = ''
        if pk and rk:
            next_entity = pk + " " + rk
        elif pk:
            next_entity = pk
        elif rk:
            next_entity = " " + rk
        return next_entity or None, props_list

class UpdateMode(object):
    def __init__(self):
        self.r = False
        self.m = False

    def replace(self):
        self.r = True
        return self.r

    def merge(self):
        self.m = True
        return self.m