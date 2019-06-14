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
from typing import (TYPE_CHECKING, Generic, TypeVar, cast, IO, List, Union, Any, Mapping, Dict, Optional, # pylint: disable=unused-import
                    Tuple, Callable, Iterator)
from azure.core.pipeline import AbstractContextManager, PipelineRequest, PipelineResponse, PipelineContext
from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")
HttpTransportType = TypeVar("HttpTransportType")

_LOGGER = logging.getLogger(__name__)
PoliciesType = List[Union[HTTPPolicy, SansIOHTTPPolicy]]


class _SansIOHTTPPolicyRunner(HTTPPolicy, Generic[HTTPRequestType, HTTPResponseType]):
    """Sync implementation of the SansIO policy.

    Modifies the request and sends to the next policy in the chain.

    :param policy: A SansIO policy.
    :type policy: ~azure.core.pipeline.policies.SansIOHTTPPolicy
    """

    def __init__(self, policy):
        # type: (SansIOHTTPPolicy) -> None
        super(_SansIOHTTPPolicyRunner, self).__init__()
        self._policy = policy

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Modifies the request and sends to the next policy in the chain.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        self._policy.on_request(request)
        try:
            response = self.next.send(request)
        except Exception: #pylint: disable=broad-except
            if not self._policy.on_exception(request):
                raise
        else:
            self._policy.on_response(request, response)
        return response


class _TransportRunner(HTTPPolicy):
    """Transport runner.

    Uses specified HTTP transport type to send request and returns response.

    :param sender: The Http Transport type.
    """
    def __init__(self, sender):
        # type: (HttpTransportType) -> None
        super(_TransportRunner, self).__init__()
        self._sender = sender

    def send(self, request):
        """HTTP transport send method.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        return PipelineResponse(
            request.http_request,
            self._sender.send(request.http_request, **request.context.options),
            context=request.context
        )


class Pipeline(AbstractContextManager, Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender. The transport is the last node in the pipeline.

    :param transport: The Http Transport type
    :param list policies: List of configured policies.
    """
    def __init__(self, transport, policies=None):
        # type: (HttpTransportType, PoliciesType) -> None
        self._impl_policies = []  # type: List[HTTPPolicy]
        self._transport = transport  # type: ignore

        for policy in (policies or []):
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOHTTPPolicyRunner(policy))
            elif policy:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies)-1):
            self._impl_policies[index].next = self._impl_policies[index+1]
        if self._impl_policies:
            self._impl_policies[-1].next = _TransportRunner(self._transport)

    def __enter__(self):
        # type: () -> Pipeline
        self._transport.__enter__() # type: ignore
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self._transport.__exit__(*exc_details)

    def run(self, request, **kwargs):
        # type: (HTTPRequestType, Any) -> PipelineResponse
        """Runs the HTTP Request through the chained policies.

        :param request: The HTTP request object.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: The PipelineResponse object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(request, context) # type: PipelineRequest
        first_node = self._impl_policies[0] if self._impl_policies else _TransportRunner(self._transport)
        return first_node.send(pipeline_request)  # type: ignore
