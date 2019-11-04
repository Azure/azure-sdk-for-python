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
ImplPoliciesType = List[
    AsyncHTTPPolicy[  # pylint: disable=unsubscriptable-object
        HTTPRequestType, AsyncHTTPResponseType
    ]
]
AsyncPoliciesType = List[Union[AsyncHTTPPolicy, SansIOHTTPPolicy]]

try:
    from contextlib import AbstractAsyncContextManager  # type: ignore
except ImportError:  # Python <= 3.7

    class AbstractAsyncContextManager(object):  # type: ignore
        async def __aenter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        async def __aexit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None


async def _await_result(func, *args, **kwargs):
    """If func returns an awaitable, await it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        # type ignore on await: https://github.com/python/mypy/issues/7587
        return await result  # type: ignore
    return result


class _SansIOAsyncHTTPPolicyRunner(
    AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]
):  # pylint: disable=unsubscriptable-object
    """Async implementation of the SansIO policy.

    Modifies the request and sends to the next policy in the chain.

    :param policy: A SansIO policy.
    :type policy: ~azure.core.pipeline.policies.SansIOHTTPPolicy
    """

    def __init__(self, policy: SansIOHTTPPolicy) -> None:
        super(_SansIOAsyncHTTPPolicyRunner, self).__init__()
        self._policy = policy

    async def send(self, request: PipelineRequest) -> PipelineResponse:
        """Modifies the request and sends to the next policy in the chain.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        await _await_result(self._policy.on_request, request)
        try:
            response = await self.next.send(request)  # type: ignore
        except Exception:  # pylint: disable=broad-except
            if not await _await_result(self._policy.on_exception, request):
                raise
        else:
            await _await_result(self._policy.on_response, request, response)
        return response


class _AsyncTransportRunner(
    AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]
):  # pylint: disable=unsubscriptable-object
    """Async Transport runner.

    Uses specified HTTP transport type to send request and returns response.

    :param sender: The async Http Transport instance.
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
            request.context,
        )


class AsyncPipeline(
    AbstractAsyncContextManager, Generic[HTTPRequestType, AsyncHTTPResponseType]
):
    """Async pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender.

    :param transport: The async Http Transport instance.
    :param list policies: List of configured policies.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_async.py
            :start-after: [START build_async_pipeline]
            :end-before: [END build_async_pipeline]
            :language: python
            :dedent: 4
            :caption: Builds the async pipeline for asynchronous transport.
    """

    def __init__(self, transport, policies: AsyncPoliciesType = None) -> None:
        self._impl_policies = []  # type: ImplPoliciesType
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

    def __enter__(self):
        raise TypeError("Use 'async with' instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self) -> "AsyncPipeline":
        await self._transport.__aenter__()
        return self

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        await self._transport.__aexit__(*exc_details)

    async def _prepare_multipart_mixed_request(self, request):
        # type: (HTTPRequestType) -> None
        """Will execute the multipart policies.

        Does nothing if "set_multipart_mixed" was never called.
        """
        multipart_mixed_info = request.multipart_mixed_info  # type: ignore
        if not multipart_mixed_info:
            return

        requests = multipart_mixed_info[0]  # type: List[HTTPRequestType]
        policies = multipart_mixed_info[1]  # type: List[SansIOHTTPPolicy]

        async def prepare_requests(req):
            context = PipelineContext(None)
            pipeline_request = PipelineRequest(req, context)
            for policy in policies:
                await _await_result(policy.on_request, pipeline_request)

        # Not happy to make this code asyncio specific, but that's multipart only for now
        # If we need trio and multipart, let's reinvesitgate that later
        import asyncio

        await asyncio.gather(*[prepare_requests(req) for req in requests])

    async def run(self, request: HTTPRequestType, **kwargs: Any):
        """Runs the HTTP Request through the chained policies.

        :param request: The HTTP request object.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        await self._prepare_multipart_mixed_request(request)
        request.prepare_multipart_body()  # type: ignore
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(request, context)
        first_node = (
            self._impl_policies[0]
            if self._impl_policies
            else _AsyncTransportRunner(self._transport)
        )
        return await first_node.send(pipeline_request)  # type: ignore
