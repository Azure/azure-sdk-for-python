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

from ._async_list import AsyncList
from ..paging._paging_method_handler import _PagingMethodHandlerBase
from ..pipeline import PipelineResponse

_LOGGER = logging.getLogger(__name__)

class _AsyncPagingMethodHandler(_PagingMethodHandlerBase):

    async def _make_call(self, request):
        return await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )

    async def _do_initial_call(self):
        if isinstance(self._initial_state, PipelineResponse):
            return self._initial_state
        return await self._make_call(self._initial_state)

    async def get_next(self, continuation_token):
        if not continuation_token:
            response = await self._do_initial_call()
        else:
            request = self._paging_method.get_next_request(continuation_token, self.initial_request, self._client)
            response = await self._make_call(request)
        return self._handle_response(response)

    def extract_data(self, pipeline_response):
        continuation_token, list_of_elem = self._extract_data_helper(pipeline_response)
        return continuation_token, AsyncList(list_of_elem)
