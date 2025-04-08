# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Optional, Callable, Any
from azure.core.exceptions import HttpResponseError
from azure.core.async_paging import AsyncPageIterator

from .._models import TableItem, _extract_continuation_token, _return_context_and_deserialized
from .._decoder import TableEntityDecoder
from .._error import _process_table_error
from .._constants import NEXT_PARTITION_KEY, NEXT_TABLE_NAME, NEXT_ROW_KEY


class TablePropertiesPaged(AsyncPageIterator):
    """An async iterable of Table properties."""

    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    filter: Optional[str]
    """The filter to apply to results."""
    continuation_token: Optional[str]
    """The continuation token needed by get_next()."""

    def __init__(self, command, **kwargs):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )
        self._command = command
        self._headers = None
        self._response = None
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self._location_mode = None

    async def _get_next_cb(self, continuation_token, **kwargs):
        try:
            return await self._command(
                top=self.results_per_page,
                filter=self.filter,
                next_table_name=continuation_token or None,
                cls=kwargs.pop("cls", None) or _return_context_and_deserialized,
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    async def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [TableItem(t.table_name) for t in self._response.value]
        return self._headers[NEXT_TABLE_NAME] or None, props_list


class TableEntityPropertiesPaged(AsyncPageIterator):
    """An async iterable of TableEntity properties."""

    table: str
    """The name of the table."""
    results_per_page: Optional[int]
    """The maximum number of results retrieved per API call."""
    filter: Optional[str]
    """The filter to apply to results."""
    select: Optional[str]
    """The select filter to apply to results."""
    continuation_token: Optional[str]
    """The continuation token needed by get_next()."""

    def __init__(
        self,
        command: Callable,
        table: str,
        *,
        decoder: TableEntityDecoder,
        **kwargs: Any,
    ) -> None:
        super(TableEntityPropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )
        self._command = command
        self._headers = None
        self._response = None
        self._location_mode = None
        self.table = table
        self.results_per_page = kwargs.get("results_per_page")
        self.filter = kwargs.get("filter")
        self.select = kwargs.get("select")
        self._decoder = decoder

    async def _get_next_cb(self, continuation_token, **kwargs):
        next_partition_key, next_row_key = _extract_continuation_token(continuation_token)
        try:
            return await self._command(
                top=self.results_per_page,
                select=self.select,
                filter=self.filter,
                next_row_key=next_row_key,
                next_partition_key=next_partition_key,
                table=self.table,
                cls=kwargs.pop("cls", _return_context_and_deserialized),
                use_location=self._location_mode,
            )
        except HttpResponseError as error:
            _process_table_error(error)

    async def _extract_data_cb(self, get_next_return):
        self._location_mode, self._response, self._headers = get_next_return
        props_list = [self._decoder(t) for t in self._response.value]
        next_entity = {}
        if self._headers[NEXT_PARTITION_KEY] or self._headers[NEXT_ROW_KEY]:
            next_entity = {
                "PartitionKey": self._headers[NEXT_PARTITION_KEY],
                "RowKey": self._headers[NEXT_ROW_KEY],
            }
        return next_entity or None, props_list
