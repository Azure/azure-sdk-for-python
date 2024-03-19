# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import (
    Any,
    Callable,
)
from corehttp.paging import PageIterator, AsyncPageIterator

NEXT_PARTITION_KEY = "x-ms-continuation-NextPartitionKey"
NEXT_ROW_KEY = "x-ms-continuation-NextRowKey"


class MockResponse:
    pass


class CustomIterator(PageIterator):
    def __init__(self, command: Callable, **kwargs: Any) -> None:
        super(CustomIterator, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )
        self._command = command
        self.page_size = kwargs.get("page_size")

    def _get_next_cb(self, continuation_token, **kwargs):  # pylint: disable=inconsistent-return-statements
        if not continuation_token:
            next_partition_key = None
            next_row_key = None
        else:
            next_partition_key = continuation_token.get("PartitionKey")
            next_row_key = continuation_token.get("RowKey")

        return self._command(top=self.page_size, next_partition_key=next_partition_key, next_row_key=next_row_key)

    def _extract_data_cb(self, response):
        next_entity = None
        if response.headers and (NEXT_PARTITION_KEY in response.headers or NEXT_ROW_KEY in response.headers):
            next_entity = {
                "PartitionKey": response.headers[NEXT_PARTITION_KEY],
                "RowKey": response.headers[NEXT_ROW_KEY],
            }

        return next_entity, response.json()["value"]


class AsyncCustomIterator(AsyncPageIterator):
    def __init__(
        self,
        command,
        page_size=None,
        continuation_token=None,
    ):
        super(AsyncCustomIterator, self).__init__(
            get_next=self._get_next_cb, extract_data=self._extract_data_cb, continuation_token=continuation_token or ""
        )
        self._command = command
        self.page_size = page_size

    async def _get_next_cb(self, continuation_token, **kwargs):  # pylint: disable=inconsistent-return-statements
        if not continuation_token:
            next_partition_key = None
            next_row_key = None
        else:
            next_partition_key = continuation_token.get("PartitionKey")
            next_row_key = continuation_token.get("RowKey")

        return await self._command(top=self.page_size, next_partition_key=next_partition_key, next_row_key=next_row_key)

    async def _extract_data_cb(self, response):
        next_entity = None
        if response.headers and (NEXT_PARTITION_KEY in response.headers or NEXT_ROW_KEY in response.headers):
            next_entity = {
                "PartitionKey": response.headers[NEXT_PARTITION_KEY],
                "RowKey": response.headers[NEXT_ROW_KEY],
            }
        return next_entity, response.json()["value"]
