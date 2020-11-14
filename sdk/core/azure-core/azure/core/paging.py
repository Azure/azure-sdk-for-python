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
import itertools
from typing import (  # pylint: disable=unused-import
    Callable,
    Optional,
    TypeVar,
    Iterator,
    Iterable,
    Tuple,
)
import logging

_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

class _LegacyPagingMethod:
    def __init__(self, get_next, extract_data):
        if not (get_next and extract_data):
            raise ValueError(
                "You are using the legacy version of paging, but haven't provided both a get_next "
                "and extract_data. Preferably switch to the new paging with PagingMethod, but if "
                "not, please pass in the missing callback."
            )
        self._get_page = get_next
        self.extract_data = extract_data
        self.did_a_call_already = False

    def initialize(self, client, deserialize_output, next_link_name, **kwargs):
        # to pass mypy
        pass

    def finished(self, continuation_token):
        return continuation_token is None and self.did_a_call_already

    @property
    def get_page(self):
        self.did_a_call_already = True
        return self._get_page

class PageIterator(Iterator[Iterator[ReturnType]]):
    def __init__(
        self,
        *args,
        get_next=None,  # type: Callable[[Optional[str]], ResponseType]
        extract_data=None,  # type: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]]
        continuation_token=None,  # type: Optional[str]
        paging_method=None,
        **kwargs,
    ):
        """Return an iterator of pages.
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


    def __iter__(self):
        """Return 'self'."""
        return self

    def __next__(self):
        # type: () -> Iterator[ReturnType]
        if self._paging_method.finished(self.continuation_token):
            raise StopIteration("End of paging")

        try:
            self._response = self._paging_method.get_page(self.continuation_token, self._initial_request)
        except TypeError:
            # legacy doesn't support passing initial request into get_page
            self._response = self._paging_method.get_page(self.continuation_token)

        self.continuation_token, self._current_page = self._paging_method.extract_data(self._response)

        return iter(self._current_page)

    next = __next__  # Python 2 compatibility.


class ItemPaged(Iterator[ReturnType]):
    def __init__(self, *args, **kwargs):
        """Return an iterator of items.

        args and kwargs will be passed to the PageIterator constructor directly,
        except page_iterator_class
        """
        # with the newest version, I want to take in the client, initial request,
        # cb to extract data, and cb to format next link
        self._args = args
        self._kwargs = kwargs
        self._internal_page_iterator = None
        self._page_iterator_class = self._kwargs.pop(
            "page_iterator_class", PageIterator
        )

    def by_page(self, continuation_token=None):
        # type: (Optional[str]) -> Iterator[Iterator[ReturnType]]
        """Get an iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :returns: An iterator of pages (themselves iterator of objects)
        """
        return self._page_iterator_class(
            continuation_token=continuation_token, *self._args, **self._kwargs
        )

    def __repr__(self):
        return "<iterator object azure.core.paging.ItemPaged at {}>".format(hex(id(self)))

    def __iter__(self):
        """Return 'self'."""
        return self

    def __next__(self):
        if self._internal_page_iterator is None:
            self._internal_page_iterator = itertools.chain.from_iterable(self.by_page())
        return next(self._internal_page_iterator)

    next = __next__  # Python 2 compatibility.
