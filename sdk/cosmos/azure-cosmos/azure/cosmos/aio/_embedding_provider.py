# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

from typing import Any, Protocol, Sequence, runtime_checkable

from .._embedding_result import EmbeddingResult


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Asynchronous Protocol for classes that generate text embeddings for Azure Cosmos DB queries.

    Asynchronous counterpart of :class:`azure.cosmos.EmbeddingProvider` for use
    with :class:`azure.cosmos.aio.CosmosClient`.
    """

    async def generate_embeddings(
        self,
        texts: Sequence[str],
        *,
        endpoint: str,
        deployment_name: str,
        dimensions: int,
        **kwargs: Any,
    ) -> EmbeddingResult:
        """Asynchronously generate one embedding vector per input string.

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
