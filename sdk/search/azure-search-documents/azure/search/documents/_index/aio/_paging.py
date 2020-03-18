# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Union

from azure.core.async_paging import AsyncItemPaged, AsyncPageIterator, ReturnType
from .._generated.models import SearchRequest
from .._paging import (
    convert_search_result,
    pack_continuation_token,
    unpack_continuation_token,
)


class AsyncSearchItemPaged(AsyncItemPaged[ReturnType]):
    def __init__(self, *args, **kwargs):
        super(AsyncSearchItemPaged, self).__init__(*args, **kwargs)
        self._first_page_iterator_instance = None

    async def __anext__(self) -> ReturnType:
        if self._page_iterator is None:
            self._page_iterator = self.by_page()
            self._first_page_iterator_instance = self._page_iterator
            return await self.__anext__()
        if self._page is None:
            # Let it raise StopAsyncIteration
            self._page = await self._page_iterator.__anext__()
            return await self.__anext__()
        try:
            return await self._page.__anext__()
        except StopAsyncIteration:
            self._page = None
            return await self.__anext__()

    def _first_iterator_instance(self):
        if self._first_page_iterator_instance is None:
            self._page_iterator = self.by_page()
            self._first_page_iterator_instance = self._page_iterator
        return self._first_page_iterator_instance

    async def get_facets(self) -> Union[dict, None]:
        """Return any facet results if faceting was requested.

        """
        return await self._first_iterator_instance().get_facets()

    async def get_coverage(self):
        # type: () -> float
        """Return the covereage percentage, if `minimum_coverage` was
        specificied for the query.

        """
        return await self._first_iterator_instance().get_coverage()

    async def get_count(self):
        # type: () -> float
        """Return the count of results if `include_total_result_count` was
        set for the query.

        """
        return await self._first_iterator_instance().get_count()


# The pylint error silenced below seems spurious, as the inner wrapper does, in
# fact, become a method of the class when it is applied.
def _ensure_response(f):
    # pylint:disable=protected-access
    async def wrapper(self, *args, **kw):
        if self._current_page is None:
            self._response = await self._get_next(self.continuation_token)
            self.continuation_token, self._current_page = await self._extract_data(
                self._response
            )
        return await f(self, *args, **kw)

    return wrapper


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
        self._facets = None

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

    @_ensure_response
    async def get_facets(self):
        facets = self._response.facets
        if facets is not None and self._facets is None:
            self._facets = {k: [x.as_dict() for x in v] for k, v in facets.items()}
        return self._facets

    @_ensure_response
    async def get_coverage(self):
        return self._response.coverage

    @_ensure_response
    async def get_count(self):
        return self._response.count
