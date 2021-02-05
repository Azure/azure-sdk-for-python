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
import logging

from ..exceptions import (
    map_error,
    HttpResponseError,
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError
)
from ..pipeline import PipelineResponse

_LOGGER = logging.getLogger(__name__)

class _PagingMethodHandlerBase(object):
    def __init__(
        self,
        _paging_method,
        _deserialize_output,
        _client,
        _initial_state,
        **kwargs
    ):
        self._paging_method = _paging_method
        self._deserialize_output = _deserialize_output
        self._client = _client
        self._initial_state = _initial_state
        self._cls = kwargs.pop("_cls", None)
        self._error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        self._error_map.update(kwargs.pop('_error_map', {}))
        self._item_name = kwargs.pop("_item_name", "value")
        self._continuation_token_location = kwargs.pop("_continuation_token_location", None)
        self._operation_config = kwargs

    @property
    def initial_request(self):
        if isinstance(self._initial_state, PipelineResponse):
            return self._initial_state.http_response.request
        return self._initial_state

    def _handle_response(self, response):
        http_response = response.http_response
        status_code = http_response.status_code
        if status_code >= 400:
            map_error(status_code=status_code, response=http_response, error_map=self._error_map)
            error = HttpResponseError(response=http_response)
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
            request = self._paging_method.get_next_request(continuation_token, self.initial_request, self._client)
            response = self._make_call(request)
        return self._handle_response(response)

    def extract_data(self, pipeline_response):
        return self._extract_data_helper(pipeline_response)
