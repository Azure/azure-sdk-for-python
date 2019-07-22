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
import logging
from typing import Iterator, AsyncIterator, TypeVar, Callable, Tuple, List, Optional, Coroutine

from .pipeline.transport import HttpResponse

_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")


class AsyncList(AsyncIterator[ReturnType]):
    def __init__(
        self,
        iterator: Iterator[ReturnType]
    ) -> None:
        """Change an iterator into a fake async iterator.

        Coul be useful to fill the async iterator contract when you get a list.

        :param iterator: A sync iterator of T
        """
        # Technically, if it's a real iterator, I don't need "iter"
        # but that will cover iterable and list as well with no troubles created.
        self._iterator = iter(iterator)

    async def __anext__(self) -> ReturnType:
        try:
            return next(self._iterator)
        except StopIteration as err:
            raise StopAsyncIteration() from err

class AsyncPageIterator(AsyncIterator[AsyncIterator[ReturnType]]):
    def __init__(
        self,
        get_next: Callable[[str], HttpResponse],
        extract_data: Callable[[HttpResponse], Tuple[str, AsyncIterator[ReturnType]]],
        continuation_token: Optional[str] = None
    ) -> None:
        """Return an async iterator of pages.

        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
        """
        self._get_next = get_next
        self._extract_data = extract_data
        self.continuation_token = continuation_token
        self._did_a_call_already = False
        self._response = None
        self._current_page = None

    async def __anext__(self):
        if self.continuation_token is None and self._did_a_call_already:
            raise StopAsyncIteration("End of paging")

        self._response = await self._get_next(self.continuation_token)
        self._did_a_call_already = True

        self.continuation_token, self._current_page = await self._extract_data(self._response)
        return self._current_page


class AsyncItemPaged(AsyncIterator[ReturnType]):
    def __init__(
        self,
        get_next: Callable[[str], HttpResponse],
        extract_data: Callable[[HttpResponse], Tuple[str, AsyncIterator[ReturnType]]],
    ) -> None:
        self._get_next = get_next
        self._extract_data = extract_data
        self._page_iterator = None
        self._page = None

    def by_page(self, continuation_token=None) -> AsyncPageIterator[ReturnType]:
        return AsyncPageIterator(
            get_next=self._get_next,
            extract_data=self._extract_data,
            continuation_token=continuation_token
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
