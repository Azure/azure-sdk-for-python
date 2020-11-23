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
import functools
from typing import (  # pylint: disable=unused-import
    Callable,
    Optional,
    TypeVar,
    Iterator,
    Iterable,
    Tuple,
)
import logging

from .exceptions import AzureError, map_error, HttpResponseError


_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

def _extract_data(pipeline_response, paging_method):
    deserialized = paging_method._deserialize_output(pipeline_response)  # pylint: disable=protected-access
    list_of_elem = paging_method.get_list_elements(pipeline_response, deserialized)  # type: Iterable[ReturnType]
    list_of_elem = paging_method.mutate_list(pipeline_response, list_of_elem)
    continuation_token = paging_method.get_continuation_token(pipeline_response, deserialized)
    return continuation_token, list_of_elem

def _get_page(continuation_token, paging_method, initial_response):
    if not continuation_token:
        if initial_response:
            return initial_response
        request = paging_method._initial_request  # pylint: disable=protected-access
    else:
        request = paging_method.get_next_request(continuation_token)

    response = paging_method._client._pipeline.run(  # pylint: disable=protected-access
        request, stream=False, **paging_method._operation_config  # pylint: disable=protected-access
    )

    http_response = response.http_response
    status_code = http_response.status_code
    if status_code < 200 or status_code >= 300:
        map_error(status_code=status_code, response=http_response, error_map=paging_method._error_map)  # pylint: disable=protected-access
        error = HttpResponseError(response=http_response)
        error.continuation_token = continuation_token
        raise error
    if "request_id" not in paging_method._operation_config:  # pylint: disable=protected-access
        paging_method._operation_config["request_id"] = response.http_response.request.headers["x-ms-client-request-id"]  # pylint: disable=protected-access
    return response

class PageIterator(Iterator[Iterator[ReturnType]]):
    def __init__(
        self,
        get_next=None,  # type: Callable[[Optional[str]], ResponseType]
        extract_data=None,  # type: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]]
        continuation_token=None,  # type: Optional[str]
        paging_method=None,
        **kwargs
    ):
        """Return an iterator of pages.
        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
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
        self._extract_data = extract_data or functools.partial(_extract_data, paging_method=paging_method)
        self._get_page = get_next or functools.partial(
            _get_page, paging_method=paging_method, initial_response=kwargs.get("initial_response")
        )
        self._paging_method = paging_method

        if self._paging_method:
            self._paging_method.initialize(**kwargs)
        self.continuation_token = continuation_token
        self._response = None  # type: Optional[ResponseType]
        self._current_page = None  # type: Optional[Iterable[ReturnType]]
        self._did_a_call_already = False
        self._operation_config = kwargs

    def _finished(self, did_a_call_already, continuation_token):
        if self._paging_method:
            return self._paging_method.finished(did_a_call_already, continuation_token)
        return did_a_call_already and not continuation_token

    def __iter__(self):
        """Return 'self'."""
        return self

    def __next__(self):
        # type: () -> Iterator[ReturnType]
        if self._finished(self._did_a_call_already, self.continuation_token):
            raise StopIteration("End of paging")
        try:
            self._response = self._get_page(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise
        self._did_a_call_already = True
        self.continuation_token, self._current_page = self._extract_data(self._response)
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
        self._page_iterator = None
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
        if self._page_iterator is None:
            self._page_iterator = itertools.chain.from_iterable(self.by_page())
        return next(self._page_iterator)

    next = __next__  # Python 2 compatibility.
