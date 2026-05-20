# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from typing import Any, Protocol, Sequence, runtime_checkable

from ._embedding_result import EmbeddingResult


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for classes that generate text embeddings for Azure Cosmos DB queries.

    Implementations are invoked by the SDK to embed literal text in queries
    that use ``GenerateEmbeddings(...)``. A provider may be attached at the
    client level or overridden at the container level.

    **Lifecycle.** The provider instance is owned by the caller. The SDK does
    not construct, configure, or dispose of the provider; callers are
    responsible for any underlying clients, credentials, or network resources
    held by the implementation, and for releasing them when the provider is no
    longer needed.

    **Error semantics.** Exceptions raised by ``generate_embeddings`` are
    surfaced to the caller of the originating query. The SDK does not retry
    failed embedding calls and does not translate provider-specific exception
    types. Implementations should raise meaningful errors (for example,
    authentication, throttling, or transport failures) so that callers can
    handle them appropriately.

    **Cancellation.** Implementations should honor caller-supplied timeouts and
    cooperate with cancellation of the calling thread or surrounding
    operation. Long-running embedding calls should not block indefinitely.

    **Idempotency and concurrency.** The SDK may invoke
    ``generate_embeddings`` multiple times for the same inputs (for example,
    during query retries or across concurrent partitions). Implementations
    must therefore be safe to call concurrently from multiple threads and may
    cache results internally if desired.
    """

    def generate_embeddings(
        self,
        texts: Sequence[str],
        *,
        endpoint: str,
        deployment_name: str,
        dimensions: int,
        **kwargs: Any,
    ) -> EmbeddingResult:
        """Generate one embedding vector per input string.

        :param texts: The input strings to embed. The returned vectors must be
            in the same order as the inputs.
        :type texts: Sequence[str]
        :keyword str endpoint: The embedding service endpoint.
        :keyword str deployment_name: The model deployment name.
        :keyword int dimensions: The expected vector dimensionality.
        :returns: An :class:`EmbeddingResult` containing the generated vectors.
        :rtype: ~azure.cosmos.EmbeddingResult
        """
        ...
