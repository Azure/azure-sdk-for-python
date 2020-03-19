# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Adapter to substitute an azure-core pipeline for Requests in MSAL application token acquisition methods."""

import json

from azure.core.configuration import Configuration
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RetryPolicy,
    UserAgentPolicy,
)
from azure.core.pipeline.transport import HttpRequest, RequestsTransport

from .user_agent import USER_AGENT

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Dict, Mapping, Optional
    from azure.core.pipeline import PipelineResponse


class MsalTransportResponse:
    """Wraps an azure-core PipelineResponse with the shape of requests.Response"""

    def __init__(self, pipeline_response):
        # type: (PipelineResponse) -> None
        self._response = pipeline_response.http_response
        self.status_code = self._response.status_code
        self.text = self._response.text()

    def json(self, **kwargs):
        # type: (Any) -> Mapping[str, Any]
        return json.loads(self.text, **kwargs)

    def raise_for_status(self):
        # type: () -> None
        if self.status_code >= 400:
            raise ClientAuthenticationError("authentication failed", self._response)


class MsalTransportAdapter(object):
    """Wraps an azure-core pipeline with the shape of ``requests.Session``.

    Used as a context manager, patches msal.authority to intercept calls to requests.
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(MsalTransportAdapter, self).__init__()
        self._patch = mock.patch("msal.authority.requests", self)
        self._pipeline = self._build_pipeline(**kwargs)

    def __enter__(self):
        self._patch.__enter__()
        return self

    def __exit__(self, *args):
        self._patch.__exit__(*args)

    @staticmethod
    def _create_config(**kwargs):
        # type: (Any) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
        return config

    def _build_pipeline(self, config=None, policies=None, transport=None, **kwargs):
        config = config or self._create_config(**kwargs)
        policies = policies or [
            ContentDecodePolicy(),
            config.user_agent_policy,
            config.proxy_policy,
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        if not transport:
            transport = RequestsTransport(**kwargs)
        return Pipeline(transport=transport, policies=policies)

    def get(self, url, headers=None, params=None, timeout=None, verify=None, **kwargs):
        # type: (str, Optional[Mapping[str, str]], Optional[Dict[str, str]], float, bool, Any) -> MsalTransportResponse
        request = HttpRequest("GET", url, headers=headers)
        if params:
            request.format_parameters(params)
        response = self._pipeline.run(
            request, stream=False, connection_timeout=timeout, connection_verify=verify, **kwargs
        )
        return MsalTransportResponse(response)

    def post(
        self,
        url,  # type: str
        data=None,  # type: Optional[Mapping[str, str]]
        headers=None,  # type: Optional[Mapping[str, str]]
        params=None,  # type: Optional[Dict[str, str]]
        timeout=None,  # type: float
        verify=None,  # type: bool
        **kwargs  # type: Any
    ):
        # type: (...) -> MsalTransportResponse
        request = HttpRequest("POST", url, headers=headers)
        if params:
            request.format_parameters(params)
        if data:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            request.set_formdata_body(data)
        response = self._pipeline.run(
            request, stream=False, connection_timeout=timeout, connection_verify=verify, **kwargs
        )
        return MsalTransportResponse(response)
