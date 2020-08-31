# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
from azure.core.async_paging import AsyncPageIterator

from .._deserialize import (
    _return_context_and_deserialized,
    _convert_to_entity
)
from .._models import TableItem
from .._error import _process_table_error

class TablePropertiesPaged(AsyncPageIterator):
    """An iterable of Table properties.

    :ivar: str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar: callable command: Function to retrieve the next page of items.
        call.
    :vartype: str continuation_token: An opaque continuation token.
    """

    def __init__(self, command, continuation_token=None, **kwargs):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or "",
            **kwargs
        )
        self._command = command
        self.next_table_name = None
        self._headers = None
        self.location_mode = None

    async def _get_next_cb(self, continuation_token, **kwargs):
        try:
            return await self._command(
                next_table_name=continuation_token or None,
                cls=kwargs.pop('cls', None) or _return_context_and_deserialized,
                use_location=self.location_mode
            )
        except HttpResponseError as error:
            _process_table_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response, self._headers = get_next_return
        props_list = [TableItem(t, self._headers) for t in self._response.value]
        return self._headers['x-ms-continuation-NextTableName'] or None, props_list


class TableEntityPropertiesPaged(AsyncPageIterator):
    """An iterable of TableEntity properties.

    :ivar: callable command: Function to retrieve the next page of items.
        call.
    :ivar: int results_per_page: The maximum number of results retrieved per API call.
    :ivar: Table table: The table that contains the entities
    :ivar: callable command: Function to retrieve the next page of items.
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

    async def _get_next_cb(self, continuation_token, **kwargs):
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
                cls=kwargs.pop("cls", _return_context_and_deserialized),
                use_location=self.location_mode
            )
        except HttpResponseError as error:
            _process_table_error(error)

    async def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response, self._headers = get_next_return
        props_list = [_convert_to_entity(t) for t in self._response.value]
        next_entity = {}
        if self._headers['x-ms-continuation-NextPartitionKey'] or self._headers['x-ms-continuation-NextRowKey']:
            next_entity = {'PartitionKey': self._headers['x-ms-continuation-NextPartitionKey'],
                           'RowKey': self._headers['x-ms-continuation-NextRowKey']}
        return next_entity or None, props_list
