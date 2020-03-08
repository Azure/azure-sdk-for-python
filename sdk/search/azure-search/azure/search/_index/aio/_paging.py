# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator, ReturnType
from .._generated.models import SearchRequest
from .._paging import (
    convert_search_result,
    pack_continuation_token,
    unpack_continuation_token,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union


class AsyncSearchItemPaged(AsyncItemPaged):
    pass


class AsyncSearchPageIterator(AsyncPageIterator[ReturnType]):
    def __init__(self, client, initial_query, kwargs, continuation_token=None):
        super(AsyncSearchPageIterator, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token,
        )
        self._client = client
        self._initial_query = initial_query
        self._kwargs = kwargs

    async def _get_next_cb(self, continuation_token):
        if continuation_token is None:
            return await self._client.documents.search_post(
                search_request=self._initial_query.request, **self._kwargs
            )

        _next_link, next_page_request = unpack_continuation_token(continuation_token)

        return await self._client.documents.search_post(
            search_request=next_page_request
        )

    async def _extract_data_cb(self, response):  # pylint:disable=no-self-use
        continuation_token = pack_continuation_token(response)

        results = [convert_search_result(r) for r in response.results]

        return continuation_token, results
