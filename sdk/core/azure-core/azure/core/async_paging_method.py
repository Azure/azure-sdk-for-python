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
from typing import Any, Callable, Iterable, Tuple
from .paging import ResponseType, ReturnType
from ._pipeline_client import PipelineClient
from .pipeline.transport import HttpRequest, HttpResponse

from .exceptions import (
    HttpResponseError, ClientAuthenticationError, ResourceExistsError, ResourceNotFoundError, map_error
)

class AsyncPagingMethodABC(metaclass=ABCMeta):

    # making requests
    def initialize(
        self,
        client: PipelineClient,
        deserialize_output: Callable,
        next_link_name: str,
        **kwargs
    ) -> None:
        """Gets parameters to make next request
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_next_request(self, continuation_token: Any) -> HttpRequest:
        """Gets parameters to make next request
        """
        raise NotImplementedError("This method needs to be implemented")

    async def get_page(self, continuation_token: Any) -> HttpResponse:
        """Gets next page
        """
        raise NotImplementedError("This method needs to be implemented")

    def finished(self, continuation_token: Any) -> bool:
        """When paging is finished
        """
        raise NotImplementedError("This method needs to be implemented")


    # extracting data from response

    def get_list_elements(
        self, pipeline_response: HttpResponse, deserialized: ResponseType
    )  -> Iterable[ReturnType]:
        """Extract the list elements from the current page to return to users
        """
        raise NotImplementedError("This method needs to be implemented")

    def mutate_list(
        self, pipeline_response: HttpResponse, list_of_elem: Iterable[ReturnType]
    ) -> Iterable[ReturnType]:
        """Mutate list of elements in current page, i.e. if users passed in a cls calback
        """
        raise NotImplementedError("This method needs to be implemented")

    def get_continuation_token(
        self, pipeline_response: HttpResponse, deserialized: ResponseType
    ) -> Any:
        """Get the continuation token from the current page
        """
        raise NotImplementedError("This method needs to be implemented")

    async def extract_data(self, pipeline_response: HttpResponse):
        """Return the continuation token and current list of elements to PageIterator
        """
        raise NotImplementedError("This method needs to be implemented")


class AsyncBasicPagingMethod(AsyncPagingMethodABC):
    """This is the most common paging method. It uses the continuation token
    as the next link
    """
    def __init__(self):
        self._client = None
        self._deserialize_output = None
        self._item_name = None
        self._next_link_name = None
        self.did_a_call_already = False
        self._cls = None
        self._error_map = None
        self._next_request_partial = None
        self._initial_request = None

    def initialize(
        self,
        client: PipelineClient,
        deserialize_output: Callable,
        next_link_name: str,
        **kwargs
    ) -> None:

        try:
            self._initial_request = kwargs.pop("initial_request")
            self._next_request_partial = kwargs.pop("next_request_partial")
        except KeyError as e:
            raise TypeError(
                "AsyncBasicPagingMethod is missing required keyword-only arg {}".format(
                    str(e).replace("KeyError: ", "")
                )
            )
        self._client = client
        self._deserialize_output = deserialize_output
        self._next_link_name = next_link_name

        self._item_name = kwargs.pop("item_name", "value")
        self._cls = kwargs.pop("_cls", None)

        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('error_map', {}))

    def get_next_request(self, continuation_token: Any) -> HttpRequest:
        try:
            return self._next_request_partial(continuation_token)
        except TypeError:
            return self._next_request_partial()

    async def get_page(self, continuation_token: Any) -> HttpResponse:
        if not self.did_a_call_already:
            request = self._initial_request
            self.did_a_call_already = True
        else:
            request = self.get_next_request(continuation_token)
        response = await self._client._pipeline.run(request, stream=False)  # pylint: disable=protected-access

        http_response = response.http_response
        status_code = http_response.status_code
        if status_code < 200 or status_code >= 300:
            map_error(status_code=status_code, response=http_response, error_map=self._error_map)
            raise HttpResponseError(response=http_response)

        return response

    def finished(self, continuation_token: Any) -> bool:
        return continuation_token is None and self.did_a_call_already

    def get_list_elements(
        self, pipeline_response: HttpResponse, deserialized: ResponseType
    )  -> Iterable[ReturnType]:
        if not hasattr(deserialized, self._item_name):
            raise ValueError(
                "The response object does not have property '{}' to extract element list from".format(self._item_name)
            )
        return getattr(deserialized, self._item_name)

    def mutate_list(
        self, pipeline_response: HttpResponse, list_of_elem: Iterable[ReturnType]
    ) -> Iterable[ReturnType]:
        if self._cls:
            list_of_elem = self._cls(list_of_elem)
        return iter(list_of_elem)

    def get_continuation_token(
        self, pipeline_response: HttpResponse, deserialized: ResponseType
    ) -> Any:
        if not self._next_link_name:
            return None
        if not hasattr(deserialized, self._next_link_name):
            raise ValueError(
                "The response object does not have property '{}' to extract continuation token from".format(
                    self._next_link_name
                )
            )
        return getattr(deserialized, self._next_link_name)


    async def extract_data(self, pipeline_response: HttpResponse):
        from .async_paging import AsyncList

        deserialized = self._deserialize_output(pipeline_response)
        list_of_elem = self.get_list_elements(pipeline_response, deserialized)  # type: Iterable[Any]
        list_of_elem = self.mutate_list(pipeline_response, list_of_elem)
        continuation_token = self.get_continuation_token(pipeline_response, deserialized)
        return continuation_token, AsyncList(list_of_elem)


class AsyncPagingMethodWithInitialResponse(AsyncBasicPagingMethod):
    """Use this paging method if the swagger defines a different next operation
    """

    def __init__(self):
        super(AsyncPagingMethodWithInitialResponse, self).__init__()
        self._initial_response = None

    def initialize(
        self,
        client: PipelineClient,
        deserialize_output: Callable,
        next_link_name: str,
        **kwargs
    ) -> None:
        try:
            self._initial_response = kwargs.pop("initial_response")
        except KeyError:
            raise TypeError(
                "AsyncPagingMethodWithInitialResponse is missing required keyword-only arg "
                "'initial_response'"
            )
        self._next_request_partial = kwargs.pop("next_request_partial", None)
        self._client = client
        self._deserialize_output = deserialize_output
        self._next_link_name = next_link_name

        self._item_name = kwargs.pop("item_name", "value")
        self._cls = kwargs.pop("_cls", None)

        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('error_map', {}))

    def get_next_request(self, continuation_token: Any) -> HttpRequest:
        if self._next_request_partial:
            return super(AsyncPagingMethodWithInitialResponse, self).get_next_request(continuation_token)
        request = self._initial_response.http_response.request
        request.url = continuation_token
        return request

    async def get_page(self, continuation_token):
        # type: (Any, HttpRequest) -> HttpResponse
        if not self.did_a_call_already:
            self.did_a_call_already = True
            return self._initial_response
        request = self.get_next_request(continuation_token)
        response = await self._client._pipeline.run(request, stream=False)  # pylint: disable=protected-access

        http_response = response.http_response
        status_code = http_response.status_code
        if status_code < 200 or status_code >= 300:
            map_error(status_code=status_code, response=http_response, error_map=self._error_map)
            raise HttpResponseError(response=http_response)

        return response
