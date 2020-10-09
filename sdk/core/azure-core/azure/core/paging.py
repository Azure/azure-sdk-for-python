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
from .paging_operation import PagingOperation, PagingOperationWithSeparateNextOperation

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore


_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

class _PagingOption(str, Enum):
    """Known paging options from Swagger."""

    TOKEN_INPUT_PARAMETER = "continuation-token-input-parameter"  # for token paging, which parameter will hold continuation token

class BadStatus(Exception):
    pass


class BadResponse(Exception):
    pass


class OperationFailed(Exception):
    pass

def _raise_if_bad_http_status_and_method(response):
    # type: (ResponseType) -> None
    """Check response status code is valid.

    Must be 200, 201, 202, or 204.

    :raises: BadStatus if invalid status.
    """
    code = response.status_code
    if code in {200, 201, 202, 204}:
        return
    raise BadStatus(
        "Invalid return status {!r} for {!r} operation".format(
            code, response.request.method
        )
    )

class PageIteratorABC(ABC):

    def initialize(
        self, client, initial_request, extract_data
    ):
        raise NotImplementedError("This method needs to be implemented")

    def get_next_page(self):
        raise NotImplementedError("This method needs to be implemented")

    def finished(self):
        raise NotImplementedError("This method needs to be implemented")

    def __iter__(self):
        raise NotImplementedError("This method needs to be implemented")

    def __next__(self):
        raise NotImplementedError("This method needs to be implemented")



class PageIterator(PageIteratorABC):
    def __init__(
        self,
        get_next=None,  # type: Callable[[Optional[str]], ResponseType]
        extract_data=None,  # type: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]]
        continuation_token=None,  # type: Optional[str]
        paging_algorithms=None,
        paging_options=None,
        path_format_arguments=None,
        **operation_config
    ):
        """Return an iterator of pages.

        :param get_next: Callable that take the continuation token and return a HTTP response
        :param extract_data: Callable that take an HTTP response and return a tuple continuation token,
         list of ReturnType
        :param str continuation_token: The continuation token needed by get_next
        """
        self._paging_algorithms = paging_algorithms or [
            PagingOperationWithSeparateNextOperation(), PagingOperation()
        ]
        self._client = None
        self._initial_request = None
        self._did_a_call_already = False
        self._response = None  # type: Optional[ResponseType]
        self._current_page = None  # type: Optional[Iterable[ReturnType]]
        self._path_format_arguments = path_format_arguments
        self._operation_config = operation_config
        self._paging_options = paging_options
        self._paging_algorithms = paging_algorithms

        # these are for back-compat
        self._get_next = get_next
        self._extract_data = extract_data


    def initialize(
        self, client, initial_request, extract_data
    ):
        self._client = client
        self._extract_data = extract_data
        self._initial_request = initial_request
        self._next_link = None

        # TODO: how to pass in next_link_operation_url
        for operation in self._paging_algorithms:
            if operation.can_page(**self._operation_config):
                self._operation = operation(**self._operation_config)
                break
        else:
            raise BadResponse("Unable to find way to retrieve next link.")

    def get_next_page(self, next_link):
        request = self._client.get(next_link)
        if self._path_format_arguments:
            request = self._client.format_url(status_link, **self._path_format_arguments)
        return self._client._pipeline.run(
            request, stream=False, **self._operation.operation_config
        )

    def finished(self):
        if self._operation.next_link is None and self._did_a_call_already:
            return True
        return False

    def __iter__(self):
        """Return 'self'."""
        return self

    def _make_initial_call(self):
        response = self._client._pipeline.run(self._initial_request)

        try:
            _raise_if_bad_http_status_and_method(initial_pipeline_response.http_response)
        except BadStatus as err:
            raise HttpResponseError(response=initial_pipeline_response.http_response, error=err)
        except BadResponse as err:
            raise HttpResponseError(
                response=initial_pipeline_response.http_response, message=str(err), error=err
            )
        except OperationFailed as err:
            raise HttpResponseError(response=initial_pipeline_response.http_response, error=err)
        return response

    def __next__(self):
        # type: () -> Iterator[ReturnType]
        if self.finished():
            raise StopIteration("End of paging")

        if not self._did_a_call_already:
            response = self._make_initial_call()
            self._operation.set_initial_state(response)
        else:
            next_link_url = self._operation.get_next_link()
            response = self.get_next_page(next_link_url)

        self._did_a_call_already = True
        self._next_link, self._current_page = self._extract_data(response)
        self._operation.update_state(self._next_link)

        return iter(self._current_page)

    next = __next__  # Python 2 compatibility.

class PageIteratorNextLinkTemplate(PageIterator):

    def get_next_page(self, next_link):
        request = self._client.get(next_link)
        if self._path_format_arguments:
            request = self._client.format_url(status_link, **self._path_format_arguments, 'nextLink'=next_link)
        return self._client._pipeline.run(
            request, stream=False, **self._operation.operation_config
        )


class PageIteratorWithContinuationToken(PageIterator):

    def _set_continuation_token(self):
        set_continuation_token = False
        continuation_token_input_parameter = self._paging_options[_PagingOption.TOKEN_INPUT_PARAMETER]
        for api_parameter_type, api_parameters in self._operation.operation_config.items():
            for param_name, param_value in api_parameters.items():
                if param_name.lower() == continuation_token_input_parameter.lower()
                    self._operation.operation_config[api_parameter_type][param_name] = self._next_link
                    set_continuation_token = True
                    break

        if not set_continuation_token:
            raise ValueError(
                "The value provided in paging_options for the input parameter that accepts "
                "the continuation token {} is not present in the API parameters".format(self._paging_options[_PagingOption.TOKEN_INPUT_PARAMETER])
            )


    def get_next_page(self, next_link):
        request = self._client.get(next_link)
        if self._path_format_arguments:
            request = self._client.format_url(status_link, **self._path_format_arguments, 'nextLink'=next_link)
        self._set_continuation_token()
        return self._client._pipeline.run(
            request, stream=False, **self._operation.operation_config
        )

    def __next__(self):
        # type: () -> Iterator[ReturnType]
        if self.finished():
            raise StopIteration("End of paging")

        if not self._did_a_call_already:
            response = self._make_initial_call()
            self._operation.set_initial_state(response)
        else:
            next_link_url = self._operation.get_next_link()
            response = self.get_next_page(next_link_url)

        self._did_a_call_already = True
        self._next_link, self._current_page = self._extract_data(response)

        return iter(self._current_page)

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
        self._page_iterator = self._kwargs.pop("page_iterator", None)
        if not self._page_iterator:
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
        if self._page_iterator:
            return self._page_iterator.initialize(*self._args, **self._kwargs)
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
