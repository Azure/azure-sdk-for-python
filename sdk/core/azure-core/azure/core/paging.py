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
from typing import (
    Dict,
    Any,
    List,
    Callable,
    Optional,
    TypeVar,
    Iterator,
    Tuple,
    Type,
)  # pylint: disable=unused-import
import logging


_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")


class PageIterator(Iterator[Iterator[ReturnType]]):
    def __init__(self, get_next, extract_data, continuation_token=None):
        # type: (Callable[[str], ResponseType], Callable[[ResponseType], Tuple[str, Iterator[ReturnType]]], Optional[str]) -> None
        """Return an iterator of pages.

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

    def __iter__(self):
        """Return 'self'."""
        return self

    def __next__(self):
        if self.continuation_token is None and self._did_a_call_already:
            raise StopIteration("End of paging")

        self._response = self._get_next(self.continuation_token)
        self._did_a_call_already = True

        self.continuation_token, self._current_page = self._extract_data(self._response)
        return self._current_page

    next = __next__  # Python 2 compatibility.


class ItemPaged(Iterator[ReturnType]):
    def __init__(self, get_next, extract_data, page_iterator_class=PageIterator):
        # type: (Callable[[str], ResponseType], Callable[[ResponseType], Tuple[str, Iterator[ReturnType]]], Type) -> None
        """Return an iterator of items.

        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param page_iterator_class: The type to use for page iterator
        """
        self._get_next = get_next
        self._extract_data = extract_data
        self._page_iterator = None
        self._page = None
        self._page_iterator_class = page_iterator_class

    def by_page(self, continuation_token=None):
        # type: (Optional[str]) -> Iterator[Iterator[ReturnType]]
        return self._page_iterator_class(
            get_next=self._get_next,
            extract_data=self._extract_data,
            continuation_token=continuation_token,
        )

    def __iter__(self):
        """Return 'self'."""
        return self

    def __next__(self):
        if self._page_iterator is None:
            self._page_iterator = self.by_page()
            return next(self)
        if self._page is None:
            # Let it raise StopIteration
            self._page = next(self._page_iterator)
            return next(self)
        try:
            return next(self._page)
        except StopIteration:
            self._page = None
            return next(self)

    next = __next__  # Python 2 compatibility.
