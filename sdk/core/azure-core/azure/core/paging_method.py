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
from abc import ABCMeta
from typing import TYPE_CHECKING
from six import add_metaclass

from .exceptions import (
    ClientAuthenticationError, ResourceExistsError, ResourceNotFoundError
)

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterable, Tuple, Optional
    from .paging import ResponseType, ReturnType
    from ._pipeline_client import PipelineClient
    from .pipeline.transport import HttpRequest, HttpResponse

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

    def get_next_request(self, continuation_token, next_request_partial=None):
        # type: (Any, Optional[Callable]) -> HttpRequest
        """Gets the next request to make to the service

        :param any continuation_token: Token passed to indicate continued paging, and how to get next page
        :param callable next_request_partial: Optional. Partial function that returns the next request
         when you pass in the continuation_token
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
        self._next_request_partial = None
        self._initial_request = None
        self._operation_config = None
        self._path_format_arguments = path_format_arguments

    def _default_next_request_partial(self, continuation_token):
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
        :keyword callable next_request_partial: A partial function that will take
         in the continuation token and return the request for a subsequent call to the service.
         If you don't pass one in, we will create one for you, based off of the initial_request
         you pass in.
        """
        self._initial_request = kwargs.pop("initial_request", None)
        self._next_request_partial = kwargs.pop("next_request_partial", self._default_next_request_partial)
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

    def get_next_request(self, continuation_token, next_request):
        # type: (Any, Optional[Callable]) -> HttpRequest
        """Gets the next request to make to the service

        :param any continuation_token: Token passed to indicate continued paging, and how to get next page
        :param callable next_request_partial: Optional. Partial function that returns the next request
         when you pass in the continuation_token
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
        """
        self._initial_response = kwargs.pop("initial_response", None)
        super(PagingMethodWithInitialResponse, self).initialize(client, deserialize_output, **kwargs)
        self._initial_request = self._initial_response.http_response.request
