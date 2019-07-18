# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Adapter to substitute an azure-core pipeline for Requests in MSAL application token acquisition methods."""

import json

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Mapping, Optional
    from azure.core.pipeline import PipelineResponse

from azure.core.configuration import Configuration
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy, RetryPolicy
from azure.core.pipeline.transport import HttpRequest, RequestsTransport


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
        raise ClientAuthenticationError("authentication failed", self._response)


class MsalTransportAdapter(object):
    """Wraps an azure-core pipeline with the shape of requests.Session"""

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(MsalTransportAdapter, self).__init__()
        self._pipeline = self._build_pipeline(**kwargs)

    @staticmethod
    def create_config(**kwargs):
        # type: (Any) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        return config

    def _build_pipeline(self, config=None, policies=None, transport=None, **kwargs):
        config = config or self.create_config(**kwargs)
        policies = policies or [ContentDecodePolicy(), config.retry_policy, config.logging_policy]
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

    def post(self, url, data=None, headers=None, params=None, timeout=None, verify=None, **kwargs):
        # type: (str, Optional[Mapping[str, str]], Optional[Mapping[str, str]], Optional[Dict[str, str]], float, bool, Any) -> MsalTransportResponse
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
