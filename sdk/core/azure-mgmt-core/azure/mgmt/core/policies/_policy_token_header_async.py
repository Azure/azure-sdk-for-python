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
from typing import TypeVar, Any, TYPE_CHECKING
from azure.core.pipeline import PipelineRequest, PipelineResponse

from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.pipeline.transport import (
    AsyncHttpResponse as LegacyAsyncHttpResponse,
    HttpRequest as LegacyHttpRequest,
)
from ._policy_token_header import _create_acquire_policy_request, _update_request_with_policy_token
from ._authentication_async import await_result

if TYPE_CHECKING:
    from .._async_pipeline_client import AsyncARMPipelineClient

AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType", AsyncHttpResponse, LegacyAsyncHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)


class AsyncPolicyTokenHeaderPolicy(AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):
    """Async HTTP pipeline policy for adding policy token headers to Azure Resource Manager requests.

    This policy handles the acquisition and application of Azure Policy tokens for external
    policy evaluation. It integrates with the Azure Policy service to obtain tokens that
    enable policy evaluation during resource operations.

    :param client: The async ARM pipeline client used for making policy token requests
    :type client: ~azure.mgmt.core.AsyncARMPipelineClient
    :param kwargs: Additional keyword arguments passed to the base policy
    :type kwargs: Any
    """

    def __init__(self, client: "AsyncARMPipelineClient", **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """Initialize the async policy token header policy.

        :param client: The async ARM pipeline client used for making policy token requests
        :type client: ~azure.mgmt.core.AsyncARMPipelineClient
        :param kwargs: Additional keyword arguments passed to the base policy
        :type kwargs: Any
        """
        self._client = client

    async def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Process the request to add policy token headers if needed.

        This method is called for each outgoing request. It checks if a policy token
        is needed and if so, acquires one and adds it to the request headers.

        :param request: The pipeline request to process
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        acquire_policy_token = request.context.options.pop("acquire_policy_token", False)
        if not acquire_policy_token or request.http_request.method.upper() == "GET":
            return
        try:
            acquire_policy_request = _create_acquire_policy_request(request)
            acquire_policy_request.url = self._client.format_url(acquire_policy_request.url)
            acquire_policy_response = await self._client.send_request(acquire_policy_request, stream=False)
            _update_request_with_policy_token(request, acquire_policy_request, acquire_policy_response)
        except Exception:
            request.context.options["acquire_policy_token"] = True
            raise

    async def send(
        self, request: PipelineRequest[HTTPRequestType]
    ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]:
        """Authorize request with a bearer token and send it to the next policy.

        This method processes the request by calling on_request to potentially add
        policy token headers, then forwards the request to the next policy in the pipeline.

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        await await_result(self.on_request, request)
        return await self.next.send(request)
