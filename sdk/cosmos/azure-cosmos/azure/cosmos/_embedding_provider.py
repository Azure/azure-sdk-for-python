# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from typing import Any, Protocol, Sequence, runtime_checkable

from ._embedding_result import EmbeddingResult


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for classes that generate text embeddings for Azure Cosmos DB queries.

    Implementations are invoked by the SDK to embed literal text in queries
    that use ``GenerateEmbeddings(...)``. A provider may be attached at the
    client level or overridden at the container level. Implementations must be
    safe to call concurrently.
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
