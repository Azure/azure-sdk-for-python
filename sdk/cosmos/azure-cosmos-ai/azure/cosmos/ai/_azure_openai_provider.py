# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

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

"""Synchronous Azure OpenAI implementation of the EmbeddingProvider Protocol."""

from typing import Any, Dict, Optional, Sequence, Union

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.cosmos import EmbeddingResult
from azure.identity import get_bearer_token_provider
from openai import AzureOpenAI

_AZURE_OPENAI_API_VERSION = "2024-10-21"
_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


class AzureOpenAIEmbeddingProvider:
    """Default Azure OpenAI implementation of the
    :class:`azure.cosmos.EmbeddingProvider` Protocol.

    The provider only stores the credential. Endpoint, deployment name, and
    dimensions are read from the container's ``vectorEmbeddingPolicy`` and
    forwarded to :meth:`generate_embeddings` by the Cosmos SDK at query time.

    :param credential: One of:

        * ``str`` – Azure OpenAI API key.
        * :class:`~azure.core.credentials.AzureKeyCredential` – Azure OpenAI API key.
        * :class:`~azure.core.credentials.TokenCredential` – Entra (RBAC). Pass the
          same credential you use with :class:`~azure.cosmos.CosmosClient` to share
          one identity across both services.
    :type credential: str or
        ~azure.core.credentials.AzureKeyCredential or
        ~azure.core.credentials.TokenCredential
    """

    def __init__(
        self,
        credential: Union[str, AzureKeyCredential, TokenCredential],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        if not isinstance(credential, (str, AzureKeyCredential)) and not _is_token_credential(credential):
            raise TypeError(
                "credential must be a str, AzureKeyCredential, or TokenCredential; "
                f"got {type(credential).__name__}"
            )
        self._credential = credential
        self._api_version = _AZURE_OPENAI_API_VERSION
        self._clients: Dict[str, AzureOpenAI] = {}

    def generate_embeddings(
        self,
        texts: Sequence[str],
        *,
        endpoint: str,
        deployment_name: str,
        dimensions: int,
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> EmbeddingResult:
        """Generate embeddings for ``texts`` using Azure OpenAI.

        :param texts: Input strings.
        :type texts: ~typing.Sequence[str]
        :keyword str endpoint: Azure OpenAI endpoint
            (from ``vectorEmbeddingPolicy.embeddingSource.endpoint``).
        :keyword str deployment_name: Azure OpenAI deployment name
            (from ``vectorEmbeddingPolicy.embeddingSource.deploymentName``).
        :keyword int dimensions: Embedding dimensions
            (from ``vectorEmbeddingPolicy.dimensions``).
        :returns: Vectors in the same order as ``texts``, plus token usage.
        :rtype: ~azure.cosmos.EmbeddingResult
        """
        if not texts:
            return EmbeddingResult(vectors=[], total_tokens=0)

        client = self._get_or_create_client(endpoint)
        response = client.embeddings.create(
            input=list(texts),
            model=deployment_name,
            dimensions=dimensions,
        )
        total_tokens: Optional[int] = response.usage.total_tokens if response.usage else None
        return EmbeddingResult(
            vectors=[item.embedding for item in response.data],
            total_tokens=total_tokens,
        )

    def close(self) -> None:
        """Close every cached underlying Azure OpenAI client and clear the cache."""
        for client in self._clients.values():
            try:
                client.close()
            except Exception:  # pylint: disable=broad-except
                pass
        self._clients.clear()

    def __enter__(self) -> "AzureOpenAIEmbeddingProvider":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _get_or_create_client(self, endpoint: str) -> AzureOpenAI:
        key = endpoint.rstrip("/")
        client = self._clients.get(key)
        if client is None:
            client = self._build_client(key)
            self._clients[key] = client
        return client

    def _build_client(self, endpoint: str) -> AzureOpenAI:
        if isinstance(self._credential, str):
            return AzureOpenAI(
                azure_endpoint=endpoint,
                api_version=self._api_version,
                api_key=self._credential,
            )
        if isinstance(self._credential, AzureKeyCredential):
            return AzureOpenAI(
                azure_endpoint=endpoint,
                api_version=self._api_version,
                api_key=self._credential.key,
            )
        token_provider = get_bearer_token_provider(self._credential, _COGNITIVE_SERVICES_SCOPE)
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_version=self._api_version,
            azure_ad_token_provider=token_provider,
        )


def _is_token_credential(obj: Any) -> bool:
    """Duck-type check for a sync TokenCredential.

    Avoids ``isinstance(obj, TokenCredential)`` because ``TokenCredential`` is a
    ``Protocol`` in some azure-core versions and not always runtime_checkable.
    """
    return callable(getattr(obj, "get_token", None))
