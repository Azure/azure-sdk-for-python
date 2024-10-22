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
import logging
from typing import Generic, TypeVar, Union, Any, List, Optional, Iterable, ContextManager
from typing_extensions import TypeGuard

from . import (
    PipelineRequest,
    PipelineResponse,
    PipelineContext,
)
from ..policies import HTTPPolicy, SansIOHTTPPolicy
from ._tools import await_result as _await_result
from ...transport import HttpTransport

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)


def is_http_policy(policy: object) -> TypeGuard[HTTPPolicy]:
    if hasattr(policy, "send"):
        return True
    return False


def is_sansio_http_policy(policy: object) -> TypeGuard[SansIOHTTPPolicy]:
    if hasattr(policy, "on_request") and hasattr(policy, "on_response"):
        return True
    return False


class _SansIOHTTPPolicyRunner(HTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Sync implementation of the SansIO policy.

    Modifies the request and sends to the next policy in the chain.

    :param policy: A SansIO policy.
    :type policy: ~corehttp.runtime.pipeline.policies.SansIOHTTPPolicy
    """

    def __init__(self, policy: SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]) -> None:
        super(_SansIOHTTPPolicyRunner, self).__init__()
        self._policy = policy

    def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]:
        """Modifies the request and sends to the next policy in the chain.

        :param request: The PipelineRequest object.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        _await_result(self._policy.on_request, request)
        response = self.next.send(request)
        _await_result(self._policy.on_response, request, response)
        return response


class _TransportRunner(HTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Transport runner.

    Uses specified HTTP transport type to send request and returns response.

    :param sender: The Http Transport instance.
    :type sender: ~corehttp.transport.HttpTransport
    """

    def __init__(self, sender: HttpTransport[HTTPRequestType, HTTPResponseType]) -> None:
        super(_TransportRunner, self).__init__()
        self._sender = sender

    def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]:
        """HTTP transport send method.

        :param request: The PipelineRequest object.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        return PipelineResponse(
            request.http_request,
            self._sender.send(request.http_request, **request.context.options),
            context=request.context,
        )


class Pipeline(ContextManager["Pipeline"], Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender. The transport is the last node in the pipeline.

    :param transport: The Http Transport instance
    :type transport: ~corehttp.transport.HttpTransport
    :param list policies: List of configured policies.
    """

    def __init__(
        self,
        transport: HttpTransport[HTTPRequestType, HTTPResponseType],
        policies: Optional[
            Iterable[
                Union[
                    HTTPPolicy[HTTPRequestType, HTTPResponseType], SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]
                ]
            ]
        ] = None,
    ) -> None:
        self._impl_policies: List[HTTPPolicy[HTTPRequestType, HTTPResponseType]] = []
        self._transport = transport

        for policy in policies or []:
            if is_http_policy(policy):
                self._impl_policies.append(policy)
            elif is_sansio_http_policy(policy):
                self._impl_policies.append(_SansIOHTTPPolicyRunner(policy))
            elif policy:
                raise AttributeError(
                    f"'{type(policy)}' object has no attribute 'send' or both 'on_request' and 'on_response'."
                )
        for index in range(len(self._impl_policies) - 1):
            self._impl_policies[index].next = self._impl_policies[index + 1]
        if self._impl_policies:
            self._impl_policies[-1].next = _TransportRunner(self._transport)

    def __enter__(self) -> Pipeline[HTTPRequestType, HTTPResponseType]:
        self._transport.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._transport.__exit__(*exc_details)

    def run(self, request: HTTPRequestType, **kwargs: Any) -> PipelineResponse[HTTPRequestType, HTTPResponseType]:
        """Runs the HTTP Request through the chained policies.

        :param request: The HTTP request object.
        :type request: ~corehttp.rest.HttpRequest
        :return: The PipelineResponse object
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        """
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request: PipelineRequest[HTTPRequestType] = PipelineRequest(request, context)
        first_node = self._impl_policies[0] if self._impl_policies else _TransportRunner(self._transport)
        return first_node.send(pipeline_request)
