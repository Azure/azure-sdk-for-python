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
from typing import TYPE_CHECKING, Iterator
from ._utils import ResponseType, ReturnType
from ._paging_method_handler import _PagingMethodHandler

from ..exceptions import AzureError

if TYPE_CHECKING:
    from typing import (
        Callable,
        Iterable,
        Optional,
        Tuple,
    )
    from ._paging_method import _PagingMethodABC

_LOGGER = logging.getLogger(__name__)

class PageIterator(Iterator[Iterator[ReturnType]]):
    def __init__(
        self,
        get_next=None,  # type: Callable[[Optional[str]], ResponseType]
        extract_data=None,  # type: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]]
        continuation_token=None,  # type: Optional[str]
        **kwargs
    ):
        """Return an iterator of pages.
        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
        """
        paging_method = kwargs.pop("_paging_method", None)
        if get_next or extract_data:
            if paging_method:
                raise ValueError(
                    "You can't pass in both a paging method and a callback for get_next or extract_data. "
                    "We recommend you only pass in a paging method, since passing in callbacks is legacy."
                )
            if not (get_next and extract_data):
                raise ValueError(
                    "If you are passing in callbacks (this is legacy), you have to pass in callbacks for both "
                    "get_next and extract_data. We recommend you just pass in a paging method instead though."
                )
        if not extract_data or not get_next:
            handler = _PagingMethodHandler(paging_method, **kwargs)
        self._extract_data = extract_data or handler.extract_data
        self._get_next = get_next or handler.get_next
        self.continuation_token = continuation_token
        self._response = None  # type: Optional[ResponseType]
        self._current_page = None  # type: Optional[Iterable[ReturnType]]
        self._did_a_call_already = False
        self._operation_config = kwargs

    def __iter__(self):
        """Return 'self'."""
        return self

    def __next__(self):
        # type: () -> Iterator[ReturnType]
        if self._did_a_call_already and not self.continuation_token:
            raise StopIteration("End of paging")
        try:
            self._response = self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise
        self._did_a_call_already = True
        self.continuation_token, self._current_page = self._extract_data(self._response)
        return iter(self._current_page)

    next = __next__  # Python 2 compatibility.
