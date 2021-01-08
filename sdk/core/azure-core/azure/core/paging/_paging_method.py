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

    def __init__(self, path_format_arguments=None, **kwargs):  # pylint: disable=unused-argument
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
