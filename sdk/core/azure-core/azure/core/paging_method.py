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
    from typing import Any, Callable, Iterable, Tuple, Optional
    from .paging import ResponseType, ReturnType
    from ._pipeline_client import PipelineClient
    from .pipeline.transport import HttpRequest, HttpResponse

@add_metaclass(ABCMeta)
class PagingMethodABC():

    # making requests

    def initialize(self, client, deserialize_output, **kwargs):
        # type: (PipelineClient, Callable, Any) -> None
        """Gets parameters to make next request
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_next_request(self, continuation_token, next_request_partial=None):
        # type: (Any, Optional[Callable]) -> HttpRequest
        """Gets parameters to make next request
        """
        raise NotImplementedError("This method needs to be implemented")

    def finished(self, did_a_call_already, continuation_token):
        # type: (bool, Any) -> bool
        """When paging is finished
        """
        raise NotImplementedError("This method needs to be implemented")

    # extracting data from response

    def get_list_elements(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Iterable[ReturnType]
        """Extract the list elements from the current page to return to users
        """
        raise NotImplementedError("This method needs to be implemented")

    def mutate_list(self, pipeline_response, list_of_elem):
        # type: (HttpResponse, Iterable[ReturnType]) -> Iterable[ReturnType]
        """Mutate list of elements in current page, i.e. if users passed in a cls calback
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_continuation_token(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Any
        """Get the continuation token from the current page
        """
        raise NotImplementedError("This method needs to be implemented")


class BasicPagingMethod(PagingMethodABC):  # pylint: disable=too-many-instance-attributes
    """This is the most common paging method. It uses the continuation token
    as the next link
    """

    def __init__(self, **operation_config):
        self._client = None
        self._deserialize_output = None
        self._item_name = None
        self._continuation_token_location = None
        self._cls = None
        self._error_map = None
        self._next_request_partial = None
        self._initial_request = None
        self._operation_config = operation_config

    def initialize(self, client, deserialize_output, **kwargs):
        # type: (PipelineClient, Callable, Any) -> None
        try:
            self._initial_request = kwargs.pop("initial_request")
            self._next_request_partial = kwargs.pop("next_request_partial")
        except KeyError as e:
            raise TypeError(
                "BasicPagingMethod is missing required keyword-only arg {}".format(
                    str(e).replace("KeyError: ", "")
                )
            )
        self._client = client
        self._deserialize_output = deserialize_output
        self._item_name = kwargs.pop("item_name", "value")
        self._cls = kwargs.pop("_cls", None)
        self._continuation_token_location = kwargs.pop("continuation_token_location")

        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('error_map', {}))

    def get_next_request(self, continuation_token, next_request_partial=None):
        # type: (Any, Optional[Callable]) -> HttpRequest
        if not next_request_partial:
            raise TypeError(
                "You need to pass in a callback for next request that takes in a continuation token"
            )
        return next_request_partial(continuation_token)

    def finished(self, did_a_call_already, continuation_token):
        # type: (bool, Any) -> bool
        return did_a_call_already and not continuation_token

    def get_list_elements(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Iterable[ReturnType]
        if not hasattr(deserialized, self._item_name):
            raise ValueError(
                "The response object does not have property '{}' to extract element list from".format(self._item_name)
            )
        return getattr(deserialized, self._item_name)

    def mutate_list(self, pipeline_response, list_of_elem):
        # type: (HttpResponse, Iterable[ReturnType]) -> Iterable[ReturnType]
        if self._cls:
            list_of_elem = self._cls(list_of_elem)
        return iter(list_of_elem)

    def get_continuation_token(self, pipeline_response, deserialized):
        # type: (HttpResponse, ResponseType) -> Any
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
    """Use this paging method if we start paging before user starts iterating.
    Currently only scenario is LRO + paging, where the final response of the LRO operation
    is the initial page.
    """

    def __init__(self):
        super(PagingMethodWithInitialResponse, self).__init__()
        self._initial_response = None
        self._path_format_arguments = None

    def initialize(self, client, deserialize_output, **kwargs):
        # type: (PipelineClient, Callable, Any) -> None
        try:
            self._initial_response = kwargs.pop("initial_response")
            self._continuation_token_location = kwargs.pop("continuation_token_location")
        except KeyError as e:
            raise TypeError(
                "PagingMethodWithInitialResponse is missing required keyword-only arg {}".format(
                    str(e).replace("KeyError: ", "")
                )
            )
        self._next_request_partial = kwargs.pop("next_request_partial", None)
        self._client = client
        self._deserialize_output = deserialize_output
        self._path_format_arguments = kwargs.pop("path_format_arguments", {})

        self._item_name = kwargs.pop("item_name", "value")
        self._cls = kwargs.pop("_cls", None)

        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('error_map', {}))

    def get_next_request(self, continuation_token, next_request_partial=None):
        # type: (Any, Optional[Callable]) -> HttpRequest
        if next_request_partial:
            return next_request_partial(continuation_token)
        request = self._initial_response.http_response.request
        request.url = self._client.format_url(continuation_token, **self._path_format_arguments)
        return request
