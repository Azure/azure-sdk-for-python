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
import logging
from abc import ABCMeta
from typing import TYPE_CHECKING, Iterator, TypeVar
from six import add_metaclass

from .exceptions import (
    map_error,
    AzureError,
    HttpResponseError,
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError
)

from .pipeline import PipelineResponse

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Dict,
        Optional,
        Iterable,
        Tuple,
    )
    from .pipeline.transport import HttpRequest, HttpResponse
    from ._pipeline_client import PipelineClient

_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

class _PagingMethodHandlerBase:
    def __init__(
        self,
        paging_method,
        deserialize_output,
        client,
        initial_state,
        **kwargs
    ):
        self._paging_method = paging_method
        self._deserialize_output = deserialize_output
        self._client = client
        self._initial_state = initial_state
        self._cls = kwargs.pop("_cls", None)
        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('error_map', {}))
        self._item_name = kwargs.pop("item_name", "value")
        self._continuation_token_location = kwargs.pop("continuation_token_location", None)
        self._operation_config = kwargs

    @property
    def _initial_request(self):
        if isinstance(self._initial_state, PipelineResponse):
            return self._initial_state.http_response.request
        return self._initial_state

    def _handle_response(self, continuation_token, response):
        http_response = response.http_response
        status_code = http_response.status_code
        if status_code < 200 or status_code >= 300:
            if self._error_map:
                map_error(status_code=status_code, response=http_response, error_map=self._error_map)
            error = HttpResponseError(response=http_response)
            error.continuation_token = continuation_token
            raise error
        if "request_id" not in self._operation_config:
            self._operation_config["request_id"] = response.http_response.request.headers["x-ms-client-request-id"]
        return response

    def _extract_data_helper(self, pipeline_response):
        deserialized = self._deserialize_output(pipeline_response)
        list_of_elem = self._paging_method.get_list_elements(pipeline_response, deserialized, self._item_name)
        list_of_elem = self._paging_method.mutate_list(pipeline_response, list_of_elem, self._cls)
        continuation_token = self._paging_method.get_continuation_token(
            pipeline_response, deserialized, self._continuation_token_location
        )
        return continuation_token, list_of_elem

class _PagingMethodHandler(_PagingMethodHandlerBase):

    def _make_call(self, request):
        return self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )

    def _do_initial_call(self):
        if isinstance(self._initial_state, PipelineResponse):
            return self._initial_state
        return self._make_call(self._initial_state)

    def get_next(self, continuation_token):
        if not continuation_token:
            response = self._do_initial_call()
        else:
            request = self._paging_method.get_next_request(continuation_token, self._initial_request, self._client)
            response = self._make_call(request)
        return self._handle_response(continuation_token, response)

    def extract_data(self, pipeline_response):
        return self._extract_data_helper(pipeline_response)


@add_metaclass(ABCMeta)
class PagingMethodABC():

    def get_next_request(self, continuation_token, initial_request, client):
        # type: (Any, HttpRequest, PipelineClient) -> HttpRequest
        """Return the next request object for paging.

        :param any continuation_token: The token used to continue paging
        :param initial_request: The initial paging request. You can use this as a foundation
         to build up your next request
        :type initial_request: ~azure.core.pipeline.transport.HttpRequest
        :param client: Your client. You can use this client to format your URL, for example.
        :type client: ~azure.core.PipelineClient
        :return: Next request for the pager to make
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        raise NotImplementedError("This method needs to be implemented")

    # extracting data from response

    def get_list_elements(self, pipeline_response, deserialized, item_name="value"):
        # type: (HttpResponse, ResponseType, str) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :param optional[str] item_name: The property name on the response that houses
         the list elements. Default is `value`.
        :return: The iterable of items extracted out of paging response
        :rtype: iterable[object]
        """
        raise NotImplementedError("This method needs to be implemented")

    def mutate_list(self, pipeline_response, list_of_elem, cls=None):
        # type: (HttpResponse, Iterable[ReturnType], Optional[Callable]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param list[object] list_of_elem: The iterable of items we will return to users
         in a page.
        :param optional[callable] cls: Callback to mutate the list.
        :return: The final list of iterable items we will return to users
        :rtype: iterable[object]
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_continuation_token(self, pipeline_response, deserialized, continuation_token_location=None):
        # type: (HttpResponse, ResponseType, Optional[str]) -> Any
        """Get the continuation token from the current page. This operation returning None signals the end of paging.
        Continuation token can be mutated here as well.

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :param optional[str] continuation_token_location: Property name on the response object that houses the
         continuation token. Defaults to `None`, as `None` is an acceptable value for a continuation token location.
         It means that there's no continuation token on the response object.
        :return: The continuation token
        :rtype: any
        """

        raise NotImplementedError("This method needs to be implemented")

class NextLinkPagingMethod(PagingMethodABC):

    def __init__(self, path_format_arguments=None, **kwargs):
        """Most common paging method. Uses the continuation token as the URL for the next call.
        """
        self._path_format_arguments = path_format_arguments or {}

    def get_next_request(self, continuation_token, initial_request, client):
        # type: (Any, HttpRequest, PipelineClient) -> HttpRequest
        """Return the next request object for paging. Uses the continuation token
        as the URL for the next call.

        :param any continuation_token: The token used to continue paging
        :param initial_request: The initial paging request. You can use this as a foundation
         to build up your next request
        :type initial_request: ~azure.core.pipeline.transport.HttpRequest
        :return: Next request for the pager to make
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = initial_request
        next_link = continuation_token
        next_link = client.format_url(next_link, **self._path_format_arguments)
        request.url = next_link
        return request

    def get_list_elements(self, pipeline_response, deserialized, item_name="value"):
        # type: (HttpResponse, ResponseType, str) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :return: The iterable of items extracted out of paging response
        :rtype: iterable[object]
        """
        if hasattr(deserialized, item_name):
            return getattr(deserialized, item_name)
        raise ValueError(
            "The response object does not have property '{}' to extract element list from".format(item_name)
        )

    def mutate_list(self, pipeline_response, list_of_elem, cls=None):
        # type: (HttpResponse, Iterable[ReturnType], Optional[Callable]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param list[object] list_of_elem: The iterable of items we will return to users
         in a page.
        :return: The final list of iterable items we will return to users
        :rtype: iterable[object]
        """
        if cls:
            list_of_elem = cls(list_of_elem)
        return iter(list_of_elem)

    def get_continuation_token(self, pipeline_response, deserialized, continuation_token_location=None):
        # type: (HttpResponse, ResponseType, Optional[str]) -> Any
        """Get the continuation token from the current page. This operation returning None signals the end of paging.

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :return: The continuation token
        :rtype: any
        """
        if continuation_token_location:
            if not hasattr(deserialized, continuation_token_location):
                raise ValueError(
                    "The response object does not have property '{}' to extract continuation token from".format(
                        continuation_token_location
                    )
                )
            return getattr(deserialized, continuation_token_location)
        return None


class CallbackPagingMethod(NextLinkPagingMethod):  # pylint: disable=too-many-instance-attributes
    def __init__(self, next_request_callback, **kwargs):
        """Base paging method. Accepts the callback for the next request as an init arg.

        :param callable next_request_callback: Takes the continuation token as input and
         outputs the next request
        """
        super(CallbackPagingMethod, self).__init__(**kwargs)
        self._next_request_callback = next_request_callback


    def get_next_request(self, continuation_token, initial_request, client):
        # type: (Any, HttpRequest, PipelineClient) -> HttpRequest
        """Return the next request object for paging. Passes the continuation token into
        the next request callback, and returns the resulting next request

        :param any continuation_token: The token used to continue paging
        :param initial_request: The initial paging request. You can use this as a foundation
         to build up your next request
        :type initial_request: ~azure.core.pipeline.transport.HttpRequest
        :return: Next request for the pager to make
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        return self._next_request_callback(continuation_token)

class HeaderPagingMethod(NextLinkPagingMethod):

    def __init__(self, header_name, **kwargs):
        """Passes continuation token as a header parameter to next call.
        """
        super(HeaderPagingMethod, self).__init__(**kwargs)
        self._header_name = header_name

    def get_next_request(self, continuation_token, initial_request, client):
        # type: (Any, HttpRequest, PipelineClient) -> HttpRequest
        """Return the next request object for paging. Passes the continuation token
        with header name `header_name`.

        :param any continuation_token: The token used to continue paging
        :param initial_request: The initial paging request. You can use this as a foundation
         to build up your next request
        :type initial_request: ~azure.core.pipeline.transport.HttpRequest
        :return: Next request for the pager to make
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = initial_request
        request.headers[self._header_name] = continuation_token
        return request

class PageIterator(Iterator[Iterator[ReturnType]]):
    def __init__(
        self,
        get_next=None,  # type: Callable[[Optional[str]], ResponseType]
        extract_data=None,  # type: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]]
        continuation_token=None,  # type: Optional[str]
        paging_method=None,  # type: PagingMethodABC
        **kwargs
    ):
        """Return an iterator of pages.
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
