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
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
from six import add_metaclass

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Iterable,
        Optional,
    )
    from ._utils import ReturnType, ResponseType
    from ..pipeline.transport import HttpResponse, HttpRequest
    from .._pipeline_client import PipelineClient

@add_metaclass(ABCMeta)
class _PagingMethodABC(object):

    @abstractmethod
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

    @abstractmethod
    def get_list_elements(self, response, deserialized, item_name="value"):
        # type: (HttpResponse, ResponseType, str) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users

        :param response: The immediate response returned from the pipeline
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized response
        :param optional[str] item_name: The property name on the response that houses
         the list elements. Default is `value`.
        :return: The iterable of items extracted out of paging response
        :rtype: iterable[object]
        """
        raise NotImplementedError("This method needs to be implemented")

    @abstractmethod
    def mutate_list(self, response, list_of_elem, cls=None):
        # type: (HttpResponse, Iterable[ReturnType], Optional[Callable]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback

        :param response: The immediate response returned from the pipeline
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param list[object] list_of_elem: The iterable of items we will return to users
         in a page.
        :param optional[callable] cls: Callback to mutate the list.
        :return: The final list of iterable items we will return to users
        :rtype: iterable[object]
        """
        raise NotImplementedError("This method needs to be implemented")

    @abstractmethod
    def get_continuation_token(self, response, deserialized, continuation_token_location=None):
        # type: (HttpResponse, ResponseType, Optional[str]) -> Any
        """Get the continuation token from the current page. This operation returning None signals the end of paging.
        Continuation token can be mutated here as well.

        :param response: The immediate response returned from the pipeline
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized response
        :param optional[str] continuation_token_location: Property name on the response object that houses the
         continuation token. Defaults to `None`, as `None` is an acceptable value for a continuation token location.
         It means that there's no continuation token on the response object.
        :return: The continuation token. Can be any value, and will be passed as-is to :func:`get_next_request`.
        :rtype: any
        """

        raise NotImplementedError("This method needs to be implemented")

class _ContinueWithCallback(_PagingMethodABC):

    def __init__(self, next_request_callback):
        """Base paging method. Accepts the callback for the next request as an init arg.

        :param callable next_request_callback: Takes the continuation token as input and
         outputs the next request
        """
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

    def get_list_elements(self, response, deserialized, item_name="value"):
        # type: (HttpResponse, ResponseType, str) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users

        :param response: The immediate response returned from the pipeline
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized response
        :return: The iterable of items extracted out of paging response
        :rtype: iterable[object]
        """
        try:
            return getattr(deserialized, item_name)
        except AttributeError:
            raise ValueError(
                "The response object does not have property '{}' to extract element list from".format(
                    item_name
                )
            )

    def mutate_list(self, response, list_of_elem, cls=None):
        # type: (HttpResponse, Iterable[ReturnType], Optional[Callable]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback

        :param response: The immediate response returned from the pipeline
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param list[object] list_of_elem: The iterable of items we will return to users
         in a page.
        :return: The final list of iterable items we will return to users
        :rtype: iterable[object]
        """
        if cls:
            list_of_elem = cls(list_of_elem)
        return iter(list_of_elem)

    def get_continuation_token(self, response, deserialized, continuation_token_location=None):
        # type: (HttpResponse, ResponseType, Optional[str]) -> Any
        """Get the continuation token from the current page. This operation returning None signals the end of paging.

        :param response: The immediate response returned from the pipeline
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param object deserialized: The deserialized response
        :return: The continuation token. Can be any value, and will be passed as-is to :func:`get_next_request`.
        :rtype: any
        """
        if not continuation_token_location:
            return None
        try:
            return getattr(deserialized, continuation_token_location)
        except AttributeError:
            pass
        # check response headers for cont token
        return response.headers.get(continuation_token_location, None)

class _ContinueWithNextLink(_ContinueWithCallback):

    def __init__(self, path_format_arguments=None):
        """Most common paging method. Uses the continuation token as the URL for the next call.
        """
        def _next_request_callback(continuation_token, initial_request, client):
            request = initial_request
            next_link = client.format_url(continuation_token, **self._path_format_arguments)
            request.url = next_link
            return request

        super(_ContinueWithNextLink, self).__init__(
            next_request_callback=_next_request_callback
        )
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
        return self._next_request_callback(continuation_token, initial_request, client)

class _ContinueWithRequestHeader(_ContinueWithCallback):

    def __init__(self, header_name):
        """Passes continuation token as a header parameter to next call.
        """
        self._header_name = header_name
        def _next_request_callback(continuation_token, initial_request):
            request = initial_request
            request.headers[self._header_name] = continuation_token
            return request
        super(_ContinueWithRequestHeader, self).__init__(
            next_request_callback=_next_request_callback
        )

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
        return self._next_request_callback(continuation_token, initial_request)
