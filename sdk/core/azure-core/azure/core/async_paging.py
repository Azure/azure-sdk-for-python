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
from .paging import _LegacyPagingMethod

from .exceptions import AzureError


_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

__all__ = [
    "AsyncPageIterator",
    "AsyncItemPaged"
]

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
        *args,
        get_next: Optional[Callable[
            [Optional[str]], Awaitable[ResponseType]
        ]] = None,
        extract_data: Optional[Callable[
            [ResponseType], Awaitable[Tuple[str, AsyncIterator[ReturnType]]]
        ]] = None,
        continuation_token: Optional[str] = None,
        paging_method=None,
        **kwargs,
    ) -> None:
        """Return an async iterator of pages.

        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
        """
        self._initial_request = kwargs.pop("initial_request", None)
        self._initial_response = kwargs.pop("initial_response", None)
        if self._initial_response:
            self._initial_request = self._initial_response.http_response.request

        if get_next or extract_data:
            if paging_method:
                raise ValueError(
                    "You can't pass in both a paging method and a callback for get_next or extract_data. "
                    "We recomment you only pass in a paging method, since passing in callbacks is legacy."
                )
            self._paging_method = _LegacyPagingMethod(get_next, extract_data)
        else:
            if not self._initial_request and not self._initial_response:
                raise ValueError(
                    "You must either supply the initial request the paging method must call, or provide "
                    "the initial response"
                )
            self._paging_method = paging_method
            self._paging_method.initialize(*args, **kwargs)
        self.continuation_token = continuation_token
        self._response = None  # type: Optional[ResponseType]
        self._current_page = None  # type: Optional[Iterable[ReturnType]]

    async def __anext__(self):
        if self._paging_method.finished(self.continuation_token):
            raise StopAsyncIteration("End of paging")
        try:
            try:
                self._response = await self._paging_method.get_page(self.continuation_token, self._initial_request)
            except TypeError:
                # legacy doesn't support passing initial request into get_page
                self._response = await self._paging_method.get_page(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self.continuation_token, self._current_page = await self._paging_method.extract_data(
            self._response
        )

        # If current_page was a sync list, wrap it async-like
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
