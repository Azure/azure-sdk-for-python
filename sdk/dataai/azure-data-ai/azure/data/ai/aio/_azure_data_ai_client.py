# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Asynchronous Azure Data AI client using Azure Core."""

from typing import Any, Union

from azure.core import AsyncPipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import policies
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async

from .._shared import API_VERSION, DEFAULT_SCOPE, SUBSCRIPTION_KEY_HEADER, create_configuration
from ._reranker import _AsyncSemanticReranker


class AzureDataAIClient:
    """Call Azure Data AI asynchronously.

    :param endpoint: The Azure Data AI endpoint.
    :type endpoint: str
    :param credential: An Azure Data AI key, as a string or AzureKeyCredential,
        or an asynchronous Microsoft Entra token credential. Keys use the
        ``Ocp-Apim-Subscription-Key`` header. Use AzureKeyCredential to update a key
        without recreating the client.
    :type credential: str or ~azure.core.credentials.AzureKeyCredential or
        ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: Service API version. Defaults to ``2026-09-01-preview``.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[str, AzureKeyCredential, AsyncTokenCredential],
        *,
        api_version: str = API_VERSION,
        **kwargs: Any,
    ) -> None:
        if not endpoint:
            raise ValueError("Parameter 'endpoint' must not be empty.")
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        if isinstance(credential, str):
            credential = AzureKeyCredential(credential)
        auth_policy: Union[policies.AzureKeyCredentialPolicy, policies.AsyncBearerTokenCredentialPolicy]
        if isinstance(credential, AzureKeyCredential):
            auth_policy = policies.AzureKeyCredentialPolicy(credential, SUBSCRIPTION_KEY_HEADER, **kwargs)
        elif hasattr(credential, "get_token"):
            scopes = kwargs.pop("credential_scopes", [DEFAULT_SCOPE])
            auth_policy = policies.AsyncBearerTokenCredentialPolicy(credential, *scopes, **kwargs)
        else:
            raise TypeError(
                "Unsupported credential. Use a key string, AzureKeyCredential, or an async token credential."
            )
        self._client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse] = AsyncPipelineClient(
            base_url=endpoint,
            config=create_configuration(auth_policy, asynchronous=True, **kwargs),
            **kwargs,
        )
        self._reranker = _AsyncSemanticReranker(endpoint, self._client, api_version=api_version)

    @distributed_trace_async
    async def semantic_rerank(self, request: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Rank documents by their relevance to a query.

        :param request: Request dictionary with a nonempty ``query`` string and a nonempty
            ``documents`` list of strings. Optional request keys are:

            * ``topK`` (int): Maximum number of ranked documents to return.
              Must be between 1 and 2147483647.
            * ``returnDocuments`` (bool): Whether to include document text in the response.
            * ``returnSentenceScore`` (bool): Whether to include sentence-level scores.
            * ``batchSize`` (int): Number of documents processed per batch.
              Must be between 1 and 2147483647.
            * ``sort`` (bool): Whether to sort results by relevance score.
            * ``documentType`` (str): Document format, such as ``"text"`` or ``"json"``.
              JSON documents must be JSON-encoded strings.
            * ``targetPaths`` (str): JSON paths containing the text to rank when
              ``documentType`` is ``"json"``.
            * ``model`` (str): Name of a reranking model supported by the endpoint.
              Omit it to use the service's default model.

            These options belong inside ``request``, using the service's JSON casing,
            not in ``kwargs``. The dictionary is sent unchanged; the service validates
            its contents and determines defaults for omitted options.
        :type request: dict[str, Any]
        :return: The response dictionary. Optional ``scores`` entries contain ``index``,
            ``score``, and, when requested, ``document`` and ``sentenceScores``.
            Sentence entries contain a nonnegative, zero-based ``index`` (not capped at 2)
            and a ``score`` from 0 to 1 inclusive. The response is returned unchanged.
            Optional ``meta`` contains token usage, latency, ``modelName``, and ``modelVersion``.
        :rtype: dict[str, Any]
        :raises ~azure.core.exceptions.HttpResponseError: If the service rejects the request.
        """
        return await self._reranker.rerank(request, **kwargs)

    async def close(self) -> None:
        """Close the underlying Azure Core client."""
        await self._client.close()

    async def __aenter__(self) -> "AzureDataAIClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)
