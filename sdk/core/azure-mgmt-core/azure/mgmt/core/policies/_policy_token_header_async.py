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
from typing import TypeVar, Any
from azure.core.pipeline import PipelineRequest, PipelineResponse

from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.pipeline.transport import (
    AsyncHttpResponse as LegacyAsyncHttpResponse,
    HttpRequest as LegacyHttpRequest,
)
from .._async_pipeline_client import AsyncARMPipelineClient
from ._policy_token_header import _PolicyTokenHeaderPolicyBase
from ._authentication_async import await_result

AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType", AsyncHttpResponse, LegacyAsyncHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)


class AsyncPolicyTokenHeaderPolicy(
    _PolicyTokenHeaderPolicyBase, AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]
):

    def __init__(self, client: AsyncARMPipelineClient, **kwargs: Any):
        super().__init__(**kwargs)
        self._client = client

    async def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        acquire_policy_request = self._create_acquire_policy_request(request)
        if acquire_policy_request:
            acquire_policy_response = await self._client.send_request(acquire_policy_request, stream=False)
            self._update_request_with_policy_token(request, acquire_policy_request, acquire_policy_response)

    async def send(
        self, request: PipelineRequest[HTTPRequestType]
    ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]:
        """Authorize request with a bearer token and send it to the next policy

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        await await_result(self.on_request, request)
        await self.next.send(request)
