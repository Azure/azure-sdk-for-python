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
import abc

from typing import Any, Union, List, Generic, TypeVar

from azure.core.pipeline import PipelineRequest, PipelineResponse, PipelineContext
from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy

AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")
ImplPoliciesType = List[AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]] #pylint: disable=unsubscriptable-object
AsyncPoliciesType = List[Union[AsyncHTTPPolicy, SansIOHTTPPolicy]]

try:
    from contextlib import AbstractAsyncContextManager  # type: ignore
except ImportError: # Python <= 3.7
    class AbstractAsyncContextManager(object):  # type: ignore
        async def __aenter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        async def __aexit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None


class _SansIOAsyncHTTPPolicyRunner(AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]): #pylint: disable=unsubscriptable-object
    """Async implementation of the SansIO policy.

    Modifies the request and sends to the next policy in the chain.

    :param policy: A SansIO policy.
    :type policy: ~azure.core.pipeline.policies.SansIOHTTPPolicy
    """

    def __init__(self, policy: SansIOHTTPPolicy) -> None:
        super(_SansIOAsyncHTTPPolicyRunner, self).__init__()
        self._policy = policy

    async def send(self, request: PipelineRequest):
        """Modifies the request and sends to the next policy in the chain.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        self._policy.on_request(request)
        try:
            response = await self.next.send(request)  # type: ignore
        except Exception: #pylint: disable=broad-except
            if not self._policy.on_exception(request):
                raise
        else:
            self._policy.on_response(request, response)
        return response


class _AsyncTransportRunner(AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]): #pylint: disable=unsubscriptable-object
    """Async Transport runner.

    Uses specified HTTP transport type to send request and returns response.

    :param sender: The async Http Transport type.
    """
    def __init__(self, sender) -> None:
        super(_AsyncTransportRunner, self).__init__()
        self._sender = sender

    async def send(self, request):
        """Async HTTP transport send method.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        return PipelineResponse(
            request.http_request,
            await self._sender.send(request.http_request, **request.context.options),
            request.context
        )


class AsyncPipeline(AbstractAsyncContextManager, Generic[HTTPRequestType, AsyncHTTPResponseType]):
    """Async pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender.

    :param transport: The async Http Transport type.
    :param list policies: List of configured policies.
    """

    def __init__(self, transport, policies: AsyncPoliciesType = None) -> None:
        self._impl_policies = []  # type: ImplPoliciesType
        self._transport = transport

        for policy in (policies or []):
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOAsyncHTTPPolicyRunner(policy))
            elif policy:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies)-1):
            self._impl_policies[index].next = self._impl_policies[index+1]
        if self._impl_policies:
            self._impl_policies[-1].next = _AsyncTransportRunner(self._transport)

    def __enter__(self):
        raise TypeError("Use 'async with' instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self) -> 'AsyncPipeline':
        await self._transport.__aenter__()
        return self

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        await self._transport.__aexit__(*exc_details)

    async def run(self, request: PipelineRequest, **kwargs: Any):
        """Runs the HTTP Request through the chained policies.

        :param request: The HTTP request object.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(request, context)
        first_node = self._impl_policies[0] if self._impl_policies else _AsyncTransportRunner(self._transport)
        return await first_node.send(pipeline_request)  # type: ignore
