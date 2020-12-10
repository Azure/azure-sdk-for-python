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

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Dict,
        Optional,
        Iterable,
        Tuple,
    )
    from azure.core.pipeline.transport import HttpRequest, HttpResponse
    from ._pipeline_client import PipelineClient

_LOGGER = logging.getLogger(__name__)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

def _extract_data_helper(pipeline_response, paging_method):
    deserialized = paging_method._deserialize_output(pipeline_response)  # pylint: disable=protected-access
    list_of_elem = paging_method.get_list_elements(pipeline_response, deserialized)  # type: Iterable[ReturnType]
    list_of_elem = paging_method.mutate_list(pipeline_response, list_of_elem)
    continuation_token = paging_method.get_continuation_token(pipeline_response, deserialized)
    return continuation_token, list_of_elem

def _extract_data(pipeline_response, paging_method):
    return _extract_data_helper(pipeline_response, paging_method)

def _get_request(continuation_token, paging_method):
    if not continuation_token:
        request = paging_method._initial_request  # pylint: disable=protected-access
    else:
        request = paging_method._next_request_callback(continuation_token)  # pylint: disable=protected-access
        request = paging_method.mutate_next_request(continuation_token, request, paging_method._initial_request)  # pylint: disable=protected-access
    return request

def _handle_response(continuation_token, paging_method, response):
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

def _get_page(continuation_token, paging_method, initial_response):
    if not continuation_token and initial_response:
        return initial_response
    request = _get_request(continuation_token, paging_method)

    response = paging_method._client._pipeline.run(  # pylint: disable=protected-access
        request, stream=False, **paging_method._operation_config  # pylint: disable=protected-access
    )
    return _handle_response(continuation_token, paging_method, response)



@add_metaclass(ABCMeta)
class PagingMethodABC():

    def initialize(self, client, deserialize_output, **kwargs):
        # type: (PipelineClient, Callable, Any) -> None
        """Initializes PagingMethod with variables passed through ItemPaged

        :param client: The client used to make requests
        :type client: ~azure.core.PipelineClient
        :param callable deserialize_output: Callback to deserialize response output
        """
        raise NotImplementedError("This method needs to be implemented")

    def mutate_next_request(self, continuation_token, next_request, initial_request):
        # type: (Any, HttpRequest) -> HttpRequest
        """Mutate next request if there are any modifications that need to be
        made to what azure core assumes the next request will be.

        :param any continuation_token: Token passed to indicate continued paging, and how to get next page
        :param next_request: What azure core assumes your next request to be.
        :type next_request: ~azure.core.pipeline.transport.HttpRequest
        :param initial_request: The initial request object you passed in. You can use the initial
         request to help mutate the next request object.
        :type initial_request: ~azure.core.pipeline.transport.HttpRequest
        :return: A request object to make the next request to the service with
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        raise NotImplementedError("This method needs to be implemented")

    # extracting data from response

    def get_list_elements(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :return: The iterable of items extracted out of paging response
        :rtype: iterable[object]
        """
        raise NotImplementedError("This method needs to be implemented")

    def mutate_list(self, pipeline_response, list_of_elem):
        # type: (HttpResponse, Iterable[ReturnType]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param list[object] list_of_elem: The iterable of items we will return to users
         in a page.
        :return: The final list of iterable items we will return to users
        :rtype: iterable[object]
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_continuation_token(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Any
        """Get the continuation token from the current page. This operation returning None signals the end of paging.
        Continuation token can be mutated here as well.

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :return: The continuation token
        :rtype: any
        """

        raise NotImplementedError("This method needs to be implemented")


class BasicPagingMethod(PagingMethodABC):  # pylint: disable=too-many-instance-attributes
    def __init__(self, path_format_arguments=None):
        """This is the most common paging method. It takes in an initial request object
        and a partial for next requests. Once deserializing the data and returning the iterable
        of paged items, it passes the continuation token from the response to the partial for the next
        request. It keeps paging until a subsequent call to the service returns an empty continuation token.

        :param dict[str, any] path_format_arguments: Any path formatting arguments you would need
         to format the endpoint for your next call
        """
        self._client = None
        self._deserialize_output = None
        self._item_name = None
        self._continuation_token_location = None
        self._cls = None
        self._error_map = None
        self._next_request_callback = None
        self._initial_request = None
        self._operation_config = None
        self._path_format_arguments = path_format_arguments

    def _default_next_request_callback(self, continuation_token):
        request = self._initial_request
        url = continuation_token
        if self._path_format_arguments:
            url = self._client.format_url(continuation_token, **self._path_format_arguments)
        request.url = url
        return request

    def _validate_inputs(self):
        if not self._initial_request:
            raise TypeError("BasicPagingMethod is missing required keyword-only arg initial_request")

    def initialize(self, client, deserialize_output, **kwargs):
        # type: (PipelineClient, Callable, Any) -> None
        """Initializes BasicPagingMethod with variables passed through ItemPaged

        :param client: The client used to make requests
        :type client: ~azure.core.PipelineClient
        :param callable deserialize_output: Callback to deserialize response output
        :keyword initial_request: Required. The request for our intial call to the service
         to begin paging
        :paramtype initial_request: ~azure.core.pipeline.transport.HttpRequest
        :keyword str continuation_token_location: Required. Specifies the name of the property that provides
         the continuation token. Common values include `next_link` and `token`.
        :keyword callable next_request_callback: A partial function that will take
         in the continuation token and return the request for a subsequent call to the service.
         If you don't pass one in, we will create one for you, based off of the initial_request
         you pass in. We will assume the continuation token is the url for the next request, and we will
         also format the URL based off of the `path_format_arguments` you initialize you pass in.
        :keyword str item_name: Specifies the name of the property that provides the collection of pageable
         items. Defaults to `value`.
        :keyword callable cls: A custom type or function that will modify each element of the pageable items.
         Takes a list of iterables as an input.
        """
        self._initial_request = kwargs.pop("initial_request", None)
        self._next_request_callback = kwargs.pop("next_request_callback", self._default_next_request_callback)
        self._client = client
        self._deserialize_output = deserialize_output
        self._item_name = kwargs.pop("item_name", "value")
        self._cls = kwargs.pop("_cls", None)
        self._continuation_token_location = kwargs.pop("continuation_token_location", None)

        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('error_map', {}))
        self._operation_config = kwargs
        self._validate_inputs()

    def mutate_next_request(self, continuation_token, next_request, initial_request):
        # type: (Any, HttpRequest) -> HttpRequest
        """Mutate next request if there are any modifications that need to be
        made to what azure core assumes the next request will be.

        :param any continuation_token: Token passed to indicate continued paging, and how to get next page
        :param next_request: What azure core assumes your next request to be.
        :type next_request: ~azure.core.pipeline.transport.HttpRequest
        :param initial_request: The initial request object you passed in. You can use the initial
         request to help mutate the next request object.
        :type initial_request: ~azure.core.pipeline.transport.HttpRequest
        :return: A request object to make the next request to the service with
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        return next_request

    def get_list_elements(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :return: The iterable of items extracted out of paging response
        :rtype: iterable[object]
        """
        if not hasattr(deserialized, self._item_name):
            raise ValueError(
                "The response object does not have property '{}' to extract element list from".format(self._item_name)
            )
        return getattr(deserialized, self._item_name)

    def mutate_list(self, pipeline_response, list_of_elem):
        # type: (HttpResponse, Iterable[ReturnType]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param list[object] list_of_elem: The iterable of items we will return to users
         in a page.
        :return: The final list of iterable items we will return to users
        :rtype: iterable[object]
        """
        if self._cls:
            list_of_elem = self._cls(list_of_elem)
        return iter(list_of_elem)

    def get_continuation_token(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Any
        """Get the continuation token from the current page. This operation returning None signals the end of paging.

        :param pipeline_response: The immediate response returned from the pipeline
        :type pipeline_response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized pipeline_response
        :return: The continuation token
        :rtype: any
        """
        if not self._continuation_token_location:
            return None
        if not hasattr(deserialized, self._continuation_token_location):
            raise ValueError(
                "The response object does not have property '{}' to extract continuation token from".format(
                    self._continuation_token_location
                )
            )
        return getattr(deserialized, self._continuation_token_location)


class PagingMethodWithInitialResponse(BasicPagingMethod):
    def __init__(self, path_format_arguments=None):
        """Use this paging method if paging has started before user starts iterating.
        Currently only scenario is LRO + paging, where the final response of the LRO operation
        is the initial page.

        :param dict[str, any] path_format_arguments: Any path formatting arguments you would need
         to format the endpoint for your next call
        """
        super(PagingMethodWithInitialResponse, self).__init__(path_format_arguments)
        self._initial_response = None

    def _validate_inputs(self):
        if not self._initial_response:
            raise TypeError("BasicPagingMethod is missing required keyword-only arg initial_response")

    def initialize(self, client, deserialize_output, **kwargs):
        # type: (PipelineClient, Callable, Any) -> None
        """Initializes PagingMethodWithInitialResponse with variables passed through ItemPaged

        :param client: The client used to make requests
        :type client: ~azure.core.PipelineClient
        :param callable deserialize_output: Callback to deserialize response output
        :keyword initial_response: Required. The response of the first request to start paging. In LRO + paging,
         the LRO function's final returned object is the initial response.
        :paramtype initial_response: ~azure.core.pipeline.transport.HttpResponse
        :keyword str continuation_token_location: Required. Specifies the name of the property that provides
         the continuation token. Common values include `next_link` and `token`.
        :keyword callable next_request_callback: A partial function that will take
         in the continuation token and return the request for a subsequent call to the service.
         If you don't pass one in, we will create one for you, based off of the initial_request
         you pass in.  We will assume the continuation token is the url for the next request, and we will
         also format the URL based off of the `path_format_arguments` you initialize you pass in.
        :keyword str item_name: Specifies the name of the property that provides the collection of pageable
         items. Defaults to `value`.
        :keyword callable cls: A custom type or function that will modify each element of the pageable items.
         Takes a list of iterables as an input.
        """
        self._initial_response = kwargs.pop("initial_response", None)
        super(PagingMethodWithInitialResponse, self).initialize(client, deserialize_output, **kwargs)
        self._initial_request = self._initial_response.http_response.request

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
        if self._paging_method:
            self._paging_method.initialize(**kwargs)
        self._extract_data = extract_data or functools.partial(_extract_data, paging_method=self._paging_method)
        self._get_page = get_next or functools.partial(
            _get_page, paging_method=self._paging_method, initial_response=kwargs.get("initial_response")
        )

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
