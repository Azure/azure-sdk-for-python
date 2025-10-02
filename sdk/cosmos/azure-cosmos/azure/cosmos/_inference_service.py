# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import urllib
from typing import Any, cast, Dict, List, Optional
from urllib3.util.retry import Retry

from azure.core import PipelineClient
from azure.core.exceptions import DecodeError
from azure.core.pipeline.policies import (ContentDecodePolicy, CustomHookPolicy, DistributedTracingPolicy,
                                          HeadersPolicy, HTTPPolicy, NetworkTraceLoggingPolicy, ProxyPolicy,
                                          UserAgentPolicy)
from azure.core.pipeline.transport import HttpRequest
from azure.core.utils import CaseInsensitiveDict

from . import exceptions
from ._constants import _Constants as Constants
from ._cosmos_http_logging_policy import CosmosHttpLoggingPolicy
from ._cosmos_responses import CosmosDict
from ._inference_auth_policy import InferenceServiceBearerTokenPolicy
from ._retry_utility import ConnectionRetryPolicy
from .http_constants import HttpHeaders


# cspell:ignore rerank reranker reranking
# pylint: disable=protected-access,line-too-long


class _InferenceService:
    """Internal client for inference service."""

    TOTAL_RETRIES = 3
    RETRY_BACKOFF_MAX = 120  # seconds
    RETRY_AFTER_STATUS_CODES = frozenset([429, 500])
    RETRY_BACKOFF_FACTOR = 0.8
    inference_service_default_scope = Constants.INFERENCE_SERVICE_DEFAULT_SCOPE
    semantic_reranking_inference_endpoint = os.environ.get(Constants.SEMANTIC_RERANKER_INFERENCE_ENDPOINT)

    def __init__(self, cosmos_client_connection):
        """Initialize inference service with credentials and endpoint information.

        :param cosmos_client_connection: Optional reference to cosmos client connection for accessing settings
        :type cosmos_client_connection: Optional[CosmosClientConnection]
        """
        self._client_connection = cosmos_client_connection
        self._aad_credentials = self._client_connection.aad_credentials
        self._token_scope = self.inference_service_default_scope

        self._inference_endpoint = f"{self.semantic_reranking_inference_endpoint}/inference/semanticReranking"
        self._inference_pipeline_client = self._create_inference_pipeline_client()

    def _create_inference_pipeline_client(self) -> PipelineClient:
        """Create a pipeline for inference requests.

        :returns: A PipelineClient configured for inference calls.
        :rtype: ~azure.core.PipelineClient
        """
        access_token = self._aad_credentials
        auth_policy = InferenceServiceBearerTokenPolicy(access_token, self._token_scope)

        connection_policy = self._client_connection.connection_policy
        retry_policy = None
        if isinstance(connection_policy.ConnectionRetryConfiguration, HTTPPolicy):
            retry_policy = ConnectionRetryPolicy(
                retry_total=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_total',
                                    self.TOTAL_RETRIES),
                retry_connect=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_connect', None),
                retry_read=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_read', None),
                retry_status=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_status', None),
                retry_backoff_max=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_backoff_max',
                                          self.RETRY_BACKOFF_MAX),
                retry_on_status_codes=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_on_status_codes',
                                              self.RETRY_AFTER_STATUS_CODES),
                retry_backoff_factor=getattr(connection_policy.ConnectionRetryConfiguration, 'retry_backoff_factor',
                                             self.RETRY_BACKOFF_FACTOR)
            )
        elif isinstance(connection_policy.ConnectionRetryConfiguration, int):
            retry_policy = ConnectionRetryPolicy(total=connection_policy.ConnectionRetryConfiguration)
        elif isinstance(connection_policy.ConnectionRetryConfiguration, Retry):
            # Convert a urllib3 retry policy to a Pipeline policy
            retry_policy = ConnectionRetryPolicy(
                retry_total=connection_policy.ConnectionRetryConfiguration.total,
                retry_connect=connection_policy.ConnectionRetryConfiguration.connect,
                retry_read=connection_policy.ConnectionRetryConfiguration.read,
                retry_status=connection_policy.ConnectionRetryConfiguration.status,
                retry_backoff_max=connection_policy.ConnectionRetryConfiguration.DEFAULT_BACKOFF_MAX,
                retry_on_status_codes=list(connection_policy.ConnectionRetryConfiguration.status_forcelist),
                retry_backoff_factor=connection_policy.ConnectionRetryConfiguration.backoff_factor
            )
        else:
            raise TypeError(
                "Unsupported retry policy. Must be an azure.cosmos.ConnectionRetryPolicy, int, or urllib3.Retry")

        proxies = {}
        if connection_policy.ProxyConfiguration and connection_policy.ProxyConfiguration.Host:
            host = connection_policy.ProxyConfiguration.Host
            url = urllib.parse.urlparse(host)
            proxy = host if url.port else host + ":" + str(connection_policy.ProxyConfiguration.Port)
            proxies.update({url.scheme: proxy})

        self._user_agent: str = self._client_connection._user_agent
        policies = [
            HeadersPolicy(),
            ProxyPolicy(proxies=proxies),
            UserAgentPolicy(base_user_agent=self._user_agent),
            ContentDecodePolicy(),
            retry_policy,
            auth_policy,
            CustomHookPolicy(),
            NetworkTraceLoggingPolicy(),
            DistributedTracingPolicy(),
            CosmosHttpLoggingPolicy(
                enable_diagnostics_logging=self._client_connection._enable_diagnostics_logging,
            ),
        ]

        return PipelineClient(
            base_url=self._inference_endpoint,
            policies=policies
        )

    def rerank(
        self,
        reranking_context: str,
        documents: List[str],
        semantic_reranking_options: Optional[Dict[str, Any]] = None,
    ) -> CosmosDict:
        """Rerank documents using the semantic reranking service.

        :param reranking_context: Query / context string used to score documents.
        :type reranking_context: str
        :param documents: List of document strings to rerank.
        :type documents: List[str]
        :param semantic_reranking_options: Optional dictionary of tuning parameters. Supported keys:
            * return_documents (bool): Include original document text in results. Default True.
            * top_k (int): Limit number of scored documents returned.
            * batch_size (int): Batch size for internal scoring operations.
            * sort (bool): If True (default) results are ordered by descending score.
        :type semantic_reranking_options: Optional[Dict[str, Any]]
        :returns: Reranking result payload.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: On HTTP or service error.
        """
        try:
            body = {
                "query": reranking_context,
                "documents": documents,
            }

            if semantic_reranking_options:
                if "return_documents" in semantic_reranking_options:
                    body["return_documents"] = semantic_reranking_options["return_documents"]
                if "top_k" in semantic_reranking_options:
                    body["top_k"] = semantic_reranking_options["top_k"]
                if "batch_size" in semantic_reranking_options:
                    body["batch_size"] = semantic_reranking_options["batch_size"]
                if "sort" in semantic_reranking_options:
                    body["sort"] = semantic_reranking_options["sort"]

            headers = {
                HttpHeaders.ContentType: "application/json"
            }

            request = HttpRequest(
                method="POST",
                url=self._inference_endpoint,
                headers=headers,
                data=json.dumps(body, separators=(",", ":"))
            )

            pipeline_response = self._inference_pipeline_client._pipeline.run(request)
            response = pipeline_response.http_response
            response_headers = cast(CaseInsensitiveDict, response.headers)

            data = response.body()
            if data:
                data = data.decode("utf-8")

            if response.status_code >= 400:
                raise exceptions.CosmosHttpResponseError(message=data, response=response)

            result = None
            if data:
                try:
                    result = json.loads(data)
                except Exception as e:
                    raise DecodeError(
                        message="Failed to decode JSON data: {}".format(e),
                        response=response,
                        error=e) from e

            return CosmosDict(result, response_headers=response_headers)

        except Exception as e:
            if isinstance(e, (exceptions.CosmosHttpResponseError, exceptions.CosmosResourceNotFoundError)):
                raise
            raise exceptions.CosmosHttpResponseError(
                message=f"Semantic reranking failed: {str(e)}",
                response=None
            ) from e
