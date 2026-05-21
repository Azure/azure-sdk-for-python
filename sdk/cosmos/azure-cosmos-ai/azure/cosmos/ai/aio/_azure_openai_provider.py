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

"""Asynchronous Azure OpenAI implementation of the EmbeddingProvider Protocol."""

import asyncio
import inspect
import time
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.cosmos import EmbeddingResult
from azure.identity.aio import get_bearer_token_provider
from openai import AsyncAzureOpenAI

_AZURE_OPENAI_API_VERSION = "2024-10-21"
_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


class AzureOpenAIEmbeddingProvider:
    """Async default Azure OpenAI implementation of the
    :class:`azure.cosmos.aio.EmbeddingProvider` Protocol.

    The provider only stores the credential. Endpoint, deployment name, and
    dimensions are read from the container's ``vectorEmbeddingPolicy`` and
    forwarded to :meth:`generate_embeddings` by the Cosmos SDK at query time.

    :param credential: One of:

        * ``str`` – Azure OpenAI API key.
        * :class:`~azure.core.credentials.AzureKeyCredential` – Azure OpenAI API key.
        * :class:`~azure.core.credentials_async.AsyncTokenCredential` – Entra (RBAC).
          Pass the same credential you use with
          :class:`~azure.cosmos.aio.CosmosClient` to share one identity across both
          services.
    :type credential: str or
        ~azure.core.credentials.AzureKeyCredential or
        ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: Azure OpenAI REST API version. Defaults to
        ``"2024-10-21"`` (the GA version when this package shipped). Override to
        access newer model features without waiting for a new release of this
        package.
    :keyword openai_client_kwargs: Additional keyword arguments forwarded
        verbatim to :class:`openai.AsyncAzureOpenAI` (e.g. ``timeout``,
        ``max_retries``, ``http_client``, ``default_headers``, ``user``). Keys
        that this provider controls (``azure_endpoint``, ``api_version``,
        ``api_key``, ``azure_ad_token_provider``) are not overridable through
        this mapping.
    :paramtype openai_client_kwargs: ~typing.Mapping[str, ~typing.Any] or None
    """

    def __init__(
        self,
        credential: Union[str, AzureKeyCredential, AsyncTokenCredential],
        *,
        api_version: str = _AZURE_OPENAI_API_VERSION,
        openai_client_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if isinstance(credential, (str, AzureKeyCredential)):
            pass
        elif _is_async_token_credential(credential):
            pass
        elif _is_sync_token_credential(credential):
            raise TypeError(
                "Asynchronous AzureOpenAIEmbeddingProvider received a sync "
                f"credential ({type(credential).__name__}). Either use "
                "azure.cosmos.ai.AzureOpenAIEmbeddingProvider instead, or "
                "pass an asynchronous TokenCredential such as "
                "azure.identity.aio.DefaultAzureCredential."
            )
        else:
            raise TypeError(
                "credential must be a str, AzureKeyCredential, or asynchronous "
                f"TokenCredential; got {type(credential).__name__}"
            )

        self._credential = credential
        self._api_version = api_version
        self._openai_client_kwargs: Dict[str, Any] = dict(openai_client_kwargs or {})
        self._clients: Dict[str, AsyncAzureOpenAI] = {}
        # Lazily created on first use so we don't require a running event loop at __init__.
        self._clients_lock: Optional[asyncio.Lock] = None

    async def generate_embeddings(
        self,
        texts: Sequence[str],
        *,
        endpoint: str,
        deployment_name: str,
        dimensions: int,
        **kwargs: Any,
    ) -> EmbeddingResult:
        """Generate embeddings for ``texts`` using Azure OpenAI.

        Safe to call concurrently from multiple coroutines.

        :param texts: Input strings.
        :type texts: ~typing.Sequence[str]
        :keyword str endpoint: Azure OpenAI endpoint
            (from ``vectorEmbeddingPolicy.embeddingSource.endpoint``).
        :keyword str deployment_name: Azure OpenAI deployment name
            (from ``vectorEmbeddingPolicy.embeddingSource.deploymentName``).
        :keyword int dimensions: Embedding dimensions
            (from ``vectorEmbeddingPolicy.dimensions``).
        :keyword Any kwargs: Reserved for forward compatibility with future
            Cosmos SDK additions. Currently, no per-call kwargs are forwarded to
            the underlying ``openai`` call; use ``openai_client_kwargs`` on the
            constructor (e.g. ``timeout``, ``max_retries``) to configure the
            underlying client.
        :returns: Vectors in the same order as ``texts``, plus token usage and
            measured latency.
        :rtype: ~azure.cosmos.EmbeddingResult
        """
        if not texts:
            return EmbeddingResult(vectors=[], total_tokens=0, latency=None)

        client = await self._get_or_create_client(endpoint)
        start = time.perf_counter()
        response = await client.embeddings.create(
            input=list(texts),
            model=deployment_name,
            dimensions=dimensions,
        )
        latency = time.perf_counter() - start
        total_tokens: Optional[int] = response.usage.total_tokens if response.usage else None
        return EmbeddingResult(
            vectors=[item.embedding for item in response.data],
            total_tokens=total_tokens,
            latency=latency,
        )

    async def close(self) -> None:
        """Close every cached underlying Azure OpenAI client and clear the cache.

        Snapshots the cached clients and clears the dict *before* awaiting each
        ``close()`` so that a concurrent :meth:`generate_embeddings` cannot
        observe a half-closed client.
        """
        clients = list(self._clients.values())
        self._clients.clear()
        for client in clients:
            try:
                await client.close()
            except Exception:  # pylint: disable=broad-except
                pass

    async def __aenter__(self) -> "AzureOpenAIEmbeddingProvider":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _ensure_lock(self) -> asyncio.Lock:
        if self._clients_lock is None:
            self._clients_lock = asyncio.Lock()
        return self._clients_lock

    async def _get_or_create_client(self, endpoint: str) -> AsyncAzureOpenAI:
        key = endpoint.rstrip("/")
        client = self._clients.get(key)
        if client is not None:
            return client
        async with self._ensure_lock():
            client = self._clients.get(key)
            if client is None:
                client = self._build_client(key)
                self._clients[key] = client
        return client

    def _build_client(self, endpoint: str) -> AsyncAzureOpenAI:
        # User-supplied kwargs go first so our explicit args win on collision.
        common: Dict[str, Any] = dict(self._openai_client_kwargs)
        common.update(azure_endpoint=endpoint, api_version=self._api_version)
        if isinstance(self._credential, str):
            return AsyncAzureOpenAI(api_key=self._credential, **common)
        if isinstance(self._credential, AzureKeyCredential):
            return AsyncAzureOpenAI(api_key=self._credential.key, **common)
        token_provider = get_bearer_token_provider(self._credential, _COGNITIVE_SERVICES_SCOPE)
        return AsyncAzureOpenAI(azure_ad_token_provider=token_provider, **common)


def _is_async_token_credential(obj: Any) -> bool:
    """Duck-type check for an *asynchronous* TokenCredential.

    Accepts any object that exposes a coroutine ``get_token`` method. Sync
    credentials are rejected so the mismatch is caught at ``__init__`` instead
    of failing deep inside ``openai`` with a confusing error.
    """
    get_token = getattr(obj, "get_token", None)
    return callable(get_token) and inspect.iscoroutinefunction(get_token)


def _is_sync_token_credential(obj: Any) -> bool:
    """Duck-type check for a *synchronous* TokenCredential.

    Used only to produce an actionable error message when a sync credential is
    accidentally passed to the async provider.
    """
    get_token = getattr(obj, "get_token", None)
    return callable(get_token) and not inspect.iscoroutinefunction(get_token)
