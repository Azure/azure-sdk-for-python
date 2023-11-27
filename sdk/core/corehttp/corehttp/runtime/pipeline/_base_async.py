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
from __future__ import annotations
from types import TracebackType
from typing import Any, Union, Generic, TypeVar, List, Optional, Iterable, Type
from typing_extensions import AsyncContextManager

from . import PipelineRequest, PipelineResponse, PipelineContext
from ..policies import AsyncHTTPPolicy, SansIOHTTPPolicy
from ._tools_async import await_result as _await_result
from ...transport import AsyncHttpTransport

AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")


class _SansIOAsyncHTTPPolicyRunner(
    AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]
):  # pylint: disable=unsubscriptable-object
    """Async implementation of the SansIO policy.

    Modifies the request and sends to the next policy in the chain.

    :param policy: A SansIO policy.
    :type policy: ~corehttp.runtime.pipeline.policies.SansIOHTTPPolicy
    """

    def __init__(self, policy: SansIOHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]) -> None:
        super(_SansIOAsyncHTTPPolicyRunner, self).__init__()
        self._policy = policy

    async def send(
        self, request: PipelineRequest[HTTPRequestType]
    ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]:
        """Modifies the request and sends to the next policy in the chain.

        :param request: The PipelineRequest object.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        await _await_result(self._policy.on_request, request)
        response: PipelineResponse[HTTPRequestType, AsyncHTTPResponseType] = await self.next.send(request)
        await _await_result(self._policy.on_response, request, response)
        return response


class _AsyncTransportRunner(
    AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]
):  # pylint: disable=unsubscriptable-object
    """Async Transport runner.

    Uses specified HTTP transport type to send request and returns response.

    :param sender: The async Http Transport instance.
    :type sender: ~corehttp.transport.AsyncHttpTransport
    """

    def __init__(self, sender: AsyncHttpTransport[HTTPRequestType, AsyncHTTPResponseType]) -> None:
        super(_AsyncTransportRunner, self).__init__()
        self._sender = sender

    async def send(
        self, request: PipelineRequest[HTTPRequestType]
    ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]:
        """Async HTTP transport send method.

        :param request: The PipelineRequest object.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        return PipelineResponse(
            request.http_request,
            await self._sender.send(request.http_request, **request.context.options),
            request.context,
        )


class AsyncPipeline(AsyncContextManager["AsyncPipeline"], Generic[HTTPRequestType, AsyncHTTPResponseType]):
    """Async pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender.

    :param transport: The async Http Transport instance.
    :type transport: ~corehttp.transport.AsyncHttpTransport
    :param list policies: List of configured policies.
    """

    def __init__(
        self,
        transport: AsyncHttpTransport[HTTPRequestType, AsyncHTTPResponseType],
        policies: Optional[
            Iterable[
                Union[
                    AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType],
                    SansIOHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType],
                ]
            ]
        ] = None,
    ) -> None:
        self._impl_policies: List[AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]] = []
        self._transport = transport

        for policy in policies or []:
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOAsyncHTTPPolicyRunner(policy))
            elif policy:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies) - 1):
            self._impl_policies[index].next = self._impl_policies[index + 1]
        if self._impl_policies:
            self._impl_policies[-1].next = _AsyncTransportRunner(self._transport)

    async def __aenter__(self) -> AsyncPipeline[HTTPRequestType, AsyncHTTPResponseType]:
        await self._transport.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self._transport.__aexit__(exc_type, exc_value, traceback)

    async def run(
        self, request: HTTPRequestType, **kwargs: Any
    ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]:
        """Runs the HTTP Request through the chained policies.

        :param request: The HTTP request object.
        :type request: ~corehttp.rest.HttpRequest
        :return: The PipelineResponse object.
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(request, context)
        first_node = self._impl_policies[0] if self._impl_policies else _AsyncTransportRunner(self._transport)
        return await first_node.send(pipeline_request)
