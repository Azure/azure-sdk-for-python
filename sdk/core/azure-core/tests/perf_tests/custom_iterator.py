# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import (
    Any,
    Callable,
)
from azure.core.paging import PageIterator
from azure.core.async_paging import AsyncPageIterator

NEXT_PARTITION_KEY = 'x-ms-continuation-NextPartitionKey'
NEXT_ROW_KEY = 'x-ms-continuation-NextRowKey'


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

    def _get_next_cb(self, continuation_token, **kwargs):  # pylint: disable=inconsistent-return-statements
        return self._command()

    def _extract_data_cb(self, response):
        return None, response.json()['value']


class AsyncCustomIterator(AsyncPageIterator):
    def __init__(
            self,
            command,
            max_results=None,
            continuation_token=None,
        ):
        super(AsyncCustomIterator, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command

    async def _get_next_cb(self, continuation_token):
        return await self._command() 

    async def _extract_data_cb(self, response):
        return None, response.json()['value']
