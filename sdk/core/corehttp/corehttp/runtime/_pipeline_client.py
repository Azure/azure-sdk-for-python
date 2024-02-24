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
from collections.abc import Iterable
from typing import TypeVar, Generic, Optional, Any

from .pipeline import Pipeline
from ._base import PipelineClientBase
from ..transport import HttpTransport
from .policies import (
    ContentDecodePolicy,
    RetryPolicy,
    HeadersPolicy,
    UserAgentPolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
)

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)


class PipelineClient(PipelineClientBase, Generic[HTTPRequestType, HTTPResponseType]):
    """Service client core methods.

    Builds a Pipeline client.

    :param str endpoint: URL for the request.
    :keyword Pipeline pipeline: If omitted, a Pipeline object is created.
    :keyword list[HTTPPolicy] policies: If omitted, a set of standard policies is used.
    :keyword per_call_policies: If specified, the policies will be added into the policy list before RetryPolicy
    :paramtype per_call_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]]
    :keyword per_retry_policies: If specified, the policies will be added into the policy list after RetryPolicy
    :paramtype per_retry_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]]
    :keyword HttpTransport transport: If omitted, RequestsTransport is used for synchronous transport.

    :ivar pipeline: The Pipeline object associated with the client.
    :vartype pipeline: ~corehttp.runtime.pipeline.Pipeline or None

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_pipeline_client.py
            :start-after: [START build_pipeline_client]
            :end-before: [END build_pipeline_client]
            :language: python
            :dedent: 4
            :caption: Builds the pipeline client.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        pipeline: Optional[Pipeline[HTTPRequestType, HTTPResponseType]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(endpoint)
        self.pipeline = pipeline or self._build_pipeline(**kwargs)

    def __enter__(self) -> PipelineClient[HTTPRequestType, HTTPResponseType]:
        self.pipeline.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self.pipeline.__exit__(*exc_details)

    def close(self) -> None:
        self.__exit__()

    def _build_pipeline(
        self,
        *,
        transport: Optional[HttpTransport[HTTPRequestType, HTTPResponseType]] = None,
        policies=None,
        per_call_policies=None,
        per_retry_policies=None,
        **kwargs,
    ) -> Pipeline[HTTPRequestType, HTTPResponseType]:
        per_call_policies = per_call_policies or []
        per_retry_policies = per_retry_policies or []

        if policies is None:
            policies = [
                kwargs.get("headers_policy") or HeadersPolicy(**kwargs),
                kwargs.get("user_agent_policy") or UserAgentPolicy(**kwargs),
                kwargs.get("proxy_policy") or ProxyPolicy(**kwargs),
                ContentDecodePolicy(**kwargs),
                kwargs.get("retry_policy") or RetryPolicy(**kwargs),
                kwargs.get("authentication_policy"),
                kwargs.get("logging_policy") or NetworkTraceLoggingPolicy(**kwargs),
            ]
        if isinstance(per_call_policies, Iterable):
            per_call_policies_list = list(per_call_policies)
        else:
            per_call_policies_list = [per_call_policies]
        per_call_policies_list.extend(policies)
        policies = per_call_policies_list

        if isinstance(per_retry_policies, Iterable):
            per_retry_policies_list = list(per_retry_policies)
        else:
            per_retry_policies_list = [per_retry_policies]
        if len(per_retry_policies_list) > 0:
            index_of_retry = -1
            for index, policy in enumerate(policies):
                if isinstance(policy, RetryPolicy):
                    index_of_retry = index
            if index_of_retry == -1:
                raise ValueError(
                    "Failed to add per_retry_policies; no RetryPolicy found in the supplied list of policies. "
                )
            policies_1 = policies[: index_of_retry + 1]
            policies_2 = policies[index_of_retry + 1 :]
            policies_1.extend(per_retry_policies_list)
            policies_1.extend(policies_2)
            policies = policies_1

        if transport is None:
            # Use private import for better typing, mypy and pyright don't like PEP562
            from ..transport.requests import RequestsTransport

            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies)

    def send_request(self, request: HTTPRequestType, *, stream: bool = False, **kwargs: Any) -> HTTPResponseType:
        """Method that runs the network request through the client's chained policies.

        >>> from corehttp.rest import HttpRequest
        >>> request = HttpRequest('GET', 'http://www.example.com')
        <HttpRequest [GET], url: 'http://www.example.com'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        :param request: The network request you want to make. Required.
        :type request: ~corehttp.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~corehttp.rest.HttpResponse
        """
        pipeline_response = self.pipeline.run(request, stream=stream, **kwargs)
        return pipeline_response.http_response
