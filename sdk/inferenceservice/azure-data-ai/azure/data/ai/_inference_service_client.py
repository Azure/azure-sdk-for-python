# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Synchronous Azure Inference Service client using Azure Core."""

from typing import Any, Union

from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace

from ._reranker import _SemanticReranker
from ._shared import API_VERSION, DEFAULT_SCOPE, SUBSCRIPTION_KEY_HEADER, create_configuration


class InferenceServiceClient:
    """Call Azure Inference Service.

    :param endpoint: The Azure Inference Service endpoint.
    :type endpoint: str
    :param credential: An Azure Inference Service key, as a string or AzureKeyCredential,
        or a Microsoft Entra token credential. Keys use the ``Ocp-Apim-Subscription-Key``
        header. Use AzureKeyCredential to update a key without recreating the client.
    :type credential: str or ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword api_version: Service API version. Defaults to ``2026-09-01-preview``.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[str, AzureKeyCredential, TokenCredential],
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
        auth_policy: Union[policies.AzureKeyCredentialPolicy, policies.BearerTokenCredentialPolicy]
        if isinstance(credential, AzureKeyCredential):
            auth_policy = policies.AzureKeyCredentialPolicy(credential, SUBSCRIPTION_KEY_HEADER, **kwargs)
        elif hasattr(credential, "get_token"):
            scopes = kwargs.pop("credential_scopes", [DEFAULT_SCOPE])
            auth_policy = policies.BearerTokenCredentialPolicy(credential, *scopes, **kwargs)
        else:
            raise TypeError("Unsupported credential. Use a key string, AzureKeyCredential, or a token credential.")
        self._client: PipelineClient[HttpRequest, HttpResponse] = PipelineClient(
            base_url=endpoint,
            config=create_configuration(auth_policy, **kwargs),
            **kwargs,
        )
        self._reranker = _SemanticReranker(endpoint, self._client, api_version=api_version)

    @distributed_trace
    def semantic_rerank(self, request: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Rank documents by their relevance to a query.

        :param request: Request dictionary with a nonempty ``query`` string and a nonempty
            ``documents`` list of strings. Optional request keys are:

            * ``model`` (str): Name of a reranking model supported by the endpoint.
              Omit it to use the service's default model.
            * ``topK`` (int): Maximum number of ranked documents to return.
              Must be between 1 and 2147483647.
            * ``batchSize`` (int): Number of documents processed per batch.
              Must be between 1 and 2147483647.
            * ``sort`` (bool): Whether to sort results by relevance score.
            * ``returnDocuments`` (bool): Whether to include document text in the response.
            * ``returnSentenceScore`` (bool): Whether to include sentence-level scores.
            * ``documentType`` (str): Document format, such as ``"text"`` or ``"json"``.
              JSON documents must be JSON-encoded strings.
            * ``targetPaths`` (str): JSON paths containing the text to rank when
              ``documentType`` is ``"json"``.

            These options belong inside ``request``, using the service's JSON casing,
            not in ``kwargs``. The dictionary is sent unchanged; the service validates
            its contents and determines defaults for omitted options.
        :type request: dict[str, Any]
        :return: The response dictionary. Optional ``scores`` entries contain ``index``,
            ``score``, and, when requested, ``document`` and ``sentenceScores``.
            Optional ``meta`` contains token usage, latency, ``modelName``, and ``modelVersion``.
        :rtype: dict[str, Any]
        :raises ~azure.core.exceptions.HttpResponseError: If the service rejects the request.
        """
        return self._reranker.rerank(request, **kwargs)

    def close(self) -> None:
        """Close the underlying Azure Core client."""
        self._client.close()

    def __enter__(self) -> "InferenceServiceClient":
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)
