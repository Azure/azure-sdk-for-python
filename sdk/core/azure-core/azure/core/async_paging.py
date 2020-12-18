# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import collections.abc
import logging
from typing import (
    Iterable,
    AsyncIterator,
    TypeVar,
    Callable,
    Tuple,
    Optional,
    Awaitable,
)
from .pipeline import PipelineResponse
from .pipeline._tools_async import await_result as _await_result

from .exceptions import AzureError
from .paging import PagingMethodABC, _PagingMethodHandlerBase


_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

__all__ = [
    "AsyncPageIterator",
    "AsyncItemPaged"
]

class _AsyncPagingMethodHandler(_PagingMethodHandlerBase):

    async def _make_call(self, request):
        return await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )

    async def _do_initial_call(self):
        if isinstance(self._initial_state, PipelineResponse):
            return self._initial_state
        return await self._make_call(self._initial_state)

    async def get_next(self, continuation_token):
        if not continuation_token:
            response = await self._do_initial_call()
        else:
            request = self._paging_method.get_next_request(continuation_token, self._initial_request, self._client)
            response = await self._make_call(request)
        return self._handle_response(continuation_token, response)

    def extract_data(self, pipeline_response):
        continuation_token, list_of_elem = self._extract_data_helper(pipeline_response)
        return continuation_token, AsyncList(list_of_elem)

class AsyncList(AsyncIterator[ReturnType]):
    def __init__(self, iterable: Iterable[ReturnType]) -> None:
        """Change an iterable into a fake async iterator.

        Coul be useful to fill the async iterator contract when you get a list.

        :param iterable: A sync iterable of T
        """
        # Technically, if it's a real iterator, I don't need "iter"
        # but that will cover iterable and list as well with no troubles created.
        self._iterator = iter(iterable)

    async def __anext__(self) -> ReturnType:
        try:
            return next(self._iterator)
        except StopIteration as err:
            raise StopAsyncIteration() from err


class AsyncPageIterator(AsyncIterator[AsyncIterator[ReturnType]]):
    def __init__(
        self,
        get_next: Optional[Callable[
            [Optional[str]], Awaitable[ResponseType]
        ]] = None,
        extract_data: Optional[Callable[
            [ResponseType], Awaitable[Tuple[str, AsyncIterator[ReturnType]]]
        ]] = None,
        continuation_token: Optional[str] = None,
        paging_method: Optional[PagingMethodABC] = None,
        **kwargs
    ) -> None:
        """Return an async iterator of pages.

        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
        :param paging_method: Preferred way of paging. Pass in a sansio paging method, to tell the iterator
         how to make requests, and deserialize responses. When passing in paging_method, do not pass in
         callables for get_next and extract_data.
        :type paging_method: ~azure.core.paging_method.PagingMethodABC
        """
        if get_next or extract_data:
            if paging_method:
                raise ValueError(
                    "You can't pass in both a paging method and a callback for get_next or extract_data. "
                    "We recommend you only pass in a paging method, since passing in callbacks is legacy."
                )
            if not get_next and extract_data:
                raise ValueError(
                    "If you are passing in callbacks (this is legacy), you have to pass in callbacks for both "
                    "get_next and extract_data. We recommend you just pass in a paging method instead though."
                )
        self._paging_method = paging_method
        handler = _AsyncPagingMethodHandler(paging_method, **kwargs)
        self._extract_data = extract_data or handler.extract_data
        self._get_next = get_next or handler.get_next

        self.continuation_token = continuation_token
        self._response = None  # type: Optional[ResponseType]
        self._current_page = None  # type: Optional[Iterable[ReturnType]]
        self._did_a_call_already = False
        self._operation_config = kwargs

    async def __anext__(self):
        if self._did_a_call_already and not self.continuation_token:
            raise StopAsyncIteration("End of paging")
        try:
            self._response = await self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise
        self._did_a_call_already = True
        self.continuation_token, self._current_page = await _await_result(self._extract_data, self._response)

        if isinstance(self._current_page, collections.abc.Iterable):
            self._current_page = AsyncList(self._current_page)
        return self._current_page


class AsyncItemPaged(AsyncIterator[ReturnType]):
    def __init__(self, *args, **kwargs) -> None:
        """Return an async iterator of items.

        args and kwargs will be passed to the AsyncPageIterator constructor directly,
        except page_iterator_class
        """
        self._args = args
        self._kwargs = kwargs
        self._page_iterator = (
            None
        )  # type: Optional[AsyncIterator[AsyncIterator[ReturnType]]]
        self._page = None  # type: Optional[AsyncIterator[ReturnType]]
        self._page_iterator_class = self._kwargs.pop(
            "page_iterator_class", AsyncPageIterator
        )

    def by_page(
        self,
        continuation_token: Optional[str] = None,
    ) -> AsyncIterator[AsyncIterator[ReturnType]]:
        """Get an async iterator of pages of objects, instead of an async iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :returns: An async iterator of pages (themselves async iterator of objects)
        """
        return self._page_iterator_class(
            *self._args, **self._kwargs, continuation_token=continuation_token
        )

    async def __anext__(self) -> ReturnType:
        if self._page_iterator is None:
            self._page_iterator = self.by_page()
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
