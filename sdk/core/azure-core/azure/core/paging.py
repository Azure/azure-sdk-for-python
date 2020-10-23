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
import abc
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
from enum import Enum
from .paging_algorithm import (
    PagingAlgorithmIfSeparateNextOperation,
    PagingAlgorithmContinuationTokenAsNextLink,
    PagingAlgorithm,
)
from .exceptions import HttpResponseError

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore


_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

class PageIterator(PageIteratorABC):
    def __init__(
        self,
        get_next=None,  # type: Callable[[Optional[str]], ResponseType]
        extract_data=None,  # type: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]]
        continuation_token=None,  # type: Optional[str]
        paging_algorithms=None,
        paging_options=None,
        path_format_arguments=None,
        **kwargs
    ):
        """Return an iterator of pages.

        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
        """
        self._paging_algorithms = paging_algorithms or [
            PagingAlgorithmIfSeparateNextOperation(),
            PagingAlgorithm(),
            PagingAlgorithmContinuationTokenAsNextLink(),
        ]
        self._client = None
        self._initial_call = None
        self._initial_response = None
        self._did_a_call_already = False
        self._response = None  # type: Optional[ResponseType]
        self._current_page = None  # type: Optional[Iterable[ReturnType]]
        self._prepare_request_to_separate_next_operation = None
        self._paging_options = paging_options
        self._kwargs = kwargs
        self._algorithm = None
        self._continuation_token = None
        self._path_format_arguments = path_format_arguments

        # these are for back-compat
        self._get_next = get_next
        self._extract_data = extract_data


    def initialize(
        self,
        client,
        initial_call,
        extract_data,
        prepare_request_to_separate_next_operation=None
    ):
        """
        initial_call takes in either a request if paging hasn't started yet, or an initial response
        (in the case of LRO and paging, the initial response is the pipeline response from the last LRO poll)
        prepare_next_requests is only used if there is a separate next operation defined in the swagger.
        """
        self._client = client
        self._extract_data = extract_data
        self._initial_call = initial_call
        self._prepare_request_to_separate_next_operation = prepare_request_to_separate_next_operation

        return self

    def get_next_page(self):
        next_link = self._algorithm.get_next_link()
        if self._path_format_arguments:
            next_link = self._client.format_url(next_link, **self._path_format_arguments)
        request_params = self._algorithm.get_request_parameters()
        request = self._client.get(next_link, **request_params)
        return self._client._pipeline.run(request, stream=False)


    def finished(self):
        if self._continuation_token is None and self._did_a_call_already:
            return True
        return False

    def __iter__(self):
        """Return 'self'."""
        return self

    def _set_algorithm(self):
        for paging_algorithm in self._paging_algorithms:
            if paging_algorithm.can_page(self):
                return paging_algorithm
        raise BadResponse("Unable to find algorithm for paging.")

    def get_initial_page(self):
        response = self._client._pipeline.run(self._initial_call, stream=False)
        return response

    def __next__(self):
        # type: () -> Iterator[ReturnType]
        if self.finished():
            raise StopIteration("End of paging")

        if not self._did_a_call_already:
            response = self.get_initial_page()
            if not self._algorithm:
                self._algorithm = self._set_algorithm()
            self._algorithm.set_initial_state(response)
        else:
            response = self.get_next_page()

        code = response.http_response.status_code
        if not (200 <= code <= 299):
            raise HttpResponseError(response=response.http_response)


        self._continuation_token, self._current_page = self._extract_data(response)

        self._did_a_call_already = True

        if not self.finished():
            self._algorithm.update_state(self._continuation_token)

        return iter(self._current_page)

    next = __next__  # Python 2 compatibility.

class PageIteratorWithInitialResponse(PageIterator):
    def get_initial_page(self):
        return self._initial_call

class PageIteratorWithContinuationToken(PageIterator):

    def _add_continuation_token(self):
        set_continuation_token = False
        continuation_token_input_parameter = self._paging_options[_PagingOption.TOKEN_INPUT_PARAMETER]
        request_params = self._algorithm.get_request_parameters()
        for api_parameter_type, api_parameters in request_params:
            for param_name, param_value in api_parameters.items():
                if param_name.lower() == continuation_token_input_parameter.lower():
                    request_params[api_parameter_type][param_name] = self._continuation_token
                    set_continuation_token = True
                    break

        if not set_continuation_token:
            raise ValueError(
                "The value provided in paging_options for the input parameter that accepts "
                "the continuation token {} is not present in the API parameters".format(self._paging_options[_PagingOption.TOKEN_INPUT_PARAMETER])
            )
        return request_params


    def get_next_page(self):
        next_link = self._algorithm.get_next_link()
        if self._path_format_arguments:
            next_link = self._client.format_url(next_link, **self._path_format_arguments)
        request_params = self._add_continuation_token()
        request = self._client.get(next_link, **request_params)
        return self._client._pipeline.run(request, stream=False)

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
        self._paging_method = self._kwargs.pop("paging_method", None)
        if not self._paging_method:
            self._page_iterator_class = self._kwargs.pop(
                "page_iterator_class", PageIterator
            )
        else:
            self._page_iterator_class = None

    def by_page(self, continuation_token=None):
        # type: (Optional[str]) -> Iterator[Iterator[ReturnType]]
        """Get an iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :returns: An iterator of pages (themselves iterator of objects)
        """
        if self._paging_method:
            return self._paging_method.initialize(*self._args, **self._kwargs)
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
